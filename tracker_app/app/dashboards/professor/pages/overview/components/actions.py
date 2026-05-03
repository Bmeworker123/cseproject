import tkinter as tk

from tracker_app.app.components import Component
from tracker_app.ui import Button, Card, Label


class OverviewTeacherActionsCard(Component):
    def __init__(self, page, parent):
        self.page = page
        super().__init__(parent)

    def render(self, parent):
        actions = Card(parent, bg="#eef8f1")
        actions.pack(fill="x")

        Label(
            actions,
            text="Teacher Actions",
            size=13,
            bold=True,
            bg="#eef8f1",
            fg="#14532d",
        ).pack(anchor="w")

        Label(
            actions,
            text="Use Students to assign classes, Classes to create offerings, Teams to group students, and Projects to review submissions.",
            size=10,
            bg="#eef8f1",
            fg="#1f7a45",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(6, 10))

        row = tk.Frame(actions, bg="#eef8f1")
        row.pack(anchor="w")

        Button(
            row,
            "Open Classes",
            lambda: self.page.dashboard.set_page("classes"),
            primary=True,
        ).pack(side="left", padx=(0, 8))

        Button(
            row, 
            "Open Teams",
            lambda: self.page.dashboard.set_page("teams")
        ).pack(side="left", padx=(0, 8))

        Button(
            row,
            "Open Projects",
            lambda: self.page.dashboard.set_page("projects")
        ).pack(side="left")
