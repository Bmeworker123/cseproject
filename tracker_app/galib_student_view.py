import tkinter as tk


class StudentRepository:
    def __init__(self, store):
        self.store = store

    def refresh_user(self, user_id):
        return self.store.find_user_by_id(user_id)

    def project_for(self, user):
        return self.store.get_project_for_student(user["email"])

    def save_project(self, user, title, notes, progress, stage, priority):
        return self.store.save_student_project(user, title, notes, progress, stage, priority)

    def class_name(self, class_id):
        return self.store.get_class_name(class_id)

    def team_name(self, team_id):
        return self.store.get_team_name(team_id)


class StudentMixin:
    def current_student_project(self):
        return self.student_repo.project_for(self.current_user)
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
        user = self.student_repo.refresh_user(self.current_user["id"])
        self.current_user = user
        project = self.current_student_project()
        tk.Label(parent, text="Overview", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2933").pack(anchor="w")
        tk.Label(parent, text="Your student profile, class, team, and latest project summary.", font=("Segoe UI", 10), bg="white", fg="#52606d", pady=6).pack(anchor="w")
        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=(14, 18))
        self.render_stat_card(stats, "Account Status", user.get("status", "Active"))
        self.render_stat_card(stats, "Class", self.student_repo.class_name(user.get("class_id")))
        self.render_stat_card(stats, "Team", self.student_repo.team_name(user.get("team_id")))
        profile = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        profile.pack(fill="x")
        tk.Label(profile, text="Student Profile", font=("Segoe UI", 13, "bold"), bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        details = [
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Student ID: {user.get('student_id') or 'Not added'}",
            f"Department: {user.get('department') or 'Not added'}",
            f"Class: {self.student_repo.class_name(user.get('class_id'))}",
            f"Team: {self.student_repo.team_name(user.get('team_id'))}",
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
            f"Class: {self.student_repo.class_name(project.get('class_id'))}",
            f"Team: {self.student_repo.team_name(project.get('team_id'))}",
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
        self.current_user = self.student_repo.refresh_user(self.current_user["id"])
        project = self.student_repo.save_project(self.current_user, title, notes, progress, stage, priority)
        if project.get("requested_progress") is not None:
            message = f"Project saved. Progress change to {project['requested_progress']}% is waiting for professor approval."
        else:
            message = f"Project saved with status: {project['status']}"
        self.student_form_message.config(text=message, fg="#1f7a45")
