import tkinter as tk
from tkinter import messagebox

from ....ui import Button, Label, Card, EntryField, TextField, OptionField, StatCard, Header



class ProfessorOverviewPage(_ProfessorPageBase):
    def render(self, parent):
        students = self.app.professor_repo.list_students()
        projects = self.app.professor_repo.list_projects()
        classes = self.teacher_classes()

        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Quick view of student growth, class setup, and team structure.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        StatCard(stats, "Total Students", str(len(students)), "Enrolled in project tracker.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Active Projects", str(len(projects)), "Submitted for review.").pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Your Classes", str(len(classes)), "Created by you.").pack(side="left", fill="both", expand=True, padx=6)

        recent_card = Card(parent, bg="#f7f9fb")
        recent_card.pack(fill="x", pady=14)
        Label(recent_card, text="New Students", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        new_students = sorted(students, key=lambda user: user.get("created_at", ""), reverse=True)[:5]
        if not new_students:
            Label(recent_card, text="No student accounts yet.", size=10, bg="#f7f9fb", fg="#52606d").pack(anchor="w", pady=(6, 0))
        else:
            for user in new_students:
                line = f"{user['name']} ({user['email']}) | Joined: {user.get('created_at', 'N/A')}"
                Label(recent_card, text=line, size=10, bg="#f7f9fb", fg="#334e68").pack(anchor="w", pady=2)

        actions = Card(parent, bg="#eef8f1")
        actions.pack(fill="x")
        Label(actions, text="Teacher Actions", size=13, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")
        Label(actions, text="Use Students to assign classes, Classes to create offerings, Teams to group students, and Projects to review submissions.", size=10, bg="#eef8f1", fg="#1f7a45", wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))

        row = tk.Frame(actions, bg="#eef8f1")
        row.pack(anchor="w")
        Button(row, "Open Classes", lambda: self.dashboard.set_page("classes"), primary=True).pack(side="left", padx=(0, 8))
        Button(row, "Open Teams", lambda: self.dashboard.set_page("teams")).pack(side="left", padx=(0, 8))
        Button(row, "Open Projects", lambda: self.dashboard.set_page("projects")).pack(side="left")

class ProfessorClassesPage(_ProfessorPageBase):
    def render(self, parent):
        Label(parent, text="Class Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Create classes and keep track of how many students belong to each one.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.class_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.class_message.pack(anchor="w", pady=(4, 8))

        form = Card(parent, bg="#f7f9fb")
        form.pack(fill="x", pady=10)
        Label(form, text="Create Class", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        self.class_name_field = EntryField(form, "Class Name", bg="#f7f9fb")
        self.class_name_field.pack(fill="x")
        self.class_term_field = EntryField(form, "Term", bg="#f7f9fb")
        self.class_term_field.pack(fill="x")
        Button(form, "Create Class", self.create_class, primary=True).pack(anchor="w", pady=(14, 0))

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        Label(list_frame, text="Your Classes", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")

        classes = self.teacher_classes()
        if not classes:
            Label(list_frame, text="No classes created yet.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            return

        self.class_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), height=8, bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.class_listbox.pack(fill="x", pady=(8, 8))
        students = self.app.professor_repo.list_students()
        for class_record in classes:
            count = len([student for student in students if student.get("class_id") == class_record["id"]])
            line = f"{class_record['name']} ({class_record['term']}) | Students: {count} | Created: {class_record['created_at']}"
            self.class_listbox.insert(tk.END, line)
        Button(list_frame, "Delete Selected Class", self.delete_selected_class).pack(anchor="w", pady=(4, 0))

    def create_class(self):
        name = self.class_name_field.get().strip()
        term = self.class_term_field.get().strip()
        if not name or not term:
            self.class_message.config(text="Class name and term are required.", fg="#c0392b")
            return
        self.app.professor_repo.create_class(self.app.current_user, name, term)
        self.class_message.config(text=f"Class '{name}' created.", fg="#1f7a45")
        self.class_name_field.delete(0, tk.END)
        self.class_term_field.delete(0, tk.END)
        self.dashboard.render()

    def delete_selected_class(self):
        selection = self.class_listbox.curselection()
        if not selection:
            return
        class_record = self.teacher_classes()[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete class '{class_record['name']}'?"):
            self.app.professor_repo.delete_class(class_record["id"])
            self.class_message.config(text="Class deleted.", fg="#1f7a45")
            self.dashboard.render()


class ProfessorTeamsPage(_ProfessorPageBase):
    def render(self, parent):
        Label(parent, text="Team Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Create teams inside a class, then assign students to them from the Students page.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.team_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.team_message.pack(anchor="w", pady=(4, 8))

        form = Card(parent, bg="#f7f9fb")
        form.pack(fill="x", pady=10)
        Label(form, text="Create Team", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        teacher_classes = self.teacher_classes()
        class_values = [f"{c['name']} ({c['term']})" for c in teacher_classes] or ["No Classes"]
        self.team_class_var = tk.StringVar(value=class_values[0])
        OptionField(form, "Class", self.team_class_var, class_values, bg="#f7f9fb").pack(anchor="w")

        self.team_name_field = EntryField(form, "Team Name", bg="#f7f9fb")
        self.team_name_field.pack(fill="x")
        Button(form, "Create Team", self.create_team, primary=True).pack(anchor="w", pady=(14, 0))

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True)
        Label(list_frame, text="Teams", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")

        if not teacher_classes:
            Label(list_frame, text="Create a class first, then add teams.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            return

        self.team_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), height=8, bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.team_listbox.pack(fill="x", pady=(8, 8))
        self.team_records = []
        any_team = False
        students = self.app.professor_repo.list_students()
        for class_record in teacher_classes:
            teams = self.app.professor_repo.list_teams_for_class(class_record["id"])
            for team in teams:
                any_team = True
                self.team_records.append(team)
                members = [s["name"] for s in students if s.get("team_id") == team["id"]]
                label = ", ".join(members) if members else "Empty"
                self.team_listbox.insert(tk.END, f"{class_record['name']} ({class_record['term']}) | {team['name']} | Members: {label}")

        if not any_team:
            Label(list_frame, text="No teams created yet.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            self.team_listbox.destroy()
            return

        Button(list_frame, "Delete Selected Team", self.delete_selected_team).pack(anchor="w", pady=(4, 0))

    def create_team(self):
        class_value = self.team_class_var.get()
        team_name = self.team_name_field.get().strip()
        if class_value == "No Classes" or not team_name:
            self.team_message.config(text="Choose a class and enter a team name.", fg="#c0392b")
            return

        class_record = next((c for c in self.teacher_classes() if f"{c['name']} ({c['term']})" == class_value), None)
        if class_record:
            self.app.professor_repo.create_team(class_record["id"], team_name)
            self.team_message.config(text=f"Team '{team_name}' added to class.", fg="#1f7a45")
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


class ProfessorProjectsPage(_ProfessorPageBase):
    def render(self, parent):
        Label(parent, text="Project Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Review student projects, class/team placement, and approval status.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.professor_project_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.professor_project_message.pack(anchor="w", pady=(4, 8))

        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)

        left = Card(shell, bg="#f7f9fb", width=320)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        Label(left, text="Projects", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")

        self.project_listbox = tk.Listbox(left, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.project_listbox.pack(fill="both", expand=True, pady=8)
        self.project_listbox.bind("<<ListboxSelect>>", lambda _event: self.load_selected_project())

        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)

        Label(right, text="Project Details", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")
        self.project_detail_label = Label(right, text="Select a project to review it.", size=10, bg="white", fg="#334e68", justify="left")
        self.project_detail_label.pack(anchor="w", pady=(6, 12))

        progress_box = Card(right, bg="#eef8f1", padx=14, pady=14)
        progress_box.pack(fill="x", pady=(0, 16))
        Label(progress_box, text="Progress Approval", size=12, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")

        progress_row = tk.Frame(progress_box, bg="#eef8f1")
        progress_row.pack(fill="x", pady=8)
        progress_left = tk.Frame(progress_row, bg="#eef8f1")
        progress_left.pack(side="left", fill="x", expand=True)
        Label(progress_left, text="Professor Progress", size=10, bg="#eef8f1").pack(anchor="w")
        self.professor_progress_scale = tk.Scale(progress_left, from_=0, to=100, orient="horizontal", bg="#eef8f1", highlightthickness=0)
        self.professor_progress_scale.pack(fill="x", pady=(4, 0))

        progress_right = tk.Frame(progress_row, bg="#eef8f1")
        progress_right.pack(side="left", fill="x", expand=True, padx=(16, 0))
        Label(progress_right, text="Progress Requested", size=10, bg="#eef8f1").pack(anchor="w")
        self.progress_request_label = Label(progress_right, text="No project selected.", size=10, bg="#eef8f1", fg="#334e68", justify="left")
        self.progress_request_label.pack(anchor="w", pady=(8, 0))

        progress_actions = tk.Frame(progress_box, bg="#eef8f1")
        progress_actions.pack(anchor="w")
        Button(progress_actions, "Approve Progress", self.approve_progress_request, primary=True).pack(side="left", padx=(0, 8))
        Button(progress_actions, "Reject Progress", self.reject_progress_request).pack(side="left", padx=(0, 8))
        Button(progress_actions, "Save Professor Progress", self.save_professor_progress).pack(side="left")

        row = tk.Frame(right, bg="white")
        row.pack(fill="x", pady=(0, 8))
        left_controls = tk.Frame(row, bg="white")
        left_controls.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.meeting_status_var = tk.StringVar(value="Pending")
        OptionField(left_controls, "Meeting Status", self.meeting_status_var, ["Pending", "Scheduled", "Completed", "Cancelled"]).pack(fill="x")

        right_controls = tk.Frame(row, bg="white")
        right_controls.pack(side="left", fill="x", expand=True)
        self.project_stage_var = tk.StringVar(value="Proposal")
        OptionField(right_controls, "Stage", self.project_stage_var, ["Proposal", "Requirement Analysis", "Design", "Development", "Testing", "Deployment"]).pack(fill="x")

        self.professor_notes_field = TextField(right, "Professor Notes", height=3)
        self.professor_notes_field.pack(fill="x")

        action_row = tk.Frame(right, bg="white")
        action_row.pack(anchor="w")
        Button(action_row, "Approve", lambda: self.update_project_status("Approved"), primary=True).pack(side="left", padx=(0, 8))
        Button(action_row, "Request Changes", lambda: self.update_project_status("Changes Requested")).pack(side="left", padx=(0, 8))
        Button(action_row, "Save Notes Only", lambda: self.update_project_status(None)).pack(side="left")

        self.refresh_project_list()

    def refresh_project_list(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        all_projects = self.app.professor_repo.list_projects()
        self.project_records = [
            project
            for project in all_projects
            if not teacher_class_ids or project.get("class_id") in teacher_class_ids or project.get("class_id") is None
        ]
        self.project_listbox.delete(0, tk.END)
        students = self.app.professor_repo.list_students()
        for project in self.project_records:
            owner = next((u for u in students if u["email"] == project["student_email"]), None)
            name = owner["name"] if owner else "Unknown"
            self.project_listbox.insert(tk.END, f"{name} | {project['title']} | {project['status']}")

    def load_selected_project(self):
        selection = self.project_listbox.curselection()
        if not selection:
            return

        project = self.project_records[selection[0]]
        self.app.selected_project_id = project["id"]
        class_name = self.app.professor_repo.get_class_name(project.get("class_id")) or "Not Assigned"
        team_name = self.app.professor_repo.get_team_name(project.get("team_id")) or "Not Assigned"
        detail_text = (
            f"Student: {project['student_email']}\n"
            f"Class: {class_name} | Team: {team_name}\n"
            f"Priority: {project.get('priority', 'Medium')}\n"
            f"Last Updated: {project.get('last_updated', 'N/A')}"
        )
        self.project_detail_label.config(text=detail_text)
        self.professor_notes_field.delete("1.0", tk.END)
        self.professor_notes_field.insert("1.0", project.get("professor_notes", ""))
        self.professor_progress_scale.set(project.get("progress", 0))
        self.meeting_status_var.set(project.get("meeting_status", "Pending"))
        self.project_stage_var.set(project.get("stage", "Proposal"))

        req = project.get("requested_progress")
        if req is not None:
            self.progress_request_label.config(text=f"Student requested change to {req}%.\nApprove or reject this request.", fg="#b45309")
        else:
            self.progress_request_label.config(text="No pending progress requests.", fg="#52606d")

    def update_project_status(self, status):
        if not self.app.selected_project_id:
            return

        notes = self.professor_notes_field.get("1.0", "end").strip()
        meeting = self.meeting_status_var.get()
        stage = self.project_stage_var.get()
        updates = {"professor_notes": notes, "meeting_status": meeting, "stage": stage}
        if status:
            updates["status"] = status

        self.app.professor_repo.update_project(
            self.app.selected_project_id,
            updates,
            notification=f"Professor updated status to {status or 'Notes Only'}",
        )
        self.professor_project_message.config(text="Project record updated.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def save_professor_progress(self):
        if not self.app.selected_project_id:
            return

        value = self.professor_progress_scale.get()
        self.app.professor_repo.update_project(
            self.app.selected_project_id,
            {"progress": value, "requested_progress": None},
            notification=f"Professor set progress to {value}%",
        )
        self.professor_project_message.config(text=f"Progress manually set to {value}%.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()

    def approve_progress_request(self):
        if not self.app.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] != self.app.selected_project_id:
                continue
            req = project.get("requested_progress")
            if req is not None:
                self.app.professor_repo.update_project(
                    project["id"],
                    {"progress": req, "requested_progress": None},
                    notification=f"Progress request for {req}% APPROVED.",
                )
                self.professor_project_message.config(text=f"Approved progress of {req}%.", fg="#1f7a45")
                self.refresh_project_list()
                self.reload_selected_project_details()
            return

    def reject_progress_request(self):
        if not self.app.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] != self.app.selected_project_id:
                continue
            req = project.get("requested_progress")
            if req is not None:
                self.app.professor_repo.update_project(
                    project["id"],
                    {"requested_progress": None},
                    notification=f"Progress request for {req}% REJECTED.",
                )
                self.professor_project_message.config(text=f"Rejected progress request of {req}%.", fg="#c0392b")
                self.refresh_project_list()
                self.reload_selected_project_details()
            return

    def reload_selected_project_details(self):
        if not self.app.selected_project_id:
            return
        for index, project in enumerate(self.project_records):
            if project["id"] == self.app.selected_project_id:
                self.project_listbox.selection_clear(0, tk.END)
                self.project_listbox.selection_set(index)
                self.load_selected_project()
                return


class ProfessorDashboardPage:
    def __init__(self, app):
        self.app = app
        self.page_renderers = {
            "overview": ProfessorOverviewPage(self),
            "students": ProfessorStudentsPage(self),
            "classes": ProfessorClassesPage(self),
            "teams": ProfessorTeamsPage(self),
            "projects": ProfessorProjectsPage(self),
        }

    def render(self):
        self.app.clear_screen()
        self.app.current_user = self.app.professor_repo.refresh_user(self.app.current_user["id"])
        subtitle = f"Signed in as {self.app.current_user['name']} ({self.app.current_user['email']})"
        Header(self.app.main_frame, "Professor Workspace", subtitle, self.app.log_out).pack(fill="x", pady=(0, 14))

        sidebar, content = self.app.build_shell()
        Label(sidebar, text="Professor Menu", size=15, bold=True, bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.app.sidebar_button(sidebar, "Overview", lambda: self.set_page("overview"), self.app.professor_page == "overview")
        self.app.sidebar_button(sidebar, "Students", lambda: self.set_page("students"), self.app.professor_page == "students")
        self.app.sidebar_button(sidebar, "Classes", lambda: self.set_page("classes"), self.app.professor_page == "classes")
        self.app.sidebar_button(sidebar, "Teams", lambda: self.set_page("teams"), self.app.professor_page == "teams")
        self.app.sidebar_button(sidebar, "Projects", lambda: self.set_page("projects"), self.app.professor_page == "projects")

        page = self.page_renderers.get(self.app.professor_page, self.page_renderers["overview"])
        page.render(content)

    def set_page(self, page):
        self.app.professor_page = page
        self.render()
