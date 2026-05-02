import tkinter as tk

from ....ui import Card, Label
from .base import StudentPageBase
from .components import render_detail_lines, render_page_header, render_section_title


class StudentOverviewPage(StudentPageBase):
    def __init__(self, app):
        super().__init__(app)

    def render(self, parent):
        user = self.refresh_user()
        project = self.current_project()

        render_page_header(parent, "Overview", "Your student profile, class, team, and latest project summary.")

        top = tk.Frame(parent, bg="white")
        top.pack(fill="x", pady=(10, 0))

        profile = Card(top, bg="#f7f9fb")
        profile.pack(side="left", fill="both", expand=True, padx=(0, 10))
        render_section_title(profile, "Student Profile", bg="#f7f9fb", fg="#102a43")

        render_detail_lines(profile, [
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Student ID: {user.get('student_id', 'N/A')}",
            f"Department: {user.get('department', 'N/A')}",
            f"Class: {self.app.student_repo.class_name(user.get('class_id')) or 'Not Assigned'}",
            f"Team: {self.app.student_repo.team_name(user.get('team_id')) or 'Not Assigned'}",
        ], bg="#f7f9fb", fg="#334e68")

        summary = Card(top, bg="#eef8f1")
        summary.pack(side="left", fill="both", expand=True)
        render_section_title(summary, "Project Summary", bg="#eef8f1", fg="#14532d")

        if not project:
            Label(summary, text="No project yet. Open Project Form to create one.", size=10, bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=(6, 0))
        else:
            render_detail_lines(summary, [
                f"Title: {project['title']}",
                f"Approval Status: {project.get('approval_status', 'Pending Approval')}",
            ], bg="#eef8f1", fg="#1f7a45")

        teammates = self.app.student_repo.teammate_names(user)
        team_card = Card(parent, bg="#fff7ed")
        team_card.pack(fill="x", pady=(12, 0))
        render_section_title(team_card, "Teammates", bg="#fff7ed", fg="#7c2d12")

        if not teammates:
            Label(team_card, text="No teammates assigned yet.", size=10, bg="#fff7ed", fg="#9a3412").pack(anchor="w", pady=(6, 0))
        else:
            render_detail_lines(team_card, [f"- {name}" for name in teammates], bg="#fff7ed", fg="#9a3412")
