import tkinter as tk

from ....ui import Button, Label, EntryField, TextField, OptionField
from .base import StudentPageBase
from .components import render_page_header


class StudentProjectFormPage(StudentPageBase):
    def __init__(self, app, navigate):
        super().__init__(app)
        self.navigate = navigate

    def render(self, parent):
        project = self.app.student_repo.project_for(self.app.current_user)
        if self.is_team_project():
            subtitle = "Submit your shared team project and keep priority and progress updated for everyone on the team."
        else:
            subtitle = "Submit your project and keep priority and progress updated."
        render_page_header(parent, "Project Form", subtitle)

        self.student_form_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.student_form_message.pack(anchor="w", pady=(4, 8))

        form = tk.Frame(parent, bg="white")
        form.pack(fill="x", pady=10)

        self.project_title_field = EntryField(form, "Project Title")
        self.project_title_field.pack(fill="x")

        if self.is_team_project():
            Label(
                form,
                text=f"This project is shared with team: {self.app.student_repo.team_name(self.app.current_user.get('team_id'))}",
                size=10,
                bg="white",
                fg="#52606d",
            ).pack(anchor="w", pady=(0, 10))

        self.project_notes_field = TextField(form, "Project Description / Notes", height=6)
        self.project_notes_field.pack(fill="x")

        row = tk.Frame(form, bg="white")
        row.pack(fill="x", pady=16)

        self.priority_var = tk.StringVar(value="Medium")
        OptionField(row, "Priority", self.priority_var, ["Low", "Medium", "High"]).pack(fill="x", expand=True)

        Label(form, text="Progress", size=10, bg="white").pack(anchor="w", pady=(12, 4))
        self.progress_scale = tk.Scale(form, from_=0, to=100, orient="horizontal", bg="white", highlightthickness=0, length=360)
        self.progress_scale.pack(anchor="w")

        button_row = tk.Frame(form, bg="white")
        button_row.pack(anchor="w", pady=(16, 0))
        Button(button_row, "Save Project", self.save_student_project, primary=True).pack(side="left", padx=(0, 8))
        Button(button_row, "Go To Status", lambda: self.navigate("status")).pack(side="left")

        if project:
            self.project_title_field.insert(0, project["title"])
            self.project_notes_field.insert("1.0", project["notes"])
            self.priority_var.set(project.get("priority", "Medium"))
            self.progress_scale.set(project.get("progress", 0))

    def save_student_project(self):
        title = self.project_title_field.get().strip()
        notes = self.project_notes_field.get("1.0", "end").strip()
        progress = self.progress_scale.get()
        priority = self.priority_var.get()

        if not title:
            self.student_form_message.config(text="Project title is required.", fg="#c0392b")
            return

        self.refresh_user()
        project = self.app.student_repo.save_project(self.app.current_user, title, notes, progress, priority)

        if project.get("requested_progress") is not None:
            message = f"Project saved. Progress change to {project['requested_progress']}% is waiting for professor approval."
        else:
            message = "Team project saved successfully." if self.is_team_project() else f"Project saved with status: {project['status']}"
        self.student_form_message.config(text=message, fg="#1f7a45")
