import tkinter as tk

from ..base import ProfessorPageBase
from .....ui import Button, Label, Card, TextField, OptionField


class ProfessorProjectsPage(ProfessorPageBase):
    def render(self, parent):
        Label(parent, text="Project Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Review student projects, class/team placement, and approval status.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.professor_project_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.professor_project_message.pack(anchor="w", pady=(4, 8))

        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)

        left = Card(shell, bg="#f7f9fb", width=320)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        Label(left, text="Projects", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        self.project_listbox = tk.Listbox(left, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.project_listbox.pack(fill="both", expand=True, pady=8)
        self.project_listbox.bind("<<ListboxSelect>>", lambda _event: self.load_selected_project())

        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)

        Label(right, text="Project Details", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")
        self.project_detail_label = Label(right, text="Select a project to review it.", size=10, bg="white", fg="#334e68", justify="left")
        self.project_detail_label.pack(anchor="w", pady=(6, 12))

        progress_box = Card(right, bg="#eef8f1", padx=14, pady=14)
        progress_box.pack(fill="x", pady=(0, 16))
        Label(progress_box, text="Progress Approval", size=12, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")

        progress_row = tk.Frame(progress_box, bg="#eef8f1")
        progress_row.pack(fill="x", pady=8)
        progress_left = tk.Frame(progress_row, bg="#eef8f1")
        progress_left.pack(side="left", fill="x", expand=True)
        Label(progress_left, text="Professor Progress", size=10, bg="#eef8f1").pack(anchor="w")
        self.professor_progress_scale = tk.Scale(progress_left, from_=0, to=100, orient="horizontal", bg="#eef8f1", highlightthickness=0)
        self.professor_progress_scale.pack(fill="x", pady=(4, 0))

        progress_right = tk.Frame(progress_row, bg="#eef8f1")
        progress_right.pack(side="left", fill="x", expand=True, padx=(16, 0))
        Label(progress_right, text="Progress Requested", size=10, bg="#eef8f1").pack(anchor="w")
        self.progress_request_label = Label(progress_right, text="No project selected.", size=10, bg="#eef8f1", fg="#334e68", justify="left")
        self.progress_request_label.pack(anchor="w", pady=(8, 0))

        progress_actions = tk.Frame(progress_box, bg="#eef8f1")
        progress_actions.pack(anchor="w")
        Button(progress_actions, "Approve Progress", self.approve_progress_request, primary=True).pack(side="left", padx=(0, 8))
        Button(progress_actions, "Reject Progress", self.reject_progress_request).pack(side="left", padx=(0, 8))
        Button(progress_actions, "Save Professor Progress", self.save_professor_progress).pack(side="left")

        row = tk.Frame(right, bg="white")
        row.pack(fill="x", pady=(0, 8))
        left_controls = tk.Frame(row, bg="white")
        left_controls.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.meeting_status_var = tk.StringVar(value="Pending")
        OptionField(left_controls, "Meeting Status", self.meeting_status_var, ["Pending", "Scheduled", "Completed", "Cancelled"]).pack(fill="x")

        right_controls = tk.Frame(row, bg="white")
        right_controls.pack(side="left", fill="x", expand=True)
        self.project_stage_var = tk.StringVar(value="Proposal")
        OptionField(right_controls, "Stage", self.project_stage_var, ["Proposal", "Requirement Analysis", "Design", "Development", "Testing", "Deployment"]).pack(fill="x")

        self.professor_notes_field = TextField(right, "Professor Notes", height=3)
        self.professor_notes_field.pack(fill="x")

        action_row = tk.Frame(right, bg="white")
        action_row.pack(anchor="w")
        Button(action_row, "Approve", lambda: self.update_project_status("Approved"), primary=True).pack(side="left", padx=(0, 8))
        Button(action_row, "Request Changes", lambda: self.update_project_status("Changes Requested")).pack(side="left", padx=(0, 8))
        Button(action_row, "Save Notes Only", lambda: self.update_project_status(None)).pack(side="left")

        self.refresh_project_list()

    def refresh_project_list(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        all_projects = self.app.professor_repo.list_projects()
        self.project_records = [
            project
            for project in all_projects
            if not teacher_class_ids or project.get("class_id") in teacher_class_ids or project.get("class_id") is None
        ]
        self.project_listbox.delete(0, tk.END)
        for project in self.project_records:
            team_name = self.app.professor_repo.get_team_name(project.get("team_id")) or "No Team"
            self.project_listbox.insert(tk.END, f"{team_name} | {project['title']} | {project['status']}")

    def load_selected_project(self):
        selection = self.project_listbox.curselection()
        if not selection:
            return

        project = self.project_records[selection[0]]
        self.app.selected_project_id = project["id"]
        class_name = self.app.professor_repo.get_class_name(project.get("class_id")) or "Not Assigned"
        team_name = self.app.professor_repo.get_team_name(project.get("team_id")) or "Not Assigned"
        detail_text = (
            f"Team: {team_name}\n"
            f"Class: {class_name}\n"
            f"Priority: {project.get('priority', 'Medium')}\n"
            f"Last Updated: {project.get('last_updated', 'N/A')}"
        )
        self.project_detail_label.config(text=detail_text)
        self.professor_notes_field.delete("1.0", tk.END)
        self.professor_notes_field.insert("1.0", project.get("professor_notes", ""))
        self.professor_progress_scale.set(project.get("progress", 0))
        self.meeting_status_var.set(project.get("meeting_status", "Pending"))
        self.project_stage_var.set(project.get("stage", "Proposal"))

        req = project.get("requested_progress")
        if req is not None:
            self.progress_request_label.config(text=f"Student requested change to {req}%.\nApprove or reject this request.", fg="#b45309")
        else:
            self.progress_request_label.config(text="No pending progress requests.", fg="#52606d")

    def update_project_status(self, status):
        if not self.app.selected_project_id:
            return

        notes = self.professor_notes_field.get("1.0", "end").strip()
        meeting = self.meeting_status_var.get()
        stage = self.project_stage_var.get()
        updates = {"professor_notes": notes, "meeting_status": meeting, "stage": stage}
        if status:
            updates["status"] = status

        self.app.professor_repo.update_project(
            self.app.selected_project_id,
            updates,
            notification=f"Professor updated status to {status or 'Notes Only'}",
        )
        self.professor_project_message.config(text="Project record updated.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def save_professor_progress(self):
        if not self.app.selected_project_id:
            return

        value = self.professor_progress_scale.get()
        self.app.professor_repo.update_project(
            self.app.selected_project_id,
            {"progress": value, "requested_progress": None},
            notification=f"Professor set progress to {value}%",
        )
        self.professor_project_message.config(text=f"Progress manually set to {value}%.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def approve_progress_request(self):
        if not self.app.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] != self.app.selected_project_id:
                continue
            req = project.get("requested_progress")
            if req is not None:
                self.app.professor_repo.update_project(
                    project["id"],
                    {"progress": req, "requested_progress": None},
                    notification=f"Progress request for {req}% APPROVED.",
                )
                self.professor_project_message.config(text=f"Approved progress of {req}%.", fg="#1f7a45")
                self.refresh_project_list()
                self.reload_selected_project_details()
            return

    def reject_progress_request(self):
        if not self.app.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] != self.app.selected_project_id:
                continue
            req = project.get("requested_progress")
            if req is not None:
                self.app.professor_repo.update_project(
                    project["id"],
                    {"requested_progress": None},
                    notification=f"Progress request for {req}% REJECTED.",
                )
                self.professor_project_message.config(text=f"Rejected progress request of {req}%.", fg="#c0392b")
                self.refresh_project_list()
                self.reload_selected_project_details()
            return

    def reload_selected_project_details(self):
        if not self.app.selected_project_id:
            return
        for index, project in enumerate(self.project_records):
            if project["id"] == self.app.selected_project_id:
                self.project_listbox.selection_clear(0, tk.END)
                self.project_listbox.selection_set(index)
                self.load_selected_project()
                return
