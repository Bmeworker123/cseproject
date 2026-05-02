import tkinter as tk

from ....ui import Button, Label, EntryField, TextField
from .base import StudentPageBase
from .components import render_page_header


class StudentProjectFormPage(StudentPageBase):
    def __init__(self, app):
        super().__init__(app)

    def render(self, parent):
        project = self.app.student_repo.project_for(self.app.current_user)
        render_page_header(parent, "Project Form", "Submit your project for team approval.")

        self.student_form_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.student_form_message.pack(anchor="w", pady=(4, 8))

        form = tk.Frame(parent, bg="white")
        form.pack(fill="x", pady=10)

        self.project_title_field = EntryField(form, "Project Title")
        self.project_title_field.pack(fill="x")

        self.project_notes_field = TextField(form, "Project Description / Notes", height=6)
        self.project_notes_field.pack(fill="x")

        button_row = tk.Frame(form, bg="white")
        button_row.pack(anchor="w", pady=(16, 0))
        Button(button_row, "Save Project", self.save_student_project, primary=True).pack(side="left", padx=(0, 8))

        if project:
            self.project_title_field.insert(0, project["title"])
            self.project_notes_field.insert("1.0", project["notes"])

    def save_student_project(self):
        title = self.project_title_field.get().strip()
        notes = self.project_notes_field.get("1.0", "end").strip()

        if not title:
            self.student_form_message.config(text="Project title is required.", fg="#c0392b")
            return

        self.refresh_user()
        if not self.app.current_user.get("team_id"):
            self.student_form_message.config(text="You need to be assigned to a team before saving a project.", fg="#c0392b")
            return

        self.app.student_repo.save_project(self.app.current_user, title, notes)
        self.student_form_message.config(text="Project saved. Waiting for team approval.", fg="#1f7a45")
