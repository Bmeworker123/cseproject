import tkinter as tk
from tkinter import messagebox
from .ui import Button, Label


class ProfessorRepository:
    def __init__(self, store):
        self.store = store

    def __getattr__(self, name):
        return getattr(self.store, name)

    def refresh_user(self, user_id):
        return self.store.find_user_by_id(user_id)

    def classes_for(self, teacher_email):
        return self.store.list_classes_for_teacher(teacher_email)


class ProfessorMixin:
    def show_professor_dashboard(self):
        self.clear_screen()
        self.current_user = self.professor_repo.refresh_user(self.current_user["id"])
        subtitle = f"Signed in as {self.current_user['name']} ({self.current_user['email']})"
        self.create_header("Professor Workspace", subtitle)
        sidebar, content = self.build_shell()
        Label(sidebar, text="Professor Menu", size=15, bold=True, bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
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
        return self.professor_repo.classes_for(self.current_user["email"])
    def render_professor_overview(self, parent):
        students = self.professor_repo.list_students()
        projects = self.professor_repo.list_projects()
        classes = self.teacher_classes()
        Label(parent, text="Overview", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Quick view of student growth, class setup, and team structure.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        self.render_stat_card(stats, "Total Students", str(len(students)), "Enrolled in project tracker.")
        self.render_stat_card(stats, "Active Projects", str(len(projects)), "Submitted for review.")
        self.render_stat_card(stats, "Your Classes", str(len(classes)), "Created by you.")
        recent_card = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        recent_card.pack(fill="x", pady=14)
        Label(recent_card, text="New Students", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        new_students = sorted(students, key=lambda user: user.get("created_at", ""), reverse=True)[:5]
        if not new_students:
            Label(recent_card, text="No student accounts yet.", size=10, bg="#f7f9fb", fg="#52606d").pack(anchor="w", pady=(6, 0))
        else:
            for user in new_students:
                line = f"{user['name']} ({user['email']}) | Joined: {user.get('created_at', 'N/A')}"
                Label(recent_card, text=line, size=10, bg="#f7f9fb", fg="#334e68").pack(anchor="w", pady=2)
        actions = tk.Frame(parent, bg="#eef8f1", padx=16, pady=16)
        actions.pack(fill="x")
        Label(actions, text="Teacher Actions", size=13, bold=True, bg="#eef8f1", fg="#14532d").pack(anchor="w")
        Label(actions, text="Use Students to assign classes, Classes to create offerings, Teams to group students, and Projects to review submissions.", size=10, bg="#eef8f1", fg="#1f7a45", wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))
        row = tk.Frame(actions, bg="#eef8f1")
        row.pack(anchor="w")
        Button(row, "Open Classes", lambda: self.set_professor_page("classes"), primary=True).pack(side="left", padx=(0, 8))
        Button(row, "Open Teams", lambda: self.set_professor_page("teams")).pack(side="left", padx=(0, 8))
        Button(row, "Open Projects", lambda: self.set_professor_page("projects")).pack(side="left")
    def render_professor_students(self, parent):
        Label(parent, text="Student Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Inspect students, leave notes, set status, and assign them to classes and teams.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.professor_student_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.professor_student_message.pack(anchor="w", pady=(4, 8))
        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)
        left = tk.Frame(shell, bg="#f7f9fb", width=300, padx=12, pady=12)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        Label(left, text="Students", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        self.student_listbox = tk.Listbox(left, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.student_listbox.pack(fill="both", expand=True, pady=8)
        self.student_listbox.bind("<<ListboxSelect>>", lambda _: self.load_selected_student())
        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)
        Label(right, text="Student Details", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")
        self.student_detail_label = Label(right, text="Select a student to manage their record.", size=10, bg="white", fg="#334e68", justify="left")
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
        tk.OptionMenu(status_box, self.account_status_var, "Active", "Suspended", "Graduated").pack(fill="x", pady=(4, 0))
        class_box = tk.Frame(controls, bg="white")
        class_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        Label(class_box, text="Assign Class", size=10, bg="white").pack(anchor="w")
        self.assign_class_var = tk.StringVar(value="Not Assigned")
        self.assign_class_menu = tk.OptionMenu(class_box, self.assign_class_var, "Not Assigned")
        self.assign_class_menu.pack(fill="x", pady=(4, 0))
        team_box = tk.Frame(controls, bg="white")
        team_box.pack(side="left", fill="x", expand=True)
        Label(team_box, text="Assign Team", size=10, bg="white").pack(anchor="w")
        self.assign_team_var = tk.StringVar(value="Not Assigned")
        self.assign_team_menu = tk.OptionMenu(team_box, self.assign_team_var, "Not Assigned")
        self.assign_team_menu.pack(fill="x", pady=(4, 0))
        row = tk.Frame(right, bg="white")
        row.pack(fill="x")
        Button(row, "Save Student Changes", self.save_student_changes, primary=True).pack(side="left", padx=(0, 8))
        Button(row, "Delete Student", self.delete_selected_student).pack(side="left", padx=(0, 8))
        Button(row, "Refresh List", self.show_professor_dashboard).pack(side="left")
        self.refresh_student_list()
    def refresh_student_list(self):
        students = self.professor_repo.list_students()
        students.sort(key=lambda user: user.get("created_at", ""), reverse=True)
        self.student_records = students
        self.student_listbox.delete(0, tk.END)
        for user in students:
            status = user.get("account_status", "Active")
            line = f"{user['name']} | {status}"
            self.student_listbox.insert(tk.END, line)
        self.update_student_dropdowns()
    def update_student_dropdowns(self):
        classes = self.teacher_classes()
        class_names = ["Not Assigned"] + [f"{c['name']} ({c['term']})" for c in classes]
        self.assign_class_menu["menu"].delete(0, "end")
        for name in class_names:
            self.assign_class_menu["menu"].add_command(label=name, command=tk._setit(self.assign_class_var, name, self.on_class_change))
    def on_class_change(self, class_name):
        if class_name == "Not Assigned":
            self.assign_team_var.set("Not Assigned")
            self.assign_team_menu["menu"].delete(0, "end")
            self.assign_team_menu["menu"].add_command(label="Not Assigned", command=tk._setit(self.assign_team_var, "Not Assigned"))
            return
        classes = self.teacher_classes()
        class_record = next((c for c in classes if f"{c['name']} ({c['term']})" == class_name), None)
        if class_record:
            teams = self.professor_repo.list_teams_for_class(class_record["id"])
            team_names = ["Not Assigned"] + [t["name"] for t in teams]
            self.assign_team_menu["menu"].delete(0, "end")
            for name in team_names:
                self.assign_team_menu["menu"].add_command(label=name, command=tk._setit(self.assign_team_var, name))
            self.assign_team_var.set("Not Assigned")
    def load_selected_student(self):
        selection = self.student_listbox.curselection()
        if not selection:
            return
        user = self.student_records[selection[0]]
        self.selected_student_id = user["id"]
        detail_text = f"Email: {user['email']}\nStudent ID: {user.get('student_id', 'N/A')}\nDepartment: {user.get('department', 'N/A')}"
        self.student_detail_label.config(text=detail_text)
        self.teacher_notes_text.delete("1.0", tk.END)
        self.teacher_notes_text.insert("1.0", user.get("teacher_notes", ""))
        self.account_status_var.set(user.get("account_status", "Active"))
        class_id = user.get("class_id")
        if class_id:
            class_record = self.professor_repo.store.get_class_record(class_id)
            if class_record:
                name = f"{class_record['name']} ({class_record['term']})"
                self.assign_class_var.set(name)
                self.on_class_change(name)
                team_id = user.get("team_id")
                if team_id:
                    team_record = next((t for t in self.professor_repo.list_teams() if t["id"] == team_id), None)
                    if team_record:
                        self.assign_team_var.set(team_record["name"])
                    else:
                        self.assign_team_var.set("Not Assigned")
                else:
                    self.assign_team_var.set("Not Assigned")
            else:
                self.assign_class_var.set("Not Assigned")
                self.on_class_change("Not Assigned")
        else:
            self.assign_class_var.set("Not Assigned")
            self.on_class_change("Not Assigned")
    def save_student_changes(self):
        if not self.selected_student_id:
            return
        notes = self.teacher_notes_text.get("1.0", "end").strip()
        status = self.account_status_var.get()
        class_name = self.assign_class_var.get()
        team_name = self.assign_team_var.get()
        updates = {"teacher_notes": notes, "account_status": status}
        if class_name == "Not Assigned":
            updates["class_id"] = None
            updates["team_id"] = None
        else:
            classes = self.teacher_classes()
            class_record = next((c for c in classes if f"{c['name']} ({c['term']})" == class_name), None)
            if class_record:
                updates["class_id"] = class_record["id"]
                if team_name == "Not Assigned":
                    updates["team_id"] = None
                else:
                    teams = self.professor_repo.list_teams_for_class(class_record["id"])
                    team_record = next((t for t in teams if t["name"] == team_name), None)
                    if team_record:
                        updates["team_id"] = team_record["id"]
        self.professor_repo.update_user(self.selected_student_id, updates)
        self.professor_student_message.config(text="Student record updated successfully.", fg="#1f7a45")
        self.refresh_student_list()
    def delete_selected_student(self):
        if not self.selected_student_id:
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            self.professor_repo.delete_user(self.selected_student_id)
            self.selected_student_id = None
            self.professor_student_message.config(text="Student deleted.", fg="#1f7a45")
            self.refresh_student_list()
    def render_professor_classes(self, parent):
        Label(parent, text="Class Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Create classes and keep track of how many students belong to each one.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.class_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.class_message.pack(anchor="w", pady=(4, 8))
        form = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        form.pack(fill="x", pady=10)
        Label(form, text="Create Class", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        Label(form, text="Class Name", size=10, bg="#f7f9fb").pack(anchor="w", pady=(8, 4))
        self.class_name_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.class_name_entry.pack(fill="x")
        Label(form, text="Term", size=10, bg="#f7f9fb").pack(anchor="w", pady=(10, 4))
        self.class_term_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.class_term_entry.pack(fill="x")
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
        for class_record in classes:
            count = len([student for student in self.professor_repo.list_students() if student.get("class_id") == class_record["id"]])
            line = f"{class_record['name']} ({class_record['term']}) | Students: {count} | Created: {class_record['created_at']}"
            self.class_listbox.insert(tk.END, line)
        Button(list_frame, "Delete Selected Class", self.delete_selected_class).pack(anchor="w", pady=(4, 0))
    def create_class(self):
        name = self.class_name_entry.get().strip()
        term = self.class_term_entry.get().strip()
        if not name or not term:
            self.class_message.config(text="Class name and term are required.", fg="#c0392b")
            return
        self.professor_repo.create_class(name, term, self.current_user["email"])
        self.class_message.config(text=f"Class '{name}' created.", fg="#1f7a45")
        self.class_name_entry.delete(0, tk.END)
        self.class_term_entry.delete(0, tk.END)
        self.show_professor_dashboard()
    def delete_selected_class(self):
        selection = self.class_listbox.curselection()
        if not selection:
            return
        class_record = self.teacher_classes()[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete class '{class_record['name']}'?"):
            self.professor_repo.delete_class(class_record["id"])
            self.class_message.config(text="Class deleted.", fg="#1f7a45")
            self.show_professor_dashboard()
    def render_professor_teams(self, parent):
        Label(parent, text="Team Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Create teams inside a class, then assign students to them from the Students page.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.team_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.team_message.pack(anchor="w", pady=(4, 8))
        form = tk.Frame(parent, bg="#f7f9fb", padx=16, pady=16)
        form.pack(fill="x", pady=10)
        Label(form, text="Create Team", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        Label(form, text="Class", size=10, bg="#f7f9fb").pack(anchor="w", pady=(8, 4))
        self.team_class_var = tk.StringVar()
        teacher_classes = self.teacher_classes()
        class_values = [f"{c['name']} ({c['term']})" for c in teacher_classes] or ["No Classes"]
        self.team_class_var.set(class_values[0])
        self.team_class_menu = tk.OptionMenu(form, self.team_class_var, *class_values)
        self.team_class_menu.pack(anchor="w")
        Label(form, text="Team Name", size=10, bg="#f7f9fb").pack(anchor="w", pady=(10, 4))
        self.team_name_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.team_name_entry.pack(fill="x")
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
        for class_record in teacher_classes:
            teams = self.professor_repo.list_teams_for_class(class_record["id"])
            for team in teams:
                any_team = True
                self.team_records.append(team)
                members = [s["name"] for s in self.professor_repo.list_students() if s.get("team_id") == team["id"]]
                label = ", ".join(members) if members else "Empty"
                self.team_listbox.insert(tk.END, f"{class_record['name']} ({class_record['term']}) | {team['name']} | Members: {label}")
        if not any_team:
            Label(list_frame, text="No teams created yet.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=(8, 0))
            self.team_listbox.destroy()
            return
        Button(list_frame, "Delete Selected Team", self.delete_selected_team).pack(anchor="w", pady=(4, 0))
    def create_team(self):
        class_value = self.team_class_var.get()
        team_name = self.team_name_entry.get().strip()
        if class_value == "No Classes" or not team_name:
            self.team_message.config(text="Choose a class and enter a team name.", fg="#c0392b")
            return
        classes = self.teacher_classes()
        class_record = next((c for c in classes if f"{c['name']} ({c['term']})" == class_value), None)
        if class_record:
            self.professor_repo.create_team(team_name, class_record["id"])
            self.team_message.config(text=f"Team '{team_name}' added to class.", fg="#1f7a45")
            self.team_name_entry.delete(0, tk.END)
            self.show_professor_dashboard()
    def delete_selected_team(self):
        selection = self.team_listbox.curselection()
        if not selection:
            return
        team = self.team_records[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete team '{team['name']}'?"):
            self.professor_repo.delete_team(team["id"])
            self.team_message.config(text="Team deleted.", fg="#1f7a45")
            self.show_professor_dashboard()
    def render_professor_projects(self, parent):
        Label(parent, text="Project Management", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="Review student projects, class/team placement, and approval status.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)
        self.professor_project_message = Label(parent, text="", size=10, bg="white", fg="#1f7a45")
        self.professor_project_message.pack(anchor="w", pady=(4, 8))
        shell = tk.Frame(parent, bg="white")
        shell.pack(fill="both", expand=True, pady=10)
        left = tk.Frame(shell, bg="#f7f9fb", width=320, padx=12, pady=12)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        Label(left, text="Projects", size=13, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w")
        self.project_listbox = tk.Listbox(left, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#e1e4e8")
        self.project_listbox.pack(fill="both", expand=True, pady=8)
        self.project_listbox.bind("<<ListboxSelect>>", lambda _: self.load_selected_project())
        right = tk.Frame(shell, bg="white")
        right.pack(side="left", fill="both", expand=True)
        Label(right, text="Project Details", size=13, bold=True, bg="white", fg="#102a43").pack(anchor="w")
        self.project_detail_label = Label(right, text="Select a project to review it.", size=10, bg="white", fg="#334e68", justify="left")
        self.project_detail_label.pack(anchor="w", pady=(6, 12))
        progress_box = tk.Frame(right, bg="#eef8f1", padx=14, pady=14)
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
        Label(left_controls, text="Meeting Status", size=10, bg="white").pack(anchor="w")
        self.meeting_status_var = tk.StringVar(value="Pending")
        tk.OptionMenu(left_controls, self.meeting_status_var, "Pending", "Scheduled", "Completed", "Cancelled").pack(fill="x", pady=(4, 0))
        right_controls = tk.Frame(row, bg="white")
        right_controls.pack(side="left", fill="x", expand=True)
        Label(right_controls, text="Stage", size=10, bg="white").pack(anchor="w")
        self.project_stage_var = tk.StringVar(value="Proposal")
        tk.OptionMenu(right_controls, self.project_stage_var, "Proposal", "Requirement Analysis", "Design", "Development", "Testing", "Deployment").pack(fill="x", pady=(4, 0))
        Label(right, text="Professor Notes", size=10, bg="white").pack(anchor="w")
        self.professor_notes_text = tk.Text(right, height=3, font=("Segoe UI", 10))
        self.professor_notes_text.pack(fill="x", pady=(4, 8))
        action_row = tk.Frame(right, bg="white")
        action_row.pack(anchor="w")
        Button(action_row, "Approve", lambda: self.update_project_status("Approved"), primary=True).pack(side="left", padx=(0, 8))
        Button(action_row, "Request Changes", lambda: self.update_project_status("Changes Requested")).pack(side="left", padx=(0, 8))
        Button(action_row, "Save Notes Only", lambda: self.update_project_status(None)).pack(side="left")
        self.refresh_project_list()
    def refresh_project_list(self):
        teacher_class_ids = {item["id"] for item in self.teacher_classes()}
        all_projects = self.professor_repo.list_projects()
        self.project_records = [project for project in all_projects if not teacher_class_ids or project.get("class_id") in teacher_class_ids or project.get("class_id") is None]
        self.project_listbox.delete(0, tk.END)
        for project in self.project_records:
            owner = next((u for u in self.professor_repo.list_students() if u["email"] == project["student_email"]), None)
            name = owner["name"] if owner else "Unknown"
            self.project_listbox.insert(tk.END, f"{name} | {project['title']} | {project['status']}")
    def load_selected_project(self):
        selection = self.project_listbox.curselection()
        if not selection:
            return
        project = self.project_records[selection[0]]
        self.selected_project_id = project["id"]
        class_name = self.professor_repo.get_class_name(project.get("class_id")) or "Not Assigned"
        team_name = self.professor_repo.get_team_name(project.get("team_id")) or "Not Assigned"
        detail_text = f"Student: {project['student_email']}\nClass: {class_name} | Team: {team_name}\nPriority: {project.get('priority', 'Medium')}\nLast Updated: {project['updated_at']}"
        self.project_detail_label.config(text=detail_text)
        self.professor_notes_text.delete("1.0", tk.END)
        self.professor_notes_text.insert("1.0", project.get("professor_notes", ""))
        self.professor_progress_scale.set(project.get("progress", 0))
        self.meeting_status_var.set(project.get("meeting_status", "Pending"))
        self.project_stage_var.set(project.get("stage", "Proposal"))
        req = project.get("requested_progress")
        if req is not None:
            self.progress_request_label.config(text=f"Student requested change to {req}%.\nApprove or reject this request.", fg="#b45309")
        else:
            self.progress_request_label.config(text="No pending progress requests.", fg="#52606d")
    def update_project_status(self, status):
        if not self.selected_project_id:
            return
        notes = self.professor_notes_text.get("1.0", "end").strip()
        meeting = self.meeting_status_var.get()
        stage = self.project_stage_var.get()
        updates = {"professor_notes": notes, "meeting_status": meeting, "stage": stage}
        if status:
            updates["status"] = status
        self.professor_repo.update_project(self.selected_project_id, updates, notification=f"Professor updated status to {status or 'Notes Only'}")
        self.professor_project_message.config(text="Project record updated.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()
    def save_professor_progress(self):
        if not self.selected_project_id:
            return
        val = self.professor_progress_scale.get()
        self.professor_repo.update_project(self.selected_project_id, {"progress": val, "requested_progress": None}, notification=f"Professor set progress to {val}%")
        self.professor_project_message.config(text=f"Progress manually set to {val}%.", fg="#1f7a45")
        self.refresh_project_list()
        self.reload_selected_project_details()
    def approve_progress_request(self):
        if not self.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] == self.selected_project_id:
                req = project.get("requested_progress")
                if req is not None:
                    self.professor_repo.update_project(project["id"], {"progress": req, "requested_progress": None}, notification=f"Progress request for {req}% APPROVED.")
                    self.professor_project_message.config(text=f"Approved progress of {req}%.", fg="#1f7a45")
                    self.refresh_project_list()
                    self.reload_selected_project_details()
                return
    def reject_progress_request(self):
        if not self.selected_project_id:
            return
        for project in self.project_records:
            if project["id"] == self.selected_project_id:
                req = project.get("requested_progress")
                if req is not None:
                    self.professor_repo.update_project(project["id"], {"requested_progress": None}, notification=f"Progress request for {req}% REJECTED.")
                    self.professor_project_message.config(text=f"Rejected progress request of {req}%.", fg="#c0392b")
                    self.add_professor_note_notification(project["id"], "Progress Rejected")
                    self.refresh_project_list()
                    self.reload_selected_project_details()
                return
    def add_professor_note_notification(self, project_id, prefix):
        note = self.professor_notes_text.get("1.0", "end").strip()
        if not note:
            return
        self.professor_repo.update_project(project_id, {}, notification=f"{prefix}: {note}")
    def reload_selected_project_details(self):
        if not self.selected_project_id:
            return
        for index, project in enumerate(self.project_records):
            if project["id"] == self.selected_project_id:
                self.project_listbox.selection_clear(0, tk.END)
                self.project_listbox.selection_set(index)
                self.load_selected_project()
                return
