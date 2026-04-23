import os
import re
import sys
import tkinter as tk
from tkinter import messagebox

from .datastore import DataStore


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ProjectApprovalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        self.store = DataStore(base_dir)
        self.current_user = None
        self.auth_mode = "signin"

        self.selected_student_id = None
        self.selected_project_id = None
        self.selected_class_id = None
        self.selected_team_id = None

        self.student_page = "overview"
        self.professor_page = "overview"

        self.title("Student Project Tracker")
        self.geometry("1180x760")
        self.configure(bg="#eef2f6")
        self.resizable(False, False)

        self.main_frame = tk.Frame(self, bg="#eef2f6", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.show_auth_screen()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def make_button(self, parent, text, command, primary=False):
        bg = "#2f80ed" if primary else "white"
        fg = "white" if primary else "#334e68"
        relief = "flat" if primary else "solid"
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=relief,
            bd=1 if not primary else 0,
            padx=12,
            pady=8,
        )

    def render_stat_card(self, parent, title, value, note="", bg="#f7f9fb"):
        card = tk.Frame(parent, bg=bg, padx=14, pady=14)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=bg, fg="#52606d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 17, "bold"), bg=bg, fg="#102a43", pady=4).pack(anchor="w")
        if note:
            tk.Label(card, text=note, font=("Segoe UI", 9), bg=bg, fg="#7b8794", wraplength=220, justify="left").pack(anchor="w")

    def create_header(self, title, subtitle):
        header = tk.Frame(self.main_frame, bg="#eef2f6")
        header.pack(fill="x", pady=(0, 14))

        info = tk.Frame(header, bg="#eef2f6")
        info.pack(side="left")
        tk.Label(info, text=title, font=("Segoe UI", 18, "bold"), bg="#eef2f6", fg="#102a43").pack(anchor="w")
        tk.Label(info, text=subtitle, font=("Segoe UI", 10), bg="#eef2f6", fg="#52606d").pack(anchor="w")

        actions = tk.Frame(header, bg="#eef2f6")
        actions.pack(side="right")
        self.make_button(actions, "Back", self.log_out).pack(side="left", padx=(0, 8))
        self.make_button(actions, "Log Out", self.log_out).pack(side="left")

    def build_shell(self):
        shell = tk.Frame(self.main_frame, bg="#eef2f6")
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg="#16324f", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        content = tk.Frame(shell, bg="white", padx=18, pady=18)
        content.pack(side="left", fill="both", expand=True)
        return sidebar, content

    def sidebar_button(self, parent, text, command, active=False):
        bg = "#2f80ed" if active else "#16324f"
        self.make_button(parent, text, command, primary=active).pack(fill="x", padx=14, pady=6)
        if not active:
            parent.winfo_children()[-1].configure(bg="#16324f", fg="white", relief="flat", activebackground="#1d456b", activeforeground="white")

    def show_auth_screen(self):
        self.clear_screen()
        wrapper = tk.Frame(self.main_frame, bg="#eef2f6")
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(wrapper, bg="white", padx=24, pady=24)
        card.pack(expand=True, ipadx=18, ipady=12)

        top_row = tk.Frame(card, bg="white")
        top_row.pack(fill="x")
        self.make_button(top_row, "Back", self.handle_auth_back).pack(anchor="w")

        title = "Create Account" if self.auth_mode == "signup" else "Sign In"
        subtitle = (
            "Create a student or professor account, then use classes and teams inside the professor workspace."
            if self.auth_mode == "signup"
            else "Sign in with the email and password you created in this app."
        )

        tk.Label(card, text="Project Approval Tracker", font=("Segoe UI", 17, "bold"), bg="white", fg="#1f2933").pack(anchor="w", pady=(14, 0))
        tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), bg="white", fg="#102a43", pady=8).pack(anchor="w")
        tk.Label(card, text=subtitle, font=("Segoe UI", 10), bg="white", fg="#52606d", wraplength=500, justify="left").pack(anchor="w")

        self.auth_message = tk.Label(card, text="", font=("Segoe UI", 9), bg="white", fg="#c0392b")
        self.auth_message.pack(anchor="w", pady=(10, 0))

        tk.Label(card, text="Full Name", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(16, 4))
        self.name_entry = tk.Entry(card, font=("Segoe UI", 11))
        self.name_entry.pack(fill="x")

        tk.Label(card, text="Email", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
        self.email_entry = tk.Entry(card, font=("Segoe UI", 11))
        self.email_entry.pack(fill="x")

        tk.Label(card, text="Password", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
        self.password_entry = tk.Entry(card, show="*", font=("Segoe UI", 11))
        self.password_entry.pack(fill="x")
        self.password_entry.bind("<Return>", lambda _event: self.submit_auth())

        self.role_var = tk.StringVar(value="student")
        if self.auth_mode == "signup":
            tk.Label(card, text="Role", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
            role_row = tk.Frame(card, bg="white")
            role_row.pack(anchor="w")
            tk.Radiobutton(role_row, text="Student", variable=self.role_var, value="student", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=(0, 14))
            tk.Radiobutton(role_row, text="Professor", variable=self.role_var, value="professor", bg="white", font=("Segoe UI", 10)).pack(side="left")

            tk.Label(card, text="Student ID (optional)", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
            self.student_id_entry = tk.Entry(card, font=("Segoe UI", 11))
            self.student_id_entry.pack(fill="x")

            tk.Label(card, text="Department (optional)", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
            self.department_entry = tk.Entry(card, font=("Segoe UI", 11))
            self.department_entry.pack(fill="x")

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
                self.current_user = self.store.create_user(name, email, password, self.role_var.get(), student_id, department)
                self.auth_message.config(text="")
                messagebox.showinfo("Account created", "Your account was created and you are now signed in.")
            else:
                self.current_user = self.store.authenticate(email, password)
                self.auth_message.config(text="")
        except ValueError as error:
            self.auth_message.config(text=str(error))
            return
        self.show_dashboard()

    def log_out(self):
        self.current_user = None
        self.auth_mode = "signin"
        self.selected_student_id = None
        self.selected_project_id = None
        self.selected_class_id = None
        self.selected_team_id = None
        self.show_auth_screen()

    def show_dashboard(self):
        if self.current_user["role"] == "student":
            self.show_student_dashboard()
        else:
            self.show_professor_dashboard()

    def current_student_project(self):
        return self.store.get_project_for_student(self.current_user["email"])

    def show_student_dashboard(self):
        self.clear_screen()
        subtitle = f"Signed in as {self.current_user['name']} ({self.current_user['email']})"
        self.create_header("Student Workspace", subtitle)
        sidebar, content = self.build_shell()

        tk.Label(sidebar, text="Student Menu", font=("Segoe UI", 15, "bold"), bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.sidebar_button(sidebar, "Overview", lambda: self.set_student_page("overview"), self.student_page == "overview")
        self.sidebar_button(sidebar, "Project Form", lambda: self.set_student_page("project"), self.student_page == "project")
        self.sidebar_button(sidebar, "Status", lambda: self.set_student_page("status"), self.student_page == "status")

        if self.student_page == "overview":
            self.render_student_overview(content)
        elif self.student_page == "project":
            self.render_student_project_form(content)
        else:
            self.render_student_status(content)

    def set_student_page(self, page):
        self.student_page = page
        self.show_student_dashboard()

    def render_student_overview(self, parent):
        user = self.store.find_user_by_id(self.current_user["id"])
        self.current_user = user
        project = self.current_student_project()
        tk.Label(parent, text="Overview", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Your student profile, class, team, and latest project summary.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=(14, 18))
        self.render_stat_card(stats, "Account Status", user.get("status", "Active"))
        self.render_stat_card(stats, "Class", self.store.get_class_name(user.get("class_id")))
        self.render_stat_card(stats, "Team", self.store.get_team_name(user.get("team_id")))

        profile = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        profile.pack(fill="x")
        tk.Label(profile, text="Student Profile", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        details = [
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Student ID: {user.get('student_id') or 'Not added'}",
            f"Department: {user.get('department') or 'Not added'}",
            f"Class: {self.store.get_class_name(user.get('class_id'))}",
            f"Team: {self.store.get_team_name(user.get('team_id'))}",
            f"Teacher Notes: {user.get('notes') or 'No teacher notes yet'}",
        ]
        for detail in details:
            tk.Label(profile, text=detail, font=("Segoe UI", 10), bg="#f7f9fb", fg="#334e68", pady=2).pack(anchor="w")

        summary = tk.Frame(parent, bg="#eef8f1", padx=16, pady=16)
        summary.pack(fill="x", pady=(16, 0))
        tk.Label(summary, text="Project Summary", font=("Segoe UI", 13, "bold"), bg="#eef8f1", fg="#14532d").pack(anchor="w")
        if not project:
            tk.Label(summary, text="No project yet. Open Project Form to create one.", font=("Segoe UI", 10), bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=(6, 0))
        else:
            lines = [
                f"Title: {project['title']}",
                f"Status: {project['status']}",
                f"Stage: {project['stage']}",
                f"Official Progress: {project['progress']}%",
            ]
            if project.get("requested_progress") is not None:
                lines.append(f"Requested Progress: {project['requested_progress']}% waiting for professor confirmation")
            for line in lines:
                tk.Label(summary, text=line, font=("Segoe UI", 10), bg="#eef8f1", fg="#1f7a45", pady=2).pack(anchor="w")

        self.render_student_notifications(parent, project)

    def render_student_notifications(self, parent, project):
        box = tk.Frame(parent, bg="#fff7ed", padx=16, pady=16)
        box.pack(fill="x", pady=(16, 0))
        tk.Label(box, text="Notifications", font=("Segoe UI", 13, "bold"), bg="#fff7ed", fg="#9a3412").pack(anchor="w")

        if not project or not project.get("notifications"):
            tk.Label(box, text="No notifications yet.", font=("Segoe UI", 10), bg="#fff7ed", fg="#b45309").pack(anchor="w", pady=(6, 0))
            return

        for notification in project["notifications"][:5]:
            tk.Label(box, text=notification, font=("Segoe UI", 10), bg="#fff7ed", fg="#7c2d12", wraplength=760, justify="left", pady=2).pack(anchor="w")

    def render_student_project_form(self, parent):
        project = self.current_student_project()
        tk.Label(parent, text="Project Form", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Submit your project and keep stage, priority, and progress updated.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        self.student_form_message = tk.Label(parent, text="", font=("Segoe UI", 10), bg="white", fg="#1f7a45")
        self.student_form_message.pack(anchor="w", pady=(4, 10))

        form = tk.Frame(parent, bg="white")
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Project Title", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(6, 4))
        self.project_title_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.project_title_entry.pack(fill="x")

        tk.Label(form, text="Project Description / Notes", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
        self.project_notes_text = tk.Text(form, height=8, font=("Segoe UI", 10))
        self.project_notes_text.pack(fill="x")

        row = tk.Frame(form, bg="white")
        row.pack(fill="x", pady=(12, 0))

        left = tk.Frame(row, bg="white")
        left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(left, text="Project Stage", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.stage_var = tk.StringVar(value="Proposal")
        tk.OptionMenu(left, self.stage_var, "Proposal", "Research", "Prototype", "Testing", "Final Review").pack(fill="x")

        right = tk.Frame(row, bg="white")
        right.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(right, text="Priority", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.priority_var = tk.StringVar(value="Medium")
        tk.OptionMenu(right, self.priority_var, "Low", "Medium", "High").pack(fill="x")

        tk.Label(form, text="Progress", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(12, 4))
        self.progress_scale = tk.Scale(form, from_=0, to=100, orient="horizontal", bg="white", highlightthickness=0, length=360)
        self.progress_scale.pack(anchor="w")

        button_row = tk.Frame(form, bg="white")
        button_row.pack(anchor="w", pady=(16, 0))
        self.make_button(button_row, "Save Project", self.save_student_project, primary=True).pack(side="left", padx=(0, 8))
        self.make_button(button_row, "Go To Status", lambda: self.set_student_page("status")).pack(side="left")

        if project:
            self.project_title_entry.insert(0, project["title"])
            self.project_notes_text.insert("1.0", project["notes"])
            self.stage_var.set(project.get("stage", "Proposal"))
            self.priority_var.set(project.get("priority", "Medium"))
            self.progress_scale.set(project.get("progress", 0))

    def render_student_status(self, parent):
        project = self.current_student_project()
        tk.Label(parent, text="Project Status", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="See the latest teacher feedback, class, and team context.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        if not project:
            empty = tk.Frame(parent, bg="#fff7ed", padx=18, pady=18)
            empty.pack(fill="x", pady=(12, 0))
            tk.Label(empty, text="No project submitted yet.", font=("Segoe UI", 13, "bold"), bg="#fff7ed", fg="#9a3412").pack(anchor="w")
            tk.Label(empty, text="Create your project in the Project Form page first.", font=("Segoe UI", 10), bg="#fff7ed", fg="#b45309").pack(anchor="w", pady=(6, 0))
            return

        card = tk.Frame(parent, bg="#f7f9fb", padx=18, pady=18)
        card.pack(fill="x", pady=(14, 0))
        lines = [
            f"Title: {project['title']}",
            f"Status: {project['status']}",
            f"Stage: {project['stage']}",
            f"Priority: {project['priority']}",
            f"Official Progress: {project['progress']}%",
            f"Requested Progress: {project['requested_progress']}%" if project.get("requested_progress") is not None else "Requested Progress: None",
            f"Progress Request Status: {project.get('progress_request_status', 'None')}",
            f"Class: {self.store.get_class_name(project.get('class_id'))}",
            f"Team: {self.store.get_team_name(project.get('team_id'))}",
            f"Meeting Status: {project.get('meeting_status', 'Not Scheduled')}",
            f"Professor Notes: {project['professor_notes']}",
        ]
        for line in lines:
            tk.Label(card, text=line, font=("Segoe UI", 10), bg="#f7f9fb", fg="#334e68", pady=2, justify="left").pack(anchor="w")

        self.render_student_notifications(parent, project)

    def save_student_project(self):
        title = self.project_title_entry.get().strip()
        notes = self.project_notes_text.get("1.0", "end").strip()
        progress = self.progress_scale.get()
        stage = self.stage_var.get()
        priority = self.priority_var.get()
        if not title:
            self.student_form_message.config(text="Project title is required.", fg="#c0392b")
            return
        self.current_user = self.store.find_user_by_id(self.current_user["id"])
        project = self.store.save_student_project(self.current_user, title, notes, progress, stage, priority)
        if project.get("requested_progress") is not None:
            message = f"Project saved. Progress change to {project['requested_progress']}% is waiting for professor approval."
        else:
            message = f"Project saved with status: {project['status']}"
        self.student_form_message.config(text=message, fg="#1f7a45")

    def show_professor_dashboard(self):
        self.clear_screen()
        self.current_user = self.store.find_user_by_id(self.current_user["id"])
        subtitle = f"Signed in as {self.current_user['name']} ({self.current_user['email']})"
        self.create_header("Professor Workspace", subtitle)
        sidebar, content = self.build_shell()

        tk.Label(sidebar, text="Professor Menu", font=("Segoe UI", 15, "bold"), bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.sidebar_button(sidebar, "Overview", lambda: self.set_professor_page("overview"), self.professor_page == "overview")
        self.sidebar_button(sidebar, "Students", lambda: self.set_professor_page("students"), self.professor_page == "students")
        self.sidebar_button(sidebar, "Classes", lambda: self.set_professor_page("classes"), self.professor_page == "classes")
        self.sidebar_button(sidebar, "Teams", lambda: self.set_professor_page("teams"), self.professor_page == "teams")
        self.sidebar_button(sidebar, "Projects", lambda: self.set_professor_page("projects"), self.professor_page == "projects")

        if self.professor_page == "overview":
            self.render_professor_overview(content)
        elif self.professor_page == "students":
            self.render_professor_students(content)
        elif self.professor_page == "classes":
            self.render_professor_classes(content)
        elif self.professor_page == "teams":
            self.render_professor_teams(content)
        else:
            self.render_professor_projects(content)

    def set_professor_page(self, page):
        self.professor_page = page
        self.show_professor_dashboard()

    def teacher_classes(self):
        return self.store.list_classes_for_teacher(self.current_user["email"])

    def render_professor_overview(self, parent):
        students = self.store.list_students()
        projects = self.store.list_projects()
        classes = self.teacher_classes()
        teams = []
        for class_record in classes:
            teams.extend(self.store.list_teams_for_class(class_record["id"]))
        pending = [
            project
            for project in projects
            if project.get("status") in {"Pending Approval", "Resubmitted"}
            or project.get("progress_request_status") == "Pending"
        ]

        tk.Label(parent, text="Overview", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Quick view of student growth, class setup, and team structure.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=(14, 18))
        self.render_stat_card(stats, "Students", str(len(students)), "All student accounts.")
        self.render_stat_card(stats, "Classes", str(len(classes)), "Classes owned by you.")
        self.render_stat_card(stats, "Teams", str(len(teams)), "Teams across your classes.")
        self.render_stat_card(stats, "Pending Reviews", str(len(pending)), "Projects or progress requests needing action.")

        recent_card = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        recent_card.pack(fill="x", pady=(0, 14))
        tk.Label(recent_card, text="New Students", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        recent = self.store.list_recent_students()
        if not recent:
            tk.Label(recent_card, text="No student accounts yet.", font=("Segoe UI", 10), bg="#f7f9fb", fg="#52606d").pack(anchor="w", pady=(6, 0))
        else:
            for student in recent:
                line = f"{student['name']} | {student['email']} | Class: {self.store.get_class_name(student.get('class_id'))} | Team: {self.store.get_team_name(student.get('team_id'))}"
                tk.Label(recent_card, text=line, font=("Segoe UI", 10), bg="#f7f9fb", fg="#334e68", pady=2).pack(anchor="w")

        actions = tk.Frame(parent, bg="#eef8f1", padx=16, pady=16)
        actions.pack(fill="x")
        tk.Label(actions, text="Teacher Actions", font=("Segoe UI", 13, "bold"), bg="#eef8f1", fg="#14532d").pack(anchor="w")
        tk.Label(actions, text="Use Students to assign classes, Classes to create offerings, Teams to group students, and Projects to review submissions.", font=("Segoe UI", 10), bg="#eef8f1", fg="#1f7a45", wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))
        row = tk.Frame(actions, bg="#eef8f1")
        row.pack(anchor="w")
        self.make_button(row, "Open Classes", lambda: self.set_professor_page("classes"), primary=True).pack(side="left", padx=(0, 8))
        self.make_button(row, "Open Teams", lambda: self.set_professor_page("teams")).pack(side="left", padx=(0, 8))
        self.make_button(row, "Open Projects", lambda: self.set_professor_page("projects")).pack(side="left")

    def render_professor_students(self, parent):
        tk.Label(parent, text="Student Management", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Inspect students, leave notes, set status, and assign them to classes and teams.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        self.professor_student_message = tk.Label(parent, text="", font=("Segoe UI", 10), bg="white", fg="#1f7a45")
        self.professor_student_message.pack(anchor="w", pady=(4, 8))

        body = tk.Frame(parent, bg="white")
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="#f7f9fb", padx=12, pady=12, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="Students", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        self.student_listbox = tk.Listbox(left, font=("Segoe UI", 10), height=26)
        self.student_listbox.pack(fill="both", expand=True, pady=(8, 0))
        self.student_listbox.bind("<<ListboxSelect>>", self.load_selected_student)

        right = tk.Frame(body, bg="white", padx=16, pady=8)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Student Details", font=("Segoe UI", 13, "bold"), bg="white", fg="#102a43").pack(anchor="w")
        self.student_detail_label = tk.Label(right, text="Select a student to manage their record.", font=("Segoe UI", 10), bg="white", fg="#334e68", justify="left")
        self.student_detail_label.pack(anchor="w", pady=(8, 10))

        tk.Label(right, text="Teacher Notes", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.student_notes_text = tk.Text(right, height=4, font=("Segoe UI", 10))
        self.student_notes_text.pack(fill="x", pady=(4, 10))

        control_grid = tk.Frame(right, bg="white")
        control_grid.pack(fill="x", pady=(0, 10))

        status_box = tk.Frame(control_grid, bg="white")
        status_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(status_box, text="Account Status", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.student_status_var = tk.StringVar(value="Active")
        self.student_status_menu = tk.OptionMenu(status_box, self.student_status_var, "Active", "Needs Meeting", "Archived")
        self.student_status_menu.pack(fill="x", pady=(4, 0))

        class_box = tk.Frame(control_grid, bg="white")
        class_box.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(class_box, text="Assign Class", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.assign_class_var = tk.StringVar(value="Not Assigned")
        self.assign_class_menu = tk.OptionMenu(class_box, self.assign_class_var, "Not Assigned")
        self.assign_class_menu.pack(fill="x", pady=(4, 0))

        team_box = tk.Frame(right, bg="white")
        team_box.pack(fill="x", pady=(0, 12))
        tk.Label(team_box, text="Assign Team", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.assign_team_var = tk.StringVar(value="Not Assigned")
        self.assign_team_menu = tk.OptionMenu(team_box, self.assign_team_var, "Not Assigned")
        self.assign_team_menu.pack(fill="x", pady=(4, 0))

        row = tk.Frame(right, bg="white")
        row.pack(fill="x")
        self.make_button(row, "Save Student Changes", self.save_student_changes, primary=True).pack(side="left", padx=(0, 8))
        self.make_button(row, "Delete Student", self.delete_selected_student).pack(side="left", padx=(0, 8))
        self.make_button(row, "Refresh List", self.show_professor_dashboard).pack(side="left")
        self.refresh_student_list()

    def refresh_student_list(self):
        students = self.store.list_students()
        students.sort(key=lambda user: user.get("created_at", ""), reverse=True)
        self.student_records = students
        self.student_listbox.delete(0, tk.END)
        for student in students:
            label = f"{student['name']} | {student.get('status', 'Active')} | {self.store.get_class_name(student.get('class_id'))}"
            self.student_listbox.insert(tk.END, label)

    def _set_option_menu_values(self, menu_widget, variable, values):
        menu = menu_widget["menu"]
        menu.delete(0, "end")
        for value in values:
            menu.add_command(label=value, command=lambda current=value: variable.set(current))
        if values:
            variable.set(values[0])

    def load_selected_student(self, _event=None):
        selection = self.student_listbox.curselection()
        if not selection:
            return
        student = self.student_records[selection[0]]
        self.selected_student_id = student["id"]
        project = self.store.get_project_for_student(student["email"])

        details = [
            f"Name: {student['name']}",
            f"Email: {student['email']}",
            f"Student ID: {student.get('student_id') or 'Not added'}",
            f"Department: {student.get('department') or 'Not added'}",
            f"Status: {student.get('status', 'Active')}",
            f"Class: {self.store.get_class_name(student.get('class_id'))}",
            f"Team: {self.store.get_team_name(student.get('team_id'))}",
            f"Project: {project['title'] if project else 'No project yet'}",
        ]
        self.student_detail_label.config(text="\n".join(details))
        self.student_notes_text.delete("1.0", "end")
        self.student_notes_text.insert("1.0", student.get("notes", ""))
        self.student_status_var.set(student.get("status", "Active"))

        teacher_classes = self.teacher_classes()
        class_options = ["Not Assigned"] + [f"{item['id']} - {item['name']} ({item['term']})" for item in teacher_classes]
        self._set_option_menu_values(self.assign_class_menu, self.assign_class_var, class_options)
        current_class = "Not Assigned"
        if student.get("class_id"):
            current_class_record = self.store.find_class_by_id(student["class_id"])
            if current_class_record:
                current_class = f"{student['class_id']} - {current_class_record['name']} ({current_class_record['term']})"
        self.assign_class_var.set(current_class)

        team_options = ["Not Assigned"]
        if student.get("class_id"):
            team_options.extend([f"{item['id']} - {item['name']}" for item in self.store.list_teams_for_class(student["class_id"])])
        self._set_option_menu_values(self.assign_team_menu, self.assign_team_var, team_options)
        current_team = "Not Assigned"
        if student.get("team_id"):
            team = self.store.find_team_by_id(student["team_id"])
            if team:
                current_team = f"{team['id']} - {team['name']}"
        self.assign_team_var.set(current_team)

    def save_student_changes(self):
        if not self.selected_student_id:
            self.professor_student_message.config(text="Select a student first.", fg="#c0392b")
            return

        notes = self.student_notes_text.get("1.0", "end").strip()
        status = self.student_status_var.get()
        self.store.update_user(self.selected_student_id, {"notes": notes, "status": status})

        class_value = self.assign_class_var.get()
        class_id = None if class_value == "Not Assigned" else int(class_value.split(" - ")[0])
        self.store.assign_student_to_class(self.selected_student_id, class_id)

        team_value = self.assign_team_var.get()
        team_id = None if team_value == "Not Assigned" else int(team_value.split(" - ")[0])
        if team_id is not None:
            self.store.assign_student_to_team(self.selected_student_id, team_id)

        self.professor_student_message.config(text="Student record updated.", fg="#1f7a45")
        self.refresh_student_list()

    def delete_selected_student(self):
        if not self.selected_student_id:
            self.professor_student_message.config(text="Select a student first.", fg="#c0392b")
            return

        student = self.store.find_user_by_id(self.selected_student_id)
        if not student:
            self.professor_student_message.config(text="Student not found.", fg="#c0392b")
            return

        confirmed = messagebox.askyesno(
            "Delete Student",
            f"Delete {student['name']} and remove their project and team assignments?",
        )
        if not confirmed:
            return

        self.store.delete_student(self.selected_student_id)
        self.selected_student_id = None
        self.student_detail_label.config(text="Student deleted. Select another student to manage their record.")
        self.student_notes_text.delete("1.0", "end")
        self.student_status_var.set("Active")
        self.assign_class_var.set("Not Assigned")
        self.assign_team_var.set("Not Assigned")
        self.professor_student_message.config(text="Student deleted.", fg="#1f7a45")
        self.refresh_student_list()

    def render_professor_classes(self, parent):
        tk.Label(parent, text="Class Management", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Create classes and keep track of how many students belong to each one.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        self.class_message = tk.Label(parent, text="", font=("Segoe UI", 10), bg="white", fg="#1f7a45")
        self.class_message.pack(anchor="w", pady=(4, 10))

        form = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        form.pack(fill="x", pady=(0, 16))
        tk.Label(form, text="Create Class", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        tk.Label(form, text="Class Name", font=("Segoe UI", 10), bg="#f7f9fb").pack(anchor="w", pady=(8, 4))
        self.class_name_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.class_name_entry.pack(fill="x")
        tk.Label(form, text="Term", font=("Segoe UI", 10), bg="#f7f9fb").pack(anchor="w", pady=(10, 4))
        self.class_term_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.class_term_entry.pack(fill="x")
        self.make_button(form, "Create Class", self.create_class, primary=True).pack(anchor="w", pady=(14, 0))

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        tk.Label(list_frame, text="Your Classes", font=("Segoe UI", 13, "bold"), bg="white", fg="#102a43").pack(anchor="w")

        classes = self.teacher_classes()
        if not classes:
            tk.Label(list_frame, text="No classes created yet.", font=("Segoe UI", 10), bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            return

        self.class_records = classes
        self.class_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), height=8)
        self.class_listbox.pack(fill="x", pady=(8, 8))
        for class_record in classes:
            count = len([student for student in self.store.list_students() if student.get("class_id") == class_record["id"]])
            line = f"{class_record['name']} ({class_record['term']}) | Students: {count} | Created: {class_record['created_at']}"
            self.class_listbox.insert(tk.END, line)

        self.make_button(list_frame, "Delete Selected Class", self.delete_selected_class).pack(anchor="w", pady=(4, 0))

    def create_class(self):
        name = self.class_name_entry.get().strip()
        term = self.class_term_entry.get().strip()
        if not name or not term:
            self.class_message.config(text="Class name and term are required.", fg="#c0392b")
            return
        self.store.create_class(self.current_user, name, term)
        self.class_message.config(text="Class created.", fg="#1f7a45")
        self.show_professor_dashboard()

    def delete_selected_class(self):
        if not hasattr(self, "class_listbox") or not self.class_listbox.curselection():
            self.class_message.config(text="Select a class first.", fg="#c0392b")
            return

        class_record = self.class_records[self.class_listbox.curselection()[0]]
        confirmed = messagebox.askyesno(
            "Delete Class",
            f"Delete {class_record['name']} and remove its teams and assignments?",
        )
        if not confirmed:
            return

        self.store.delete_class(class_record["id"])
        self.class_message.config(text="Class deleted.", fg="#1f7a45")
        self.show_professor_dashboard()

    def render_professor_teams(self, parent):
        tk.Label(parent, text="Team Management", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Create teams inside a class, then assign students to them from the Students page.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        self.team_message = tk.Label(parent, text="", font=("Segoe UI", 10), bg="white", fg="#1f7a45")
        self.team_message.pack(anchor="w", pady=(4, 10))

        teacher_classes = self.teacher_classes()
        form = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        form.pack(fill="x", pady=(0, 16))
        tk.Label(form, text="Create Team", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        tk.Label(form, text="Class", font=("Segoe UI", 10), bg="#f7f9fb").pack(anchor="w", pady=(8, 4))
        self.team_class_var = tk.StringVar(value="No Classes")
        class_values = ["No Classes"] if not teacher_classes else [f"{item['id']} - {item['name']} ({item['term']})" for item in teacher_classes]
        self.team_class_menu = tk.OptionMenu(form, self.team_class_var, *class_values)
        self.team_class_menu.pack(anchor="w")

        tk.Label(form, text="Team Name", font=("Segoe UI", 10), bg="#f7f9fb").pack(anchor="w", pady=(10, 4))
        self.team_name_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.team_name_entry.pack(fill="x")
        self.make_button(form, "Create Team", self.create_team, primary=True).pack(anchor="w", pady=(14, 0))

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        tk.Label(list_frame, text="Teams", font=("Segoe UI", 13, "bold"), bg="white", fg="#102a43").pack(anchor="w")

        if not teacher_classes:
            tk.Label(list_frame, text="Create a class first, then add teams.", font=("Segoe UI", 10), bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            return

        self.team_records = []
        self.team_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), height=10)
        self.team_listbox.pack(fill="x", pady=(8, 8))
        any_team = False
        for class_record in teacher_classes:
            teams = self.store.list_teams_for_class(class_record["id"])
            if not teams:
                continue
            any_team = True
            for team in teams:
                members = [self.store.find_user_by_id(member_id)["name"] for member_id in team.get("member_ids", []) if self.store.find_user_by_id(member_id)]
                label = ", ".join(members) if members else "No members yet"
                self.team_records.append(team)
                self.team_listbox.insert(tk.END, f"{class_record['name']} ({class_record['term']}) | {team['name']} | Members: {label}")

        if not any_team:
            tk.Label(list_frame, text="No teams created yet.", font=("Segoe UI", 10), bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            self.team_listbox.destroy()
            return

        self.make_button(list_frame, "Delete Selected Team", self.delete_selected_team).pack(anchor="w", pady=(4, 0))

    def create_team(self):
        class_value = self.team_class_var.get()
        team_name = self.team_name_entry.get().strip()
        if class_value == "No Classes" or not team_name:
            self.team_message.config(text="Choose a class and enter a team name.", fg="#c0392b")
            return
        class_id = int(class_value.split(" - ")[0])
        self.store.create_team(class_id, team_name)
        self.team_message.config(text="Team created.", fg="#1f7a45")
        self.show_professor_dashboard()

    def delete_selected_team(self):
        if not hasattr(self, "team_listbox") or not self.team_listbox.curselection():
            self.team_message.config(text="Select a team first.", fg="#c0392b")
            return

        team = self.team_records[self.team_listbox.curselection()[0]]
        confirmed = messagebox.askyesno(
            "Delete Team",
            f"Delete {team['name']} and remove students from this team?",
        )
        if not confirmed:
            return

        self.store.delete_team(team["id"])
        self.team_message.config(text="Team deleted.", fg="#1f7a45")
        self.show_professor_dashboard()

    def render_professor_projects(self, parent):
        tk.Label(parent, text="Project Management", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Review student projects, class/team placement, and approval status.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        self.professor_project_message = tk.Label(parent, text="", font=("Segoe UI", 10), bg="white", fg="#1f7a45")
        self.professor_project_message.pack(anchor="w", pady=(4, 10))

        body = tk.Frame(parent, bg="white")
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="#f7f9fb", padx=12, pady=12, width=370)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="Projects", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        self.project_listbox = tk.Listbox(left, font=("Segoe UI", 10), height=26)
        self.project_listbox.pack(fill="both", expand=True, pady=(8, 0))
        self.project_listbox.bind("<<ListboxSelect>>", self.load_selected_project)

        right = tk.Frame(body, bg="white", padx=16, pady=8)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Project Details", font=("Segoe UI", 13, "bold"), bg="white", fg="#102a43").pack(anchor="w")
        self.project_detail_label = tk.Label(right, text="Select a project to review it.", font=("Segoe UI", 10), bg="white", fg="#334e68", justify="left")
        self.project_detail_label.pack(anchor="w", pady=(6, 8))

        progress_box = tk.Frame(right, bg="#eef8f1", padx=12, pady=10)
        progress_box.pack(fill="x", pady=(0, 10))
        tk.Label(progress_box, text="Progress Approval", font=("Segoe UI", 12, "bold"), bg="#eef8f1", fg="#14532d").pack(anchor="w")

        progress_row = tk.Frame(progress_box, bg="#eef8f1")
        progress_row.pack(fill="x", pady=(6, 8))
        progress_left = tk.Frame(progress_row, bg="#eef8f1")
        progress_left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(progress_left, text="Professor Progress", font=("Segoe UI", 10), bg="#eef8f1").pack(anchor="w")
        self.professor_progress_scale = tk.Scale(progress_left, from_=0, to=100, orient="horizontal", bg="#eef8f1", highlightthickness=0, length=250)
        self.professor_progress_scale.pack(anchor="w")

        progress_right = tk.Frame(progress_row, bg="#eef8f1")
        progress_right.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(progress_right, text="Progress Requested", font=("Segoe UI", 10), bg="#eef8f1").pack(anchor="w")
        self.progress_request_label = tk.Label(progress_right, text="No project selected.", font=("Segoe UI", 10), bg="#eef8f1", fg="#334e68", justify="left")
        self.progress_request_label.pack(anchor="w", pady=(8, 0))

        progress_actions = tk.Frame(progress_box, bg="#eef8f1")
        progress_actions.pack(anchor="w")
        self.make_button(progress_actions, "Approve Progress", self.approve_progress_request, primary=True).pack(side="left", padx=(0, 8))
        self.make_button(progress_actions, "Reject Progress", self.reject_progress_request).pack(side="left", padx=(0, 8))
        self.make_button(progress_actions, "Save Professor Progress", self.save_professor_progress).pack(side="left")

        row = tk.Frame(right, bg="white")
        row.pack(fill="x", pady=(0, 8))
        left_controls = tk.Frame(row, bg="white")
        left_controls.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(left_controls, text="Meeting Status", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.meeting_status_var = tk.StringVar(value="Not Scheduled")
        tk.OptionMenu(left_controls, self.meeting_status_var, "Not Scheduled", "Meeting Scheduled", "Meeting Completed").pack(anchor="w")

        right_controls = tk.Frame(row, bg="white")
        right_controls.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(right_controls, text="Stage", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.teacher_stage_var = tk.StringVar(value="Proposal")
        tk.OptionMenu(right_controls, self.teacher_stage_var, "Proposal", "Research", "Prototype", "Testing", "Final Review").pack(anchor="w")

        tk.Label(right, text="Professor Notes", font=("Segoe UI", 10), bg="white").pack(anchor="w")
        self.professor_notes_text = tk.Text(right, height=3, font=("Segoe UI", 10))
        self.professor_notes_text.pack(fill="x", pady=(4, 8))

        action_row = tk.Frame(right, bg="white")
        action_row.pack(anchor="w")
        self.make_button(action_row, "Approve", lambda: self.update_project_status("Approved"), primary=True).pack(side="left", padx=(0, 8))
        self.make_button(action_row, "Request Changes", lambda: self.update_project_status("Changes Requested")).pack(side="left", padx=(0, 8))
        self.make_button(action_row, "Save Notes Only", lambda: self.update_project_status(None)).pack(side="left")
        self.refresh_project_list()

    def refresh_project_list(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        all_projects = self.store.list_projects()
        self.project_records = [project for project in all_projects if not teacher_class_ids or project.get("class_id") in teacher_class_ids or project.get("class_id") is None]
        self.project_records.sort(key=lambda project: project.get("last_updated", ""), reverse=True)
        self.project_listbox.delete(0, tk.END)
        for project in self.project_records:
            label = f"{project['student_name']} | {project['title']} | {project['status']} | {project['progress']}%"
            self.project_listbox.insert(tk.END, label)

    def load_selected_project(self, _event=None):
        selection = self.project_listbox.curselection()
        if not selection:
            return
        project = self.project_records[selection[0]]
        self.selected_project_id = project["id"]
        details = [
            f"Student: {project['student_name']}",
            f"Email: {project['student_email']}",
            f"Class: {self.store.get_class_name(project.get('class_id'))}",
            f"Team: {self.store.get_team_name(project.get('team_id'))}",
            f"Title: {project['title']}",
            f"Status: {project['status']}",
            f"Stage: {project.get('stage', 'Proposal')}",
            f"Official Progress: {project['progress']}%",
            f"Requested Progress: {project['requested_progress']}%" if project.get("requested_progress") is not None else "Requested Progress: None",
            f"Progress Request Status: {project.get('progress_request_status', 'None')}",
            f"Meeting Status: {project.get('meeting_status', 'Not Scheduled')}",
        ]
        self.project_detail_label.config(text="\n".join(details))
        self.professor_notes_text.delete("1.0", "end")
        self.professor_notes_text.insert("1.0", project.get("professor_notes", ""))
        self.meeting_status_var.set(project.get("meeting_status", "Not Scheduled"))
        self.teacher_stage_var.set(project.get("stage", "Proposal"))
        self.professor_progress_scale.set(project.get("progress", 0))
        if project.get("requested_progress") is None:
            self.progress_request_label.config(text="No pending progress request.")
        else:
            self.progress_request_label.config(text=f"Student requested {project['requested_progress']}%.")

    def update_project_status(self, status):
        if not self.selected_project_id:
            self.professor_project_message.config(text="Select a project first.", fg="#c0392b")
            return
        updates = {
            "professor_notes": self.professor_notes_text.get("1.0", "end").strip() or "No notes provided.",
            "meeting_status": self.meeting_status_var.get(),
            "stage": self.teacher_stage_var.get(),
        }
        if status:
            updates["status"] = status
        notification = None
        if status == "Approved":
            notification = "Professor approved your project."
        elif status == "Changes Requested":
            notification = "Professor requested changes to your project. Please review the professor notes."
        project = self.store.update_project(self.selected_project_id, updates, notification=notification)
        text = f"Project updated: {project['title']} is now {project['status']}." if status else "Project notes and stage updated."
        self.professor_project_message.config(text=text, fg="#1f7a45")
        self.refresh_project_list()

    def approve_progress_request(self):
        if not self.selected_project_id:
            self.professor_project_message.config(text="Select a project first.", fg="#c0392b")
            return
        try:
            project = self.store.approve_progress_request(self.selected_project_id)
            self.add_professor_note_notification(project["id"], "Professor note about approved progress")
        except ValueError as error:
            self.professor_project_message.config(text=str(error), fg="#c0392b")
            return
        self.professor_project_message.config(text=f"Progress approved. Official progress is now {project['progress']}%.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def reject_progress_request(self):
        if not self.selected_project_id:
            self.professor_project_message.config(text="Select a project first.", fg="#c0392b")
            return
        try:
            project = self.store.reject_progress_request(self.selected_project_id)
            self.add_professor_note_notification(project["id"], "Professor note about rejected progress")
        except ValueError as error:
            self.professor_project_message.config(text=str(error), fg="#c0392b")
            return
        self.professor_project_message.config(text="Progress request rejected.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def save_professor_progress(self):
        if not self.selected_project_id:
            self.professor_project_message.config(text="Select a project first.", fg="#c0392b")
            return
        progress = self.professor_progress_scale.get()
        current_project = self.store._find_project_or_raise(self.selected_project_id)
        updates = {
            "progress": progress,
            "requested_progress": None,
            "progress_request_status": "Professor Updated",
        }
        if current_project.get("status") in {"Pending Approval", "Resubmitted"}:
            updates["status"] = "Reviewed"

        project = self.store.update_project(
            self.selected_project_id,
            updates,
            notification=self.progress_notification_with_note(progress),
        )
        self.professor_project_message.config(text=f"Professor set official progress to {project['progress']}%.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def progress_notification_with_note(self, progress):
        note = self.professor_notes_text.get("1.0", "end").strip()
        message = f"Professor changed your official progress to {progress}%."
        if note:
            message += f" Note: {note}"
        return message

    def add_professor_note_notification(self, project_id, prefix):
        note = self.professor_notes_text.get("1.0", "end").strip()
        if not note:
            return
        self.store.update_project(project_id, {}, notification=f"{prefix}: {note}")

    def reload_selected_project_details(self):
        if not self.selected_project_id:
            return
        for index, project in enumerate(self.project_records):
            if project["id"] == self.selected_project_id:
                self.project_listbox.selection_clear(0, tk.END)
                self.project_listbox.selection_set(index)
                self.load_selected_project()
                return
