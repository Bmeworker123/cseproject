from collections import Counter
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ExcelExporterEngine:
    @staticmethod
    def export(file_path, headers, rows):
        sheet_xml = ExcelExporterEngine._build_sheet_xml(headers, rows)
        with ZipFile(file_path, "w", ZIP_DEFLATED) as archive:
            archive.writestr(
                "[Content_Types].xml",
                """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
  <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
  <Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>
</Types>
                """.strip(),
            )
            archive.writestr(
                "_rels/.rels",
                """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>
                """.strip(),
            )
            archive.writestr(
                "xl/workbook.xml",
                """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"Report\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
</workbook>
                """.strip(),
            )
            archive.writestr(
                "xl/_rels/workbook.xml.rels",
                """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
  <Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>
</Relationships>
                """.strip(),
            )
            archive.writestr(
                "xl/styles.xml",
                """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <fonts count=\"1\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>
  <fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>
  <borders count=\"1\"><border/></borders>
  <cellStyleXfs count=\"1\"><xf/></cellStyleXfs>
  <cellXfs count=\"1\"><xf xfId=\"0\"/></cellXfs>
  <cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles>
</styleSheet>
                """.strip(),
            )
            archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    @staticmethod
    def _build_sheet_xml(headers, rows):
        all_rows = [headers] + rows
        xml_rows = []
        for row_index, row in enumerate(all_rows, start=1):
            cells = []
            for col_index, value in enumerate(row, start=1):
                ref = f"{ExcelExporterEngine._col_name(col_index)}{row_index}"
                cell_value = "" if value is None else str(value)
                if cell_value.isdigit():
                    cells.append(f"<c r=\"{ref}\"><v>{cell_value}</v></c>")
                else:
                    cells.append(
                        f"<c r=\"{ref}\" t=\"inlineStr\"><is><t>{escape(cell_value)}</t></is></c>"
                    )
            xml_rows.append(f"<row r=\"{row_index}\">{''.join(cells)}</row>")
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
            "<sheetData>"
            f"{''.join(xml_rows)}"
            "</sheetData>"
            "</worksheet>"
        )

    @staticmethod
    def _col_name(index):
        label = ""
        while index > 0:
            index, rem = divmod(index - 1, 26)
            label = chr(65 + rem) + label
        return label


class ProfessorReportRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def list_combined_workflow_rows(self, teacher_email):
        classes = self.db.list_classes_for_teacher(teacher_email)
        class_ids = {item["id"] for item in classes}
        class_name_by_id = {
            item["id"]: f"{item['name']} ({item['term']})" for item in classes
        }

        teams = self.db.list_teams_for_teacher(teacher_email)
        team_ids = {team["id"] for team in teams}
        team_name_by_id = {team["id"]: team["name"] for team in teams}

        projects = self.db.list_projects_for_teacher(teacher_email)
        project_by_team = {
            project.get("team_id"): project
            for project in projects
            if project.get("team_id") is not None
        }

        students = [
            user
            for user in self.db.list_users()
            if user.get("role") == "student"
            and (
                user.get("class_id") in class_ids
                or user.get("team_id") in team_ids
            )
        ]

        rows = []
        for student in students:
            team_id = student.get("team_id")
            project = project_by_team.get(team_id)
            rows.append(
                {
                    "student_name": student.get("name", ""),
                    "student_email": student.get("email", ""),
                    "student_number": student.get("student_id", ""),
                    "department": student.get("department", ""),
                    "class_name": class_name_by_id.get(student.get("class_id"), "Not Assigned"),
                    "team_name": team_name_by_id.get(team_id, "Not Assigned"),
                    "project_title": (project or {}).get("title", "No Project"),
                    "approval_status": (
                        (project or {}).get("approval_status")
                        or "No Project"
                    ),
                    "last_updated": (project or {}).get("last_updated", ""),
                }
            )

        rows.sort(key=lambda item: (item["class_name"], item["team_name"], item["student_name"]))
        return rows

    def project_status_counts(self, teacher_email):
        teams = self.db.list_teams_for_teacher(teacher_email)
        projects = self.db.list_projects_for_teacher(teacher_email)
        project_by_team = {
            project.get("team_id"): project
            for project in projects
            if project.get("team_id") is not None
        }

        counts = {
            "No Project": 0,
            "Pending Approval": 0,
            "Approved": 0,
            "Rejected": 0,
        }
        for team in teams:
            project = project_by_team.get(team["id"])
            if not project:
                counts["No Project"] += 1
                continue
            status = (project.get("approval_status") or "Pending Approval").strip().lower()
            if status == "approved":
                counts["Approved"] += 1
            elif status == "rejected":
                counts["Rejected"] += 1
            else:
                counts["Pending Approval"] += 1
        return counts

    def projects_by_class(self, teacher_email):
        classes = self.db.list_classes_for_teacher(teacher_email)
        projects = self.db.list_projects_for_teacher(teacher_email)
        counts = Counter(project.get("class_id") for project in projects)
        chart_rows = []
        for item in classes:
            label = f"{item['name']} ({item['term']})"
            chart_rows.append((label, counts.get(item["id"], 0)))
        return chart_rows

    def students_by_class(self, teacher_email):
        classes = self.db.list_classes_for_teacher(teacher_email)
        class_ids = {item["id"] for item in classes}
        students = [
            user
            for user in self.db.list_users()
            if user.get("role") == "student" and user.get("class_id") in class_ids
        ]
        counts = Counter(student.get("class_id") for student in students)
        chart_rows = []
        for item in classes:
            label = f"{item['name']} ({item['term']})"
            chart_rows.append((label, counts.get(item["id"], 0)))
        return chart_rows

    def team_sizes_by_class(self, teacher_email):
        classes = self.db.list_classes_for_teacher(teacher_email)
        class_ids = {item["id"] for item in classes}
        teams = [
            team
            for team in self.db.list_teams_for_teacher(teacher_email)
            if team.get("class_id") in class_ids
        ]
        students = [
            user
            for user in self.db.list_users()
            if user.get("role") == "student" and user.get("team_id") is not None
        ]
        team_sizes = Counter(student.get("team_id") for student in students)

        chart_rows = []
        for team in teams:
            class_record = next(
                (item for item in classes if item["id"] == team.get("class_id")),
                None,
            )
            class_name = (
                f"{class_record['name']} ({class_record['term']})"
                if class_record
                else "Unknown Class"
            )
            label = f"{class_name} / {team['name']}"
            chart_rows.append((label, team_sizes.get(team["id"], 0)))

        chart_rows.sort(key=lambda item: item[0])
        return chart_rows

    def team_project_coverage(self, teacher_email):
        teams = self.db.list_teams_for_teacher(teacher_email)
        projects = self.db.list_projects_for_teacher(teacher_email)
        team_ids_with_project = {
            project.get("team_id")
            for project in projects
            if project.get("team_id") is not None
        }
        with_project = sum(1 for team in teams if team["id"] in team_ids_with_project)
        without_project = sum(1 for team in teams if team["id"] not in team_ids_with_project)
        return {
            "With Project": with_project,
            "Without Project": without_project,
        }
