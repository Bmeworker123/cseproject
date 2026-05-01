import tkinter as tk
from .ui import Button, Label, Card, EntryField, TextField, OptionField, StatCard, Header


class StudentRepository:
    def __init__(self, store):
        self.store = store

    def refresh_user(self, user_id):
        return self.store.find_user_by_id(user_id)

    def project_for(self, user):
        return self.store.get_project_for_student(user["email"])

    def save_project(self, user, title, notes, priority):
        return self.store.save_student_project(user, title, notes, priority)

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
        Header(self.main_frame, "Student Workspace", subtitle, self.log_out).pack(fill="x", pady=(0, 14))
        
        sidebar, content = self.build_shell()
        Label(sidebar, text="Student Menu", size=15, bold=True, bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.sidebar_button(sidebar, "Overview", lambda: self.set_student_page("overview"), self.student_page == "overview")
        self.sidebar_button(sidebar, "Project Form", lambda: self.set_student_page("project"), self.student_page == "project")
        if self.student_page == "overview":
            self.render_student_overview(content)
        else:
            self.render_student_project_form(content)

    def set_student_page(self, page):
        self.student_page = page
        self.show_student_dashboard()

    def render_student_overview(self, parent):
        user = self.student_repo.refresh_user(self.current_user["id"])
        self.current_user = user
        project = self.current_student_project()
        
        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Your student profile, class, team, and latest project summary.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        
        top = tk.Frame(parent, bg="white")
        top.pack(fill="x", pady=(10, 0))
        
        profile = Card(top, bg="#f7f9fb")
        profile.pack(side="left", fill="both", expand=True, padx=(0, 10))
        Label(profile, text="Student Profile", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        
        details = [
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Student ID: {user.get('student_id', 'N/A')}",
            f"Department: {user.get('department', 'N/A')}",
            f"Class: {self.student_repo.class_name(user.get('class_id')) or 'Not Assigned'}",
            f"Team: {self.student_repo.team_name(user.get('team_id')) or 'Not Assigned'}"
        ]
        for detail in details:
            Label(profile, text=detail, size=10, bg="#f7f9fb", fg="#334e68").pack(anchor="w", pady=2)
            
        summary = Card(top, bg="#eef8f1")
        summary.pack(side="left", fill="both", expand=True)
        Label(summary, text="Project Summary", size=13, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")
        
        if not project:
            Label(summary, text="No project yet. Open Project Form to create one.", size=10, bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=(6, 0))
        else:
            p_details = [
                f"Title: {project['title']}",
                f"Priority: {project.get('priority', 'N/A')}",
                f"Last Update: {project['last_updated']}"
            ]
            for line in p_details:
                Label(summary, text=line, size=10, bg="#eef8f1", fg="#1f7a45").pack(anchor="w", pady=2)
                
        box = Card(parent, bg="#fff7ed")
        box.pack(fill="x", pady=(18, 0))
        Label(box, text="Notifications", size=13, bold=True, bg="#fff7ed", fg="#9a3412").pack(anchor="w")
        
        if not user.get("notifications"):
            Label(box, text="No notifications yet.", size=10, bg="#fff7ed", fg="#b45309").pack(anchor="w", pady=(6, 0))
        else:
            for notification in user["notifications"]:
                Label(box, text=notification, size=10, bg="#fff7ed", fg="#7c2d12", wraplength=760, justify="left").pack(anchor="w", pady=2)

    def render_student_project_form(self, parent):
        project = self.current_student_project()
        Label(parent, text="Project Form", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Submit your project and keep the priority and notes updated.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        
        self.student_form_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.student_form_message.pack(anchor="w", pady=(4, 8))
        
        form = tk.Frame(parent, bg="white")
        form.pack(fill="x", pady=10)
        
        self.project_title_field = EntryField(form, "Project Title")
        self.project_title_field.pack(fill="x")
        
        self.project_notes_field = TextField(form, "Project Description / Notes", height=6)
        self.project_notes_field.pack(fill="x")
        
        row = tk.Frame(form, bg="white")
        row.pack(fill="x", pady=16)
        
        right = tk.Frame(row, bg="white")
        right.pack(side="left", fill="x", expand=True)
        self.priority_var = tk.StringVar(value="Medium")
        self.project_priority_field = OptionField(right, "Priority", self.priority_var, ["Low", "Medium", "High"])
        self.project_priority_field.pack(fill="x")
        
        button_row = tk.Frame(form, bg="white")
        button_row.pack(anchor="w", pady=(16, 0))
        Button(button_row, "Save Project", self.save_student_project, primary=True).pack(side="left")
        
        if project:
            self.project_title_field.insert(0, project["title"])
            self.project_notes_field.insert("1.0", project["notes"])
            self.priority_var.set(project.get("priority", "Medium"))

    def save_student_project(self):
        title = self.project_title_field.get().strip()
        notes = self.project_notes_field.get("1.0", "end").strip()
        priority = self.priority_var.get()
        
        if not title:
            self.student_form_message.config(text="Project title is required.", fg="#c0392b")
            return
            
        self.current_user = self.student_repo.refresh_user(self.current_user["id"])
        self.student_repo.save_project(self.current_user, title, notes, priority)
        self.student_form_message.config(text="Project saved successfully.", fg="#1f7a45")
