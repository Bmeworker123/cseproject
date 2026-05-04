import tkinter as tk
from tkinter import messagebox

from tracker_app.ui import Button, Card, EntryField, Label, Table
from ..base import ProfessorPageBase


class ProfessorClassesPage(ProfessorPageBase):
    def render(self, parent):
        Label(
            parent,
            text="Class Management",
            size=16,
            bold=True,
            bg="white",
            fg="#1f2933",
        ).pack(anchor="w")
        Label(
            parent,
            text="Create classes and keep track of how many students belong to each one.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)
        self.class_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.class_message.pack(anchor="w", pady=(4, 8))

        form = Card(parent, bg="#f7f9fb")
        form.pack(fill="x", pady=10)
        Label(
            form, text="Create Class", size=13, bold=True, bg="#f7f9fb", fg="#102a43"
        ).pack(anchor="w")
        self.class_name_field = EntryField(form, "Class Name", bg="#f7f9fb")
        self.class_name_field.pack(fill="x")
        self.class_term_field = EntryField(form, "Term", bg="#f7f9fb")
        self.class_term_field.pack(fill="x")
        Button(form, "Create Class", self.create_class, primary=True).pack(
            anchor="w", pady=(14, 0)
        )

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        Label(
            list_frame,
            text="Your Classes",
            size=13,
            bold=True,
            bg="white",
            fg="#102a43",
        ).pack(anchor="w")

        classes = self.teacher_classes()
        if not classes:
            Label(
                list_frame,
                text="No classes created yet.",
                size=10,
                bg="white",
                fg="#52606d",
            ).pack(anchor="w", pady=(8, 0))
            return

        self.class_table = Table(list_frame)
        self.class_table.pack(fill="x", pady=(8, 8))
        self.class_table.set_header(["Class Name", "Term", "Students", "Created"])
        
        students = self.app.professor_repo.list_students()
        for class_record in classes:
            count = len(
                [
                    student
                    for student in students
                    if student.get("class_id") == class_record["id"]
                ]
            )
            self.class_table.add_row(
                [
                    class_record["name"],
                    class_record["term"],
                    str(count),
                    class_record["created_at"],
                ]
            )
        Button(list_frame, "Delete Selected Class", self.delete_selected_class).pack(
            anchor="w", pady=(4, 0)
        )

    def create_class(self):
        name = self.class_name_field.get().strip()
        term = self.class_term_field.get().strip()
        if not name or not term:
            self.class_message.config(
                text="Class name and term are required.", fg="#c0392b"
            )
            return
        self.app.professor_repo.create_class(self.app.current_user, name, term)
        self.class_message.config(text=f"Class '{name}' created.", fg="#1f7a45")
        self.class_name_field.delete(0, tk.END)
        self.class_term_field.delete(0, tk.END)
        self.dashboard.render()

    def delete_selected_class(self):
        index = self.class_table.get_selected_index()
        if index == -1:
            return
        class_record = self.teacher_classes()[index]
        if messagebox.askyesno(
            "Confirm Delete", f"Delete class '{class_record['name']}'?"
        ):
            self.app.professor_repo.delete_class(class_record["id"])
            self.class_message.config(text="Class deleted.", fg="#1f7a45")
            self.dashboard.render()
