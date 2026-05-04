import csv
import tkinter as tk
from tkinter import filedialog
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tracker_app.ui import Button, Card, Label

from ..base import ProfessorPageBase


class ProfessorReportsPage(ProfessorPageBase):
    HEADERS = [
        "Student Name",
        "Student Email",
        "Student Number",
        "Department",
        "Class",
        "Team",
        "Project Title",
        "Approval Status",
        "Last Updated",
    ]

    def render(self, parent):
        canvas, scrollable = self._build_scrollable_area(parent)

        Label(
            scrollable,
            text="Reports",
            size=16,
            bold=True,
            bg="white",
            fg="#1f2933",
        ).pack(anchor="w")
        Label(
            scrollable,
            text="Export workflow data to CSV/XLSX and review graphical reports.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)

        self.message_label = Label(
            scrollable, text="", size=10, bg="white", fg="#1f7a45"
        )
        self.message_label.pack(anchor="w", pady=(2, 8))

        controls = tk.Frame(scrollable, bg="white")
        controls.pack(fill="x", pady=(0, 10))
        Button(controls, "Export CSV", self.export_csv, primary=True).pack(side="left")
        Button(controls, "Export Excel (.xlsx)", self.export_xlsx).pack(
            side="left", padx=(8, 0)
        )

        preview_card = Card(scrollable, bg="#f7f9fb")
        preview_card.pack(fill="x", pady=(0, 12))
        Label(
            preview_card,
            text="Combined Workflow Report Preview",
            size=12,
            bold=True,
            bg="#f7f9fb",
            fg="#102a43",
        ).pack(anchor="w")

        self.preview_list = tk.Listbox(
            preview_card,
            height=8,
            font=("Consolas", 9),
            bd=0,
            highlightthickness=1,
            highlightbackground="#d9e2ec",
        )
        self.preview_list.pack(fill="x", pady=(6, 0))

        self.rows = self.app.professor_repo.list_combined_workflow_rows(
            self.app.current_user["email"]
        )
        self._render_preview()

        chart_shell = tk.Frame(scrollable, bg="white")
        chart_shell.pack(fill="both", expand=True)

        status_counts = self.app.professor_repo.project_status_counts(
            self.app.current_user["email"]
        )
        self._render_pie_card(
            chart_shell,
            "Project Approval Status",
            "Team-level project status distribution.",
            status_counts,
            ["No Project", "Pending Approval", "Approved", "Rejected"],
            ["#94a3b8", "#f59e0b", "#22c55e", "#ef4444"],
        )

        self._render_bar_card(
            chart_shell,
            "Projects by Class",
            "How many team projects exist in each class.",
            self.app.professor_repo.projects_by_class(self.app.current_user["email"]),
            "#2f80ed",
        )
        self._render_bar_card(
            chart_shell,
            "Students by Class",
            "Student distribution across the teacher's classes.",
            self.app.professor_repo.students_by_class(self.app.current_user["email"]),
            "#00a3a3",
        )
        self._render_bar_card(
            chart_shell,
            "Team Size by Class/Team",
            "Student count per team.",
            self.app.professor_repo.team_sizes_by_class(self.app.current_user["email"]),
            "#8b5cf6",
        )

        coverage = self.app.professor_repo.team_project_coverage(
            self.app.current_user["email"]
        )
        self._render_pie_card(
            chart_shell,
            "Team Project Coverage",
            "Teams with and without submitted projects.",
            coverage,
            ["With Project", "Without Project"],
            ["#10b981", "#f97316"],
        )

        canvas.yview_moveto(0)

    def _build_scrollable_area(self, parent):
        container = tk.Frame(parent, bg="white")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scrollable = tk.Frame(canvas, bg="white")
        window = canvas.create_window((0, 0), window=scrollable, anchor="nw")

        def on_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(window, width=event.width)

        scrollable.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        self._bind_mousewheel(canvas)

        return canvas, scrollable

    def _bind_mousewheel(self, widget):
        def on_mousewheel(event):
            delta = event.delta
            if delta == 0 and hasattr(event, "num"):
                if event.num == 4:
                    widget.yview_scroll(-1, "units")
                    return
                if event.num == 5:
                    widget.yview_scroll(1, "units")
                    return
            widget.yview_scroll(int(-1 * (delta / 120)), "units")

        widget.bind("<MouseWheel>", on_mousewheel)
        widget.bind("<Button-4>", on_mousewheel)
        widget.bind("<Button-5>", on_mousewheel)

    def _render_preview(self):
        self.preview_list.delete(0, tk.END)
        self.preview_list.insert(
            tk.END,
            " | ".join(
                ["Student", "Class", "Team", "Project", "Status", "Updated"]
            ),
        )
        self.preview_list.insert(tk.END, "-" * 110)
        if not self.rows:
            self.preview_list.insert(tk.END, "No rows available for this teacher yet.")
            return

        for row in self.rows[:20]:
            self.preview_list.insert(
                tk.END,
                " | ".join(
                    [
                        row["student_name"] or "-",
                        row["class_name"] or "-",
                        row["team_name"] or "-",
                        row["project_title"] or "-",
                        row["approval_status"] or "-",
                        row["last_updated"] or "-",
                    ]
                ),
            )

    def _row_values(self):
        return [
            [
                row["student_name"],
                row["student_email"],
                row["student_number"],
                row["department"],
                row["class_name"],
                row["team_name"],
                row["project_title"],
                row["approval_status"],
                row["last_updated"],
            ]
            for row in self.rows
        ]

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Save CSV Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not file_path:
            return
        with open(file_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(self.HEADERS)
            writer.writerows(self._row_values())
        self.message_label.config(text=f"CSV exported: {file_path}", fg="#1f7a45")

    def export_xlsx(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Excel Report",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
        )
        if not file_path:
            return
        self._write_xlsx(file_path, self.HEADERS, self._row_values())
        self.message_label.config(text=f"Excel exported: {file_path}", fg="#1f7a45")

    def _render_bar_card(self, parent, title, subtitle, rows, color):
        card = Card(parent, bg="#f8fafc")
        card.pack(fill="x", pady=(0, 10))
        Label(card, text=title, size=12, bold=True, bg="#f8fafc", fg="#102a43").pack(
            anchor="w"
        )
        Label(card, text=subtitle, size=10, bg="#f8fafc", fg="#52606d").pack(
            anchor="w", pady=(3, 6)
        )

        if not rows:
            Label(
                card,
                text="No data available yet.",
                size=10,
                bg="#f8fafc",
                fg="#52606d",
            ).pack(anchor="w")
            return

        labels = [label for label, _ in rows]
        values = [value for _, value in rows]

        figure = Figure(figsize=(8.2, 2.8), dpi=100, facecolor="#f8fafc")
        axis = figure.add_subplot(111)
        bars = axis.bar(range(len(values)), values, color=color)
        axis.set_xticks(range(len(labels)))
        axis.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
        axis.set_ylabel("Count")
        axis.grid(axis="y", linestyle="--", alpha=0.25)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        for bar, value in zip(bars, values):
            axis.text(
                bar.get_x() + (bar.get_width() / 2),
                value + 0.05,
                str(value),
                ha="center",
                va="bottom",
                fontsize=8,
            )
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x")

    def _render_pie_card(self, parent, title, subtitle, values_by_label, labels, colors):
        card = Card(parent, bg="#fff7ed")
        card.pack(fill="x", pady=(0, 10))
        Label(card, text=title, size=12, bold=True, bg="#fff7ed", fg="#7c2d12").pack(
            anchor="w"
        )
        Label(card, text=subtitle, size=10, bg="#fff7ed", fg="#9a3412").pack(
            anchor="w", pady=(3, 6)
        )

        values = [int(values_by_label.get(label, 0)) for label in labels]
        if sum(values) == 0:
            Label(
                card,
                text="No data available yet.",
                size=10,
                bg="#fff7ed",
                fg="#9a3412",
            ).pack(anchor="w")
            return

        figure = Figure(figsize=(7.6, 2.8), dpi=100, facecolor="#fff7ed")
        axis = figure.add_subplot(111)
        wedges, _, autotexts = axis.pie(
            values,
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
            textprops={"fontsize": 9},
        )
        axis.axis("equal")
        axis.legend(
            wedges,
            [f"{label} ({value})" for label, value in zip(labels, values)],
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=9,
        )
        for text in autotexts:
            text.set_color("white")
            text.set_fontweight("bold")
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x")

    @staticmethod
    def _write_xlsx(file_path, headers, rows):
        sheet_xml = ProfessorReportsPage._build_sheet_xml(headers, rows)
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
                ref = f"{ProfessorReportsPage._col_name(col_index)}{row_index}"
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
