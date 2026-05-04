import tkinter as tk

from tracker_app.ui import Button, Card, Label, Table
from ..base import ProfessorPageBase


class ProfessorProjectsPage(ProfessorPageBase):
    def render(self, parent):
        Label(
            parent,
            text="Project Management",
            size=16,
            bold=True,
            bg="white",
            fg="#1f2933",
        ).pack(anchor="w")
        Label(
            parent,
            text="Review team projects and approve or reject them.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)
        self.professor_project_message = Label(
            parent, text="", size=10, bg="white", fg="#1f7a45"
        )
        self.professor_project_message.pack(anchor="w", pady=(4, 8))

        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)

        left = Card(shell, bg="#f7f9fb", width=420)
        left.pack(side="left", fill="both", padx=(0, 16))
        left.pack_propagate(False)
        Label(
            left, text="Projects", size=13, bold=True, bg="#f7f9fb", fg="#102a43"
        ).pack(anchor="w")

        self.project_table = Table(left, bg="#f7f9fb")
        self.project_table.pack(fill="both", expand=True, pady=8)
        self.project_table.on_select(lambda row: self.load_selected_project())

        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)

        Label(
            right, text="Project Details", size=13, bold=True, bg="white", fg="#102a43"
        ).pack(anchor="w")
        self.project_detail_label = Label(
            right,
            text="Select a project to review it.",
            size=10,
            bg="white",
            fg="#334e68",
            justify="left",
        )
        self.project_detail_label.pack(anchor="w", pady=(6, 12))

        row = tk.Frame(right, bg="white")
        row.pack(fill="x", pady=(0, 8))

        action_row = tk.Frame(right, bg="white")
        action_row.pack(anchor="w")
        Button(
            action_row,
            "Approve",
            lambda: self.update_project_status("Approved"),
            primary=True,
        ).pack(side="left", padx=(0, 8))
        Button(
            action_row, "Reject", lambda: self.update_project_status("Rejected")
        ).pack(side="left")

        self.refresh_project_list()

    def refresh_project_list(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        all_projects = self.app.professor_repo.list_projects()
        self.project_records = [
            project
            for project in all_projects
            if not teacher_class_ids
            or project.get("class_id") in teacher_class_ids
            or project.get("class_id") is None
        ]
        self.project_table.clear()
        self.project_table.set_header(["Team", "Title", "Status"])
        for project in self.project_records:
            team_name = (
                self.app.professor_repo.get_team_name(project.get("team_id"))
                or "No Team"
            )
            self.project_table.add_row(
                [
                    team_name,
                    project["title"],
                    project.get("approval_status", "Pending Approval"),
                ]
            )

    def load_selected_project(self):
        index = self.project_table.get_selected_index()
        if index == -1:
            return

        project = self.project_records[index]
        self.app.selected_project_id = project["id"]
        class_name = (
            self.app.professor_repo.get_class_name(project.get("class_id"))
            or "Not Assigned"
        )
        team_name = (
            self.app.professor_repo.get_team_name(project.get("team_id"))
            or "Not Assigned"
        )
        detail_text = (
            f"Team: {team_name}\n"
            f"Class: {class_name}\n"
            f"Approval Status: {project.get('approval_status', 'Pending Approval')}\n"
            f"Last Updated: {project.get('last_updated', 'N/A')}"
        )
        self.project_detail_label.config(text=detail_text)

    def update_project_status(self, status):
        if not self.app.selected_project_id:
            return

        updates = {"approval_status": status}

        self.app.professor_repo.update_project(
            self.app.selected_project_id,
            updates,
        )
        self.professor_project_message.config(
            text="Project status updated.",
            fg="#1f7a45" if status == "Approved" else "#c0392b",
        )
        self.refresh_project_list()
        self.reload_selected_project_details()

    def reload_selected_project_details(self):
        if not self.app.selected_project_id:
            return
        for index, project in enumerate(self.project_records):
            if project["id"] == self.app.selected_project_id:
                self.project_table.select_index(index)
                return
