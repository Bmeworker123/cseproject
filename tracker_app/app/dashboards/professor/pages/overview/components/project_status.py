import tkinter as tk

from tracker_app.app.components import Component
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tracker_app.ui import Card, Label


class OverviewProjectStatusCard(Component):
    def __init__(self, page, parent):
        self.page = page
        super().__init__(parent)

    def render(self, parent):
        chart_card = Card(parent, bg="#fff7ed")
        chart_card.pack(fill="x", pady=14)
        Label(
            chart_card,
            text="Project Status Breakdown",
            size=13,
            bold=True,
            bg="#fff7ed",
            fg="#7c2d12",
        ).pack(anchor="w")
        Label(
            chart_card,
            text="Teams without a project, plus approved, pending, and rejected submissions.",
            size=10,
            bg="#fff7ed",
            fg="#9a3412",
        ).pack(anchor="w", pady=(4, 8))

        self.chart_host = tk.Frame(chart_card, bg="#fff7ed")
        self.chart_host.pack(fill="x")
        self.loading_label = Label(
            self.chart_host,
            text="Loading chart...",
            size=10,
            bg="#fff7ed",
            fg="#9a3412",
        )
        self.loading_label.pack(anchor="w", pady=(4, 0))

        self.run_in_background(
            lambda: self.project_status_breakdown(),
            on_success=lambda counts: self.render_project_status_chart(self.chart_host, counts),
            on_error=lambda _error: self.show_chart_error(),
        )

    def show_chart_error(self):
        self.loading_label.config(text="Failed to load chart data.")

    def project_status_breakdown(self):
        return self.calculate_status_breakdown(self.page)

    @staticmethod
    def calculate_status_breakdown(page):
        teacher_class_ids = {item["id"] for item in page.teacher_classes()}
        teams = []
        for class_record in page.teacher_classes():
            teams.extend(
                page.app.professor_repo.list_teams_for_class(class_record["id"])
            )

        projects = [
            project
            for project in page.app.professor_repo.list_projects()
            if not teacher_class_ids
            or project.get("class_id") in teacher_class_ids
            or project.get("class_id") is None
        ]
        projects_by_team = {
            project.get("team_id"): project
            for project in projects
            if project.get("team_id") is not None
        }

        counts = {
            "No Project": 0,
            "Not Approved": 0,
            "Approved": 0,
            "Rejected": 0,
        }

        for team in teams:
            project = projects_by_team.get(team["id"])
            if not project:
                counts["No Project"] += 1
                continue

            status = (
                (project.get("approval_status") or "Pending Approval").strip().lower()
            )
            if status == "approved":
                counts["Approved"] += 1
            elif status == "rejected":
                counts["Rejected"] += 1
            else:
                counts["Not Approved"] += 1

        return counts

    def render_project_status_chart(self, parent, counts):
        for widget in parent.winfo_children():
            widget.destroy()

        values = [
            counts["No Project"],
            counts["Not Approved"],
            counts["Approved"],
            counts["Rejected"],
        ]
        labels = ["No Project", "Not Approved", "Approved", "Rejected"]
        colors = ["#94a3b8", "#f59e0b", "#22c55e", "#ef4444"]

        if sum(values) == 0:
            Label(
                parent,
                text="No team data available yet.",
                size=10,
                bg="#fff7ed",
                fg="#9a3412",
            ).pack(anchor="w", pady=(4, 0))
            return

        figure = Figure(figsize=(6.4, 2.8), dpi=100, facecolor="#fff7ed")
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
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", pady=(4, 0))
