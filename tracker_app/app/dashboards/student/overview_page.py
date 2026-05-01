import tkinter as tk

from ....ui import Label, Card


class StudentOverviewPage:
    def __init__(self, app):
        self.app = app

    def render(self, parent):
        user = self.app.student_repo.refresh_user(self.app.current_user["id"])
        self.app.current_user = user
        project = self.app.student_repo.project_for(self.app.current_user)

        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Your student profile, class, team, and latest project summary.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)

        top = tk.Frame(parent, bg="white")
        top.pack(fill="x", pady=(10, 0))

        profile = Card(top, bg="#f7f9fb")
        profile.pack(side="left", fill="both", expand=True, padx=(0, 10))
        Label(profile, text="Student Profile", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        details = [
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Student ID: {user.get('student_id', 'N/A')}",
            f"Department: {user.get('department', 'N/A')}",
            f"Class: {self.app.student_repo.class_name(user.get('class_id')) or 'Not Assigned'}",
            f"Team: {self.app.student_repo.team_name(user.get('team_id')) or 'Not Assigned'}",
        ]
        for detail in details:
            Label(profile, text=detail, size=10, bg="#f7f9fb", fg="#334e68").pack(anchor="w", pady=2)

        summary = Card(top, bg="#eef8f1")
        summary.pack(side="left", fill="both", expand=True)
        Label(summary, text="Project Summary", size=13, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")

        if not project:
            Label(summary, text="No project yet. Open Project Form to create one.", size=10, bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=(6, 0))
        else:
            p_details = [
                f"Title: {project['title']}",
                f"Stage: {project.get('stage', 'N/A')}",
                f"Status: {project['status']}",
                f"Progress: {project['progress']}%",
            ]
            for line in p_details:
                Label(summary, text=line, size=10, bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=2)

        box = Card(parent, bg="#fff7ed")
        box.pack(fill="x", pady=(18, 0))
        Label(box, text="Notifications", size=13, bold=True, bg="#fff7ed", fg="#9a3412").pack(anchor="w")

        if not user.get("notifications"):
            Label(box, text="No notifications yet.", size=10, bg="#fff7ed", fg="#b45309").pack(anchor="w", pady=(6, 0))
        else:
            for notification in user["notifications"]:
                Label(box, text=notification, size=10, bg="#fff7ed", fg="#7c2d12", wraplength=760, justify="left").pack(anchor="w", pady=2)
