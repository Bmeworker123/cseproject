import re
import tkinter as tk
from tkinter import messagebox

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthRepository:
    def __init__(self, store):
        self.store = store

    def create_account(self, name, email, password, role, student_id="", department=""):
        return self.store.create_user(name, email, password, role, student_id, department)

    def sign_in(self, email, password):
        return self.store.authenticate(email, password)


class AuthMixin:
    def show_auth_screen(self):
        self.clear_screen()
        wrapper = tk.Frame(self.main_frame, bg="#eef2f6")
        wrapper.pack(fill="both", expand=True)
        card = tk.Frame(wrapper, bg="white", padx=24, pady=24)
        card.pack(expand=True, ipadx=18, ipady=12)
        if self.auth_mode == "signup":
            top_row = tk.Frame(card, bg="white")
            top_row.pack(fill="x")
            self.make_button(top_row, "Back", self.handle_auth_back).pack(anchor="w")
        title = "Create Account" if self.auth_mode == "signup" else "Sign In"
        subtitle = (
            "Create a student or professor account, then use classes and teams inside the professor workspace."
            if self.auth_mode == "signup"
            else "Sign in with the email and password you created in this app."
        )
        self.label(card, "Project Approval Tracker", 17, True, fg="#1f2933", pady=(14, 0))
        self.label(card, title, 14, True, fg="#102a43", pady=8)
        self.label(card, subtitle, fg="#52606d", wraplength=500, justify="left")
        self.auth_message = tk.Label(card, text="", font=("Segoe UI", 9), bg="white", fg="#c0392b")
        self.auth_message.pack(anchor="w", pady=(10, 0))
        self.name_entry = self.entry_field(card, "Full Name")
        self.email_entry = self.entry_field(card, "Email")
        self.password_entry = self.entry_field(card, "Password", show="*")
        self.password_entry.bind("<Return>", lambda _event: self.submit_auth())
        self.role_var = tk.StringVar(value="student")
        if self.auth_mode == "signup":
            self.label(card, "Role", bg="white", fg="#000000", pady=(12, 4))
            role_row = tk.Frame(card, bg="white")
            role_row.pack(anchor="w")
            tk.Radiobutton(role_row, text="Student", variable=self.role_var, value="student", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=(0, 14))
            tk.Radiobutton(role_row, text="Professor", variable=self.role_var, value="professor", bg="white", font=("Segoe UI", 10)).pack(side="left")
            self.student_id_entry = self.entry_field(card, "Student ID (optional)")
            self.department_entry = self.entry_field(card, "Department (optional)")
        primary_text = "Create Account" if self.auth_mode == "signup" else "Sign In"
        self.make_button(card, primary_text, self.submit_auth, primary=True).pack(fill="x", pady=(18, 10))
        switch_text = "Already have an account? Sign in" if self.auth_mode == "signup" else "Need an account? Create one"
        tk.Button(card, text=switch_text, command=self.toggle_auth_mode, font=("Segoe UI", 10), bg="white", fg="#334e68", relief="flat").pack(anchor="w")
        tk.Label(card, text="No demo accounts exist. Teachers can create classes and teams after signing in.", font=("Segoe UI", 9), bg="white", fg="#7b8794", wraplength=500, justify="left", pady=10).pack(anchor="w")
        self.name_entry.focus_set()
    def toggle_auth_mode(self):
        self.auth_mode = "signup" if self.auth_mode == "signin" else "signin"
        self.show_auth_screen()
    def handle_auth_back(self):
        if self.auth_mode == "signup":
            self.auth_mode = "signin"
            self.show_auth_screen()
            return
        self.destroy()
    def validate_email_password(self, email, password):
        if not email:
            raise ValueError("Email is required.")
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Enter a valid email address.")
        if not password:
            raise ValueError("Password is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
    def submit_auth(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        try:
            self.validate_email_password(email, password)
            if self.auth_mode == "signup":
                if not name:
                    raise ValueError("Full name is required.")
                student_id = self.student_id_entry.get().strip()
                department = self.department_entry.get().strip()
                self.current_user = self.auth_repo.create_account(name, email, password, self.role_var.get(), student_id, department)
                self.auth_message.config(text="")
                messagebox.showinfo("Account created", "Your account was created and you are now signed in.")
            else:
                self.current_user = self.auth_repo.sign_in(email, password)
                self.auth_message.config(text="")
        except ValueError as error:
            self.auth_message.config(text=str(error))
            return
        self.show_dashboard()
