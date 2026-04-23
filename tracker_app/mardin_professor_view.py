import tkinter as tk
from tkinter import messagebox


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
        return self.professor_repo.classes_for(self.current_user["email"])
    def render_professor_overview(self, parent):
        students = self.professor_repo.list_students()
        projects = self.professor_repo.list_projects()
        classes = self.teacher_classes()
        teams = []
        for class_record in classes:
            teams.extend(self.professor_repo.list_teams_for_class(class_record["id"]))
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
        recent = self.professor_repo.list_recent_students()
        if not recent:
            tk.Label(recent_card, text="No student accounts yet.", font=("Segoe UI", 10), bg="#f7f9fb", fg="#52606d").pack(anchor="w", pady=(6, 0))
        else:
            for student in recent:
                line = f"{student['name']} | {student['email']} | Class: {self.professor_repo.get_class_name(student.get('class_id'))} | Team: {self.professor_repo.get_team_name(student.get('team_id'))}"
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
        students = self.professor_repo.list_students()
        students.sort(key=lambda user: user.get("created_at", ""), reverse=True)
        self.student_records = students
        self.student_listbox.delete(0, tk.END)
        for student in students:
            label = f"{student['name']} | {student.get('status', 'Active')} | {self.professor_repo.get_class_name(student.get('class_id'))}"
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
        project = self.professor_repo.get_project_for_student(student["email"])
        details = [
            f"Name: {student['name']}",
            f"Email: {student['email']}",
            f"Student ID: {student.get('student_id') or 'Not added'}",
            f"Department: {student.get('department') or 'Not added'}",
            f"Status: {student.get('status', 'Active')}",
            f"Class: {self.professor_repo.get_class_name(student.get('class_id'))}",
            f"Team: {self.professor_repo.get_team_name(student.get('team_id'))}",
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
            current_class_record = self.professor_repo.find_class_by_id(student["class_id"])
            if current_class_record:
                current_class = f"{student['class_id']} - {current_class_record['name']} ({current_class_record['term']})"
        self.assign_class_var.set(current_class)
        team_options = ["Not Assigned"]
        if student.get("class_id"):
            team_options.extend([f"{item['id']} - {item['name']}" for item in self.professor_repo.list_teams_for_class(student["class_id"])])
        self._set_option_menu_values(self.assign_team_menu, self.assign_team_var, team_options)
        current_team = "Not Assigned"
        if student.get("team_id"):
            team = self.professor_repo.find_team_by_id(student["team_id"])
            if team:
                current_team = f"{team['id']} - {team['name']}"
        self.assign_team_var.set(current_team)
    def save_student_changes(self):
        if not self.selected_student_id:
            self.professor_student_message.config(text="Select a student first.", fg="#c0392b")
            return
        notes = self.student_notes_text.get("1.0", "end").strip()
        status = self.student_status_var.get()
        self.professor_repo.update_user(self.selected_student_id, {"notes": notes, "status": status})
        class_value = self.assign_class_var.get()
        class_id = None if class_value == "Not Assigned" else int(class_value.split(" - ")[0])
        self.professor_repo.assign_student_to_class(self.selected_student_id, class_id)
        team_value = self.assign_team_var.get()
        team_id = None if team_value == "Not Assigned" else int(team_value.split(" - ")[0])
        if team_id is not None:
            self.professor_repo.assign_student_to_team(self.selected_student_id, team_id)
        self.professor_student_message.config(text="Student record updated.", fg="#1f7a45")
        self.refresh_student_list()
    def delete_selected_student(self):
        if not self.selected_student_id:
            self.professor_student_message.config(text="Select a student first.", fg="#c0392b")
            return
        student = self.professor_repo.find_user_by_id(self.selected_student_id)
        if not student:
            self.professor_student_message.config(text="Student not found.", fg="#c0392b")
            return
        confirmed = messagebox.askyesno(
            "Delete Student",
            f"Delete {student['name']} and remove their project and team assignments?",
        )
        if not confirmed:
            return
        self.professor_repo.delete_student(self.selected_student_id)
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
            count = len([student for student in self.professor_repo.list_students() if student.get("class_id") == class_record["id"]])
            line = f"{class_record['name']} ({class_record['term']}) | Students: {count} | Created: {class_record['created_at']}"
            self.class_listbox.insert(tk.END, line)
        self.make_button(list_frame, "Delete Selected Class", self.delete_selected_class).pack(anchor="w", pady=(4, 0))
    def create_class(self):
        name = self.class_name_entry.get().strip()
        term = self.class_term_entry.get().strip()
        if not name or not term:
            self.class_message.config(text="Class name and term are required.", fg="#c0392b")
            return
        self.professor_repo.create_class(self.current_user, name, term)
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
        self.professor_repo.delete_class(class_record["id"])
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
            teams = self.professor_repo.list_teams_for_class(class_record["id"])
            if not teams:
                continue
            any_team = True
            for team in teams:
                members = [self.professor_repo.find_user_by_id(member_id)["name"] for member_id in team.get("member_ids", []) if self.professor_repo.find_user_by_id(member_id)]
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
        self.professor_repo.create_team(class_id, team_name)
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
        self.professor_repo.delete_team(team["id"])
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
        all_projects = self.professor_repo.list_projects()
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
            f"Class: {self.professor_repo.get_class_name(project.get('class_id'))}",
            f"Team: {self.professor_repo.get_team_name(project.get('team_id'))}",
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
        project = self.professor_repo.update_project(self.selected_project_id, updates, notification=notification)
        text = f"Project updated: {project['title']} is now {project['status']}." if status else "Project notes and stage updated."
        self.professor_project_message.config(text=text, fg="#1f7a45")
        self.refresh_project_list()
    def approve_progress_request(self):
        if not self.selected_project_id:
            self.professor_project_message.config(text="Select a project first.", fg="#c0392b")
            return
        try:
            project = self.professor_repo.approve_progress_request(self.selected_project_id)
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
            project = self.professor_repo.reject_progress_request(self.selected_project_id)
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
        current_project = self.professor_repo._find_project_or_raise(self.selected_project_id)
        updates = {
            "progress": progress,
            "requested_progress": None,
            "progress_request_status": "Professor Updated",
        }
        if current_project.get("status") in {"Pending Approval", "Resubmitted"}:
            updates["status"] = "Reviewed"
        project = self.professor_repo.update_project(
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
