import tkinter as tk

from tracker_app.ui import Button, Card, Label, Table
from ..base import ProfessorPageBase


class ProfessorStudentsPage(ProfessorPageBase):
    def render(self, parent):
        Label(
            parent,
            text="Student Management",
            size=16,
            bold=True,
            bg="white",
            fg="#1f2933",
        ).pack(anchor="w")
        Label(
            parent,
            text="Inspect students, leave notes, set status, and assign them to classes and teams.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)

        self.professor_student_message = Label(
            parent, text="", size=10, bg="white", fg="#1f7a45"
        )
        self.professor_student_message.pack(anchor="w", pady=(4, 8))

        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)

        left = Card(shell, bg="#f7f9fb", width=300)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        Label(
            left, text="Students", size=13, bold=True, bg="#f7f9fb", fg="#102a43"
        ).pack(anchor="w")

        self.student_table = Table(left, bg="#f7f9fb")
        self.student_table.pack(fill="both", expand=True, pady=8)
        self.student_table.on_select(lambda row: self.load_selected_student())

        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)

        Label(
            right, text="Student Details", size=13, bold=True, bg="white", fg="#102a43"
        ).pack(anchor="w")
        self.student_detail_label = Label(
            right,
            text="Select a student to manage their record.",
            size=10,
            bg="white",
            fg="#334e68",
            justify="left",
        )
        self.student_detail_label.pack(anchor="w", pady=(6, 12))

        Label(right, text="Teacher Notes", size=10, bg="white").pack(anchor="w")
        self.teacher_notes_text = tk.Text(right, height=4, font=("Segoe UI", 10))
        self.teacher_notes_text.pack(fill="x", pady=(4, 14))

        controls = tk.Frame(right, bg="white")
        controls.pack(fill="x", pady=(0, 18))

        status_box = tk.Frame(controls, bg="white")
        status_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        Label(status_box, text="Account Status", size=10, bg="white").pack(anchor="w")
        self.account_status_var = tk.StringVar(value="Active")
        tk.OptionMenu(status_box, self.account_status_var, "Active", "Suspended").pack(
            fill="x", pady=(4, 0)
        )

        class_box = tk.Frame(controls, bg="white")
        class_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        Label(class_box, text="Assign Class", size=10, bg="white").pack(anchor="w")
        self.assign_class_var = tk.StringVar(value="Not Assigned")
        self.assign_class_menu = tk.OptionMenu(
            class_box, self.assign_class_var, "Not Assigned"
        )
        self.assign_class_menu.pack(fill="x", pady=(4, 0))

        team_box = tk.Frame(controls, bg="white")
        team_box.pack(side="left", fill="x", expand=True)
        Label(team_box, text="Assign Team", size=10, bg="white").pack(anchor="w")
        self.assign_team_var = tk.StringVar(value="Not Assigned")
        self.assign_team_menu = tk.OptionMenu(
            team_box, self.assign_team_var, "Not Assigned"
        )
        self.assign_team_menu.pack(fill="x", pady=(4, 0))

        row = tk.Frame(right, bg="white")
        row.pack(fill="x")
        Button(
            row, "Save Student Changes", self.save_student_changes, primary=True
        ).pack(side="left", padx=(0, 8))
        Button(row, "Refresh List", self.dashboard.render).pack(side="left")

        self.refresh_student_list()

    def refresh_student_list(self):
        students = self.app.professor_repo.list_students()
        students.sort(key=lambda user: user.get("created_at", ""), reverse=True)
        self.student_records = students
        self.student_table.clear()
        self.student_table.set_header(["Name", "Status"])
        for user in students:
            status = user.get("status", "Active")
            self.student_table.add_row([user["name"], status])
        self.update_student_dropdowns()

    def update_student_dropdowns(self):
        class_names = ["Not Assigned"] + [
            f"{c['name']} ({c['term']})" for c in self.teacher_classes()
        ]
        self.assign_class_menu["menu"].delete(0, "end")
        for name in class_names:
            self.assign_class_menu["menu"].add_command(
                label=name,
                command=tk._setit(self.assign_class_var, name, self.on_class_change),
            )

    def on_class_change(self, class_name):
        if class_name == "Not Assigned":
            self.assign_team_var.set("Not Assigned")
            self.assign_team_menu["menu"].delete(0, "end")
            self.assign_team_menu["menu"].add_command(
                label="Not Assigned",
                command=tk._setit(self.assign_team_var, "Not Assigned"),
            )
            return

        class_record = next(
            (
                c
                for c in self.teacher_classes()
                if f"{c['name']} ({c['term']})" == class_name
            ),
            None,
        )
        if not class_record:
            return

        teams = self.app.professor_repo.list_teams_for_class(class_record["id"])
        team_names = ["Not Assigned"] + [t["name"] for t in teams]
        self.assign_team_menu["menu"].delete(0, "end")
        for name in team_names:
            self.assign_team_menu["menu"].add_command(
                label=name, command=tk._setit(self.assign_team_var, name)
            )
        self.assign_team_var.set("Not Assigned")

    def load_selected_student(self):
        index = self.student_table.get_selected_index()
        if index == -1:
            return

        user = self.student_records[index]
        self.app.selected_student_id = user["id"]
        self.student_detail_label.config(
            text=(
                f"Email: {user['email']}\n"
                f"Student ID: {user.get('student_id', 'N/A')}\n"
                f"Department: {user.get('department', 'N/A')}"
            )
        )
        self.teacher_notes_text.delete("1.0", tk.END)
        self.teacher_notes_text.insert("1.0", user.get("notes", ""))
        self.account_status_var.set(user.get("status", "Active"))

        class_id = user.get("class_id")
        if class_id:
            class_record = self.app.professor_repo.find_class_by_id(class_id)
            if class_record:
                name = f"{class_record['name']} ({class_record['term']})"
                self.assign_class_var.set(name)
                self.on_class_change(name)
                team_id = user.get("team_id")
                if team_id:
                    team_record = next(
                        (
                            t
                            for t in self.app.professor_repo.list_teams()
                            if t["id"] == team_id
                        ),
                        None,
                    )
                    self.assign_team_var.set(
                        team_record["name"] if team_record else "Not Assigned"
                    )
                else:
                    self.assign_team_var.set("Not Assigned")
                return

        self.assign_class_var.set("Not Assigned")
        self.on_class_change("Not Assigned")

    def save_student_changes(self):
        if not self.app.selected_student_id:
            return

        notes = self.teacher_notes_text.get("1.0", "end").strip()
        status = self.account_status_var.get()
        class_name = self.assign_class_var.get()
        team_name = self.assign_team_var.get()
        updates = {"notes": notes, "status": status}

        if class_name == "Not Assigned":
            updates["class_id"] = None
            updates["team_id"] = None
        else:
            class_record = next(
                (
                    c
                    for c in self.teacher_classes()
                    if f"{c['name']} ({c['term']})" == class_name
                ),
                None,
            )
            if class_record:
                updates["class_id"] = class_record["id"]
                if team_name == "Not Assigned":
                    updates["team_id"] = None
                else:
                    teams = self.app.professor_repo.list_teams_for_class(
                        class_record["id"]
                    )
                    team_record = next(
                        (t for t in teams if t["name"] == team_name), None
                    )
                    updates["team_id"] = team_record["id"] if team_record else None

        self.app.professor_repo.update_user(self.app.selected_student_id, updates)
        self.professor_student_message.config(
            text="Student record updated successfully.", fg="#1f7a45"
        )
        self.refresh_student_list()
