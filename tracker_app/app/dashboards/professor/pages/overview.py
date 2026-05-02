import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ..base import ProfessorPageBase
from .....ui import Button, Label, Card, StatCard


class ProfessorOverviewPage(ProfessorPageBase):
    def render(self, parent):
        students = self.app.professor_repo.list_students()
        projects = self.app.professor_repo.list_projects()
        classes = self.teacher_classes()
        status_counts = self.project_status_breakdown()

        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Quick view of student growth, class setup, and team structure.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        StatCard(stats, "Total Students", str(len(students)), "Enrolled in project tracker.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Active Projects", str(len(projects)), "Submitted for review.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Your Classes", str(len(classes)), "Created by you.").pack(side="left", fill="both", expand=True, padx=6)

        chart_card = Card(parent, bg="#fff7ed")
        chart_card.pack(fill="x", pady=14)
        Label(chart_card, text="Project Status Breakdown", size=13, bold=True, bg="#fff7ed", fg="#7c2d12").pack(anchor="w")
        Label(chart_card, text="Teams without a project, plus approved, pending, and rejected submissions.", size=10, bg="#fff7ed", fg="#9a3412").pack(anchor="w", pady=(4, 8))

        self.render_project_status_chart(chart_card, status_counts)

        recent_card = Card(parent, bg="#f7f9fb")
        recent_card.pack(fill="x", pady=14)
        Label(recent_card, text="New Students", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        new_students = sorted(students, key=lambda user: user.get("created_at", ""), reverse=True)[:5]
        if not new_students:
            Label(recent_card, text="No student accounts yet.", size=10, bg="#f7f9fb", fg="#52606d").pack(anchor="w", pady=(6, 0))
        else:
            for user in new_students:
                line = f"{user['name']} ({user['email']}) | Joined: {user.get('created_at', 'N/A')}"
                Label(recent_card, text=line, size=10, bg="#f7f9fb", fg="#334e68").pack(anchor="w", pady=2)

        actions = Card(parent, bg="#eef8f1")
        actions.pack(fill="x")
        Label(actions, text="Teacher Actions", size=13, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")
        Label(actions, text="Use Students to assign classes, Classes to create offerings, Teams to group students, and Projects to review submissions.", size=10, bg="#eef8f1", fg="#1f7a45", wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))

        row = tk.Frame(actions, bg="#eef8f1")
        row.pack(anchor="w")
        Button(row, "Open Classes", lambda: self.dashboard.set_page("classes"), primary=True).pack(side="left", padx=(0, 8))
        Button(row, "Open Teams", lambda: self.dashboard.set_page("teams")).pack(side="left", padx=(0, 8))
        Button(row, "Open Projects", lambda: self.dashboard.set_page("projects")).pack(side="left")

    def project_status_breakdown(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        teams = []
        for class_record in self.teacher_classes():
            teams.extend(self.app.professor_repo.list_teams_for_class(class_record["id"]))

        projects = [
            project
            for project in self.app.professor_repo.list_projects()
            if not teacher_class_ids or project.get("class_id") in teacher_class_ids or project.get("class_id") is None
        ]
        projects_by_team = {project.get("team_id"): project for project in projects if project.get("team_id") is not None}

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

            status = (project.get("approval_status") or "Pending Approval").strip().lower()
            if status == "approved":
                counts["Approved"] += 1
            elif status == "rejected":
                counts["Rejected"] += 1
            else:
                counts["Not Approved"] += 1

        return counts

    def render_project_status_chart(self, parent, counts):
        values = [counts["No Project"], counts["Not Approved"], counts["Approved"], counts["Rejected"]]
        labels = ["No Project", "Not Approved", "Approved", "Rejected"]
        colors = ["#94a3b8", "#f59e0b", "#22c55e", "#ef4444"]

        if sum(values) == 0:
            Label(parent, text="No team data available yet.", size=10, bg="#fff7ed", fg="#9a3412").pack(anchor="w", pady=(4, 0))
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
