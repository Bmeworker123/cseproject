import tkinter as tk

from ..base import ProfessorPageBase
from .....ui import Button, Label, Card, StatCard


class ProfessorOverviewPage(ProfessorPageBase):
    def render(self, parent):
        students = self.app.professor_repo.list_students()
        projects = self.app.professor_repo.list_projects()
        classes = self.teacher_classes()

        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Quick view of student growth, class setup, and team structure.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        StatCard(stats, "Total Students", str(len(students)), "Enrolled in project tracker.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Active Projects", str(len(projects)), "Submitted for review.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Your Classes", str(len(classes)), "Created by you.").pack(side="left", fill="both", expand=True, padx=6)

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
