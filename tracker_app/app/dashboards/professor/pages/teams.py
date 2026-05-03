import tkinter as tk
from tkinter import messagebox

from tracker_app.ui import Button, Card, EntryField, Label, OptionField
from ..base import ProfessorPageBase


class ProfessorTeamsPage(ProfessorPageBase):
    def render(self, parent):
        Label(
            parent, text="Team Management", size=16, bold=True, bg="white", fg="#1f2933"
        ).pack(anchor="w")
        Label(
            parent,
            text="Create teams inside a class, then assign students to them from the Students page.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)
        self.team_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.team_message.pack(anchor="w", pady=(4, 8))

        form = Card(parent, bg="#f7f9fb")
        form.pack(fill="x", pady=10)
        Label(
            form, text="Create Team", size=13, bold=True, bg="#f7f9fb", fg="#102a43"
        ).pack(anchor="w")

        teacher_classes = self.teacher_classes()
        class_values = [f"{c['name']} ({c['term']})" for c in teacher_classes] or [
            "No Classes"
        ]
        self.team_class_var = tk.StringVar(value=class_values[0])
        OptionField(
            form, "Class", self.team_class_var, class_values, bg="#f7f9fb"
        ).pack(anchor="w")

        self.team_name_field = EntryField(form, "Team Name", bg="#f7f9fb")
        self.team_name_field.pack(fill="x")
        Button(form, "Create Team", self.create_team, primary=True).pack(
            anchor="w", pady=(14, 0)
        )

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        Label(
            list_frame, text="Teams", size=13, bold=True, bg="white", fg="#102a43"
        ).pack(anchor="w")

        if not teacher_classes:
            Label(
                list_frame,
                text="Create a class first, then add teams.",
                size=10,
                bg="white",
                fg="#52606d",
            ).pack(anchor="w", pady=(8, 0))
            return

        self.team_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            height=8,
            bd=0,
            highlightthickness=1,
            highlightbackground="#e1e4e8",
        )
        self.team_listbox.pack(fill="x", pady=(8, 8))
        self.team_records = []
        any_team = False
        students = self.app.professor_repo.list_students()
        for class_record in teacher_classes:
            teams = self.app.professor_repo.list_teams_for_class(class_record["id"])
            for team in teams:
                any_team = True
                self.team_records.append(team)
                members = [
                    s["name"] for s in students if s.get("team_id") == team["id"]
                ]
                label = ", ".join(members) if members else "Empty"
                self.team_listbox.insert(
                    tk.END,
                    f"{class_record['name']} ({class_record['term']}) | {team['name']} | Members: {label}",
                )

        if not any_team:
            Label(
                list_frame,
                text="No teams created yet.",
                size=10,
                bg="white",
                fg="#52606d",
            ).pack(anchor="w", pady=(8, 0))
            self.team_listbox.destroy()
            return

        Button(list_frame, "Delete Selected Team", self.delete_selected_team).pack(
            anchor="w", pady=(4, 0)
        )

    def create_team(self):
        class_value = self.team_class_var.get()
        team_name = self.team_name_field.get().strip()
        if class_value == "No Classes" or not team_name:
            self.team_message.config(
                text="Choose a class and enter a team name.", fg="#c0392b"
            )
            return

        class_record = next(
            (
                c
                for c in self.teacher_classes()
                if f"{c['name']} ({c['term']})" == class_value
            ),
            None,
        )
        if class_record:
            self.app.professor_repo.create_team(class_record["id"], team_name)
            self.team_message.config(
                text=f"Team '{team_name}' added to class.", fg="#1f7a45"
            )
            self.team_name_field.delete(0, tk.END)
            self.dashboard.render()

    def delete_selected_team(self):
        selection = self.team_listbox.curselection()
        if not selection:
            return
        team = self.team_records[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete team '{team['name']}'?"):
            self.app.professor_repo.delete_team(team["id"])
            self.team_message.config(text="Team deleted.", fg="#1f7a45")
            self.dashboard.render()
