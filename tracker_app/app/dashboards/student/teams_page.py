import tkinter as tk

from ....ui import Card, Label
from .base import StudentPageBase
from .components import render_detail_lines, render_empty_state, render_page_header, render_section_title


class StudentTeamsPage(StudentPageBase):
    def __init__(self, app):
        super().__init__(app)

    def render(self, parent):
        user = self.refresh_user()
        render_page_header(parent, "Teams", "See your assigned team and the classmates who are working with you.")

        if not user.get("class_id"):
            empty = render_empty_state(
                parent,
                "No class assigned yet.",
                "A professor needs to place you in a class before team information can appear here.",
                bg="#fff7ed",
                title_fg="#9a3412",
                message_fg="#b45309",
            )
            empty.pack(fill="x", pady=20)
            return

        card = Card(parent, bg="#f7f9fb", padx=18, pady=18)
        card.pack(fill="both", expand=True, pady=(12, 0))
        render_section_title(card, "Current Team", bg="#f7f9fb", fg="#102a43")

        details = [
            f"Class: {self.app.student_repo.class_name(user.get('class_id'))}",
            f"Team: {self.app.student_repo.team_name(user.get('team_id'))}",
        ]
        render_detail_lines(card, details, bg="#f7f9fb", fg="#334e68")

        if not user.get("team_id"):
            Label(
                card,
                text="Your professor has not assigned you to a team yet.",
                size=10,
                bg="#f7f9fb",
                fg="#52606d",
                wraplength=720,
                justify="left",
            ).pack(anchor="w", pady=(14, 0))
            return

        members = self.app.student_repo.team_members_for(user)
        Label(card, text="Members", size=11, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w", pady=(14, 6))
        for member in members:
            member_line = f"{member['name']} ({member['email']})"
            Label(card, text=member_line, size=10, bg="#f7f9fb", fg="#334e68", wraplength=720, justify="left").pack(anchor="w", pady=2)
