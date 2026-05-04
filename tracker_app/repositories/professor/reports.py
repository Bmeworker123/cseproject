from collections import Counter

from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


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
