import tkinter as tk

from ....ui import Button, Card, Label
from .base import StudentPageBase
from .components import render_detail_lines, render_empty_state, render_page_header, render_section_title


class StudentTeamsPage(StudentPageBase):
    def __init__(self, app):
        super().__init__(app)

    def render(self, parent):
        user = self.refresh_user()
        render_page_header(parent, "Teams", "Pair with classmates, see your current team, and manage your student team membership.")

        self.team_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.team_message.pack(anchor="w", pady=(4, 8))

        if not user.get("class_id"):
            empty = render_empty_state(
                parent,
                "No class assigned yet.",
                "A professor needs to place you in a class before you can pair with teammates.",
                bg="#fff7ed",
                title_fg="#9a3412",
                message_fg="#b45309",
            )
            empty.pack(fill="x", pady=20)
            return

        top = tk.Frame(parent, bg="white")
        top.pack(fill="both", expand=True, pady=(8, 0))

        self._render_current_team(top, user)
        self._render_pairing_panel(top, user)

    def _render_current_team(self, parent, user):
        card = Card(parent, bg="#f7f9fb", padx=18, pady=18, width=340)
        card.pack(side="left", fill="y", padx=(0, 12))
        card.pack_propagate(False)
        render_section_title(card, "Current Team", bg="#f7f9fb", fg="#102a43")

        details = [
            f"Class: {self.app.student_repo.class_name(user.get('class_id'))}",
            f"Team: {self.app.student_repo.team_name(user.get('team_id'))}",
        ]
        render_detail_lines(card, details, bg="#f7f9fb", fg="#334e68")

        members = self.app.student_repo.team_members_for(user)
        Label(card, text="Members", size=11, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w", pady=(14, 6))
        for member in members:
            member_line = f"{member['name']} ({member['email']})"
            Label(card, text=member_line, size=10, bg="#f7f9fb", fg="#334e68", wraplength=280, justify="left").pack(anchor="w", pady=2)

        if user.get("team_id"):
            Button(card, "Leave Team", self.leave_team).pack(anchor="w", pady=(16, 0))

    def _render_pairing_panel(self, parent, user):
        card = Card(parent, bg="#eef8f1", padx=18, pady=18)
        card.pack(side="left", fill="both", expand=True)
        render_section_title(card, "Pair With Classmates", bg="#eef8f1", fg="#14532d")
        Label(
            card,
            text="Select a classmate to create a new team, join their team, or add them to yours.",
            size=10,
            bg="#eef8f1",
            fg="#1f7a45",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(6, 10))

        self.candidate_records = self.app.student_repo.available_pairing_candidates(user)
        if not self.candidate_records:
            Label(card, text="No available classmates to pair with right now.", size=10, bg="#eef8f1", fg="#52606d").pack(anchor="w", pady=(6, 0))
            return

        self.candidate_listbox = tk.Listbox(card, font=("Segoe UI", 10), height=10, bd=0, highlightthickness=1, highlightbackground="#d9e2ec")
        self.candidate_listbox.pack(fill="both", expand=True, pady=(4, 12))
        for classmate in self.candidate_records:
            team_name = self.app.student_repo.team_name(classmate.get("team_id"))
            team_text = team_name if classmate.get("team_id") else "No Team"
            self.candidate_listbox.insert(
                tk.END,
                f"{classmate['name']} | {classmate.get('email')} | Team: {team_text}",
            )

        action_row = tk.Frame(card, bg="#eef8f1")
        action_row.pack(anchor="w")
        Button(action_row, "Pair With Selected Student", self.pair_with_selected, primary=True).pack(side="left", padx=(0, 8))
        Button(action_row, "Refresh", self.app.student_dashboard.render).pack(side="left")

    def pair_with_selected(self):
        selection = self.candidate_listbox.curselection()
        if not selection:
            self.team_message.config(text="Choose a classmate first.", fg="#c0392b")
            return
        partner = self.candidate_records[selection[0]]
        try:
            result = self.app.student_repo.pair_with_student(self.app.current_user["id"], partner["id"])
        except ValueError as error:
            self.team_message.config(text=str(error), fg="#c0392b")
            return

        member_names = ", ".join(member["name"] for member in result["members"])
        self.team_message.config(
            text=f"Team updated: {result['team_name']} ({member_names})",
            fg="#1f7a45",
        )
        self.app.current_user = self.app.student_repo.refresh_user(self.app.current_user["id"])
        self.app.student_dashboard.render()

    def leave_team(self):
        try:
            self.app.student_repo.leave_team(self.app.current_user["id"])
        except ValueError as error:
            self.team_message.config(text=str(error), fg="#c0392b")
            return

        self.app.current_user = self.app.student_repo.refresh_user(self.app.current_user["id"])
        self.team_message.config(text="You left the team successfully.", fg="#1f7a45")
        self.app.student_dashboard.render()
