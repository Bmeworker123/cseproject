import tkinter as tk
from tkinter import messagebox

from tracker_app.app.components import Component
from tracker_app.ui import Button, EntryField, Label


class SignUpFormCard(Component):
    def __init__(self, page, wrapper):
        self.page = page
        super().__init__(wrapper)

    def render(self, wrapper):
        card = self.page._build_card(
            wrapper,
            "Create Account",
            "Create a student or professor account, then use classes and teams inside the professor workspace.",
        )

        self.page.name_field = EntryField(card, "Full Name")
        self.page.name_field.pack(fill="x")

        self.page.email_field = EntryField(card, "Email")
        self.page.email_field.pack(fill="x")

        self.page.password_field = EntryField(card, "Password", show="*")
        self.page.password_field.pack(fill="x")
        self.page.password_field.bind("<Return>", lambda _event: self.submit())

        self.page.role_var = tk.StringVar(value="student")
        Label(card, "Role", bg="white", fg="#000000").pack(anchor="w", pady=(12, 4))
        role_row = tk.Frame(card, bg="white")
        role_row.pack(anchor="w")
        tk.Radiobutton(
            role_row,
            text="Student",
            variable=self.page.role_var,
            value="student",
            bg="white",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(0, 14))
        tk.Radiobutton(
            role_row,
            text="Professor",
            variable=self.page.role_var,
            value="professor",
            bg="white",
            font=("Segoe UI", 10),
        ).pack(side="left")

        self.page.student_id_field = EntryField(card, "Student ID (optional)")
        self.page.student_id_field.pack(fill="x")

        self.page.department_field = EntryField(card, "Department (optional)")
        self.page.department_field.pack(fill="x")

        Button(card, "Create Account", self.submit, primary=True).pack(
            fill="x", pady=(18, 10)
        )
        Button(
            card,
            text="Already have an account? Sign in",
            command=self.page._toggle_auth_mode,
            relief="flat",
            bd=0,
        ).pack(anchor="w")

        Label(
            card,
            "No demo accounts exist. Teachers can create classes and teams after signing in.",
            size=9,
            bg="white",
            fg="#7b8794",
            wraplength=500,
            justify="left",
        ).pack(anchor="w", pady=10)

        self.page.name_field.focus_set()

    def submit(self):
        name = self.page.name_field.get().strip()
        email = self.page.email_field.get().strip().lower()
        password = self.page.password_field.get().strip()

        try:
            self.page._validate_email(email)
            self.page._validate_password(password)
            if not name:
                raise ValueError("Full name is required.")

            student_id = self.page.student_id_field.get().strip()
            department = self.page.department_field.get().strip()
            self.page.app.current_user = self.page.app.auth_repo.create_account(
                name,
                email,
                password,
                self.page.role_var.get(),
                student_id,
                department,
            )
            self.page.auth_message.config(text="")
            messagebox.showinfo(
                "Account created",
                "Your account was created and you are now signed in.",
            )
        except ValueError as error:
            self.page.auth_message.config(text=str(error))
            return
        self.page.app.show_dashboard()
