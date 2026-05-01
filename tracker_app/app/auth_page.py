import re
import tkinter as tk
from tkinter import messagebox

from ..base import AuthMode
from ..ui import Button, Label, Card, EntryField

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthPage:
    def __init__(self, app):
        self.app = app

    def render(self):
        self.app.clear_screen()
        wrapper = tk.Frame(self.app.main_frame, bg="#eef2f6")
        wrapper.pack(fill="both", expand=True)

        card = Card(wrapper, padx=24, pady=24)
        card.pack(expand=True, ipadx=18, ipady=12)

        title = "Create Account" if self.app.auth_mode == AuthMode.SIGNUP.value else "Sign In"
        subtitle = (
            "Create a student or professor account, then use classes and teams inside the professor workspace."
            if self.app.auth_mode == AuthMode.SIGNUP.value
            else "Sign in with the email and password you created in this app."
        )

        Label(card, "Project Approval Tracker", size=17, bold=True, fg="#1f2933").pack(anchor="w", pady=(14, 0))
        Label(card, title, size=14, bold=True, fg="#102a43").pack(anchor="w", pady=8)
        Label(card, subtitle, fg="#52606d", wraplength=500, justify="left").pack(anchor="w")

        self.auth_message = Label(card, "", bg="white", fg="#c0392b", size=9)
        self.auth_message.pack(anchor="w", pady=(10, 0))

        if self.app.auth_mode == AuthMode.SIGNUP.value:
            self.name_field = EntryField(card, "Full Name")
            self.name_field.pack(fill="x")

        self.email_field = EntryField(card, "Email")
        self.email_field.pack(fill="x")

        self.password_field = EntryField(card, "Password", show="*")
        self.password_field.pack(fill="x")
        self.password_field.bind("<Return>", lambda _event: self.submit_auth())

        self.role_var = tk.StringVar(value="student")
        if self.app.auth_mode == AuthMode.SIGNUP.value:
            Label(card, "Role", bg="white", fg="#000000").pack(anchor="w", pady=(12, 4))
            role_row = tk.Frame(card, bg="white")
            role_row.pack(anchor="w")
            tk.Radiobutton(
                role_row,
                text="Student",
                variable=self.role_var,
                value="student",
                bg="white",
                font=("Segoe UI", 10),
            ).pack(side="left", padx=(0, 14))
            tk.Radiobutton(
                role_row,
                text="Professor",
                variable=self.role_var,
                value="professor",
                bg="white",
                font=("Segoe UI", 10),
            ).pack(side="left")

            self.student_id_field = EntryField(card, "Student ID (optional)")
            self.student_id_field.pack(fill="x")

            self.department_field = EntryField(card, "Department (optional)")
            self.department_field.pack(fill="x")

        primary_text = "Create Account" if self.app.auth_mode == AuthMode.SIGNUP.value else "Sign In"
        Button(card, primary_text, self.submit_auth, primary=True).pack(fill="x", pady=(18, 10))

        switch_text = (
            "Already have an account? Sign in"
            if self.app.auth_mode == AuthMode.SIGNUP.value
            else "Need an account? Create one"
        )
        Button(card, text=switch_text, command=self._toggle_auth_mode, relief="flat", bd=0).pack(anchor="w")

        Label(
            card,
            "No demo accounts exist. Teachers can create classes and teams after signing in.",
            size=9,
            bg="white",
            fg="#7b8794",
            wraplength=500,
            justify="left",
        ).pack(anchor="w", pady=10)

        if self.app.auth_mode == AuthMode.SIGNUP.value:
            self.name_field.focus_set()
        else:
            self.email_field.focus_set()

    def _toggle_auth_mode(self):
        self.app.auth_mode = (
            AuthMode.SIGNUP.value
            if self.app.auth_mode == AuthMode.SIGNIN.value
            else AuthMode.SIGNIN.value
        )
        self.render()

    def _validate_email(self, email):
        if not email:
            raise ValueError("Email is required.")
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Enter a valid email address.")

    def _validate_password(self, password):
        if not password:
            raise ValueError("Password is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

    def submit_auth(self):
        name = self.name_field.get().strip() if self.app.auth_mode == AuthMode.SIGNUP.value else ""
        email = self.email_field.get().strip().lower()
        password = self.password_field.get().strip()

        try:
            self._validate_email(email)
            self._validate_password(password)
            if self.app.auth_mode == AuthMode.SIGNUP.value:
                if not name:
                    raise ValueError("Full name is required.")
                student_id = self.student_id_field.get().strip()
                department = self.department_field.get().strip()
                self.app.current_user = self.app.auth_repo.create_account(
                    name,
                    email,
                    password,
                    self.role_var.get(),
                    student_id,
                    department,
                )
                self.auth_message.config(text="")
                messagebox.showinfo(
                    "Account created",
                    "Your account was created and you are now signed in.",
                )
            else:
                self.app.current_user = self.app.auth_repo.sign_in(email, password)
                self.auth_message.config(text="")
        except ValueError as error:
            self.auth_message.config(text=str(error))
            return
        self.app.show_dashboard()
