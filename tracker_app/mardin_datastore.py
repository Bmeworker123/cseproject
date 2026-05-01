from .galib_datastore import GalibDataStore


class MardinDataStore(GalibDataStore):
    def delete_student(self, student_id):
        student = self.find_user_by_id(student_id)
        if not student or student.get("role") != "student":
            raise ValueError("Student not found.")
        users = [user for user in self.list_users() if user["id"] != student_id]
        teams = self.list_teams()
        for team in teams:
            if student_id in team.get("member_ids", []):
                team["member_ids"] = [member_id for member_id in team["member_ids"] if member_id != student_id]
        projects = [
            project
            for project in self.list_projects()
            if project.get("student_email") != student["email"]
        ]
        self.save_users(users)
        self.save_teams(teams)
        self.save_projects(projects)
        return student

    def list_students(self):
        return [user for user in self.list_users() if user["role"] == "student"]

    def list_professors(self):
        return [user for user in self.list_users() if user["role"] == "professor"]

    def list_recent_students(self, limit=5):
        students = self.list_students()
        students.sort(key=lambda user: user.get("created_at", ""), reverse=True)
        return students[:limit]

    def create_class(self, teacher, class_name, term):
        classes = self.list_classes()
        new_class = {
            "id": self._next_id(classes),
            "name": class_name.strip(),
            "term": term.strip(),
            "teacher_email": teacher["email"],
            "teacher_name": teacher["name"],
            "created_at": self._timestamp(),
        }
        classes.append(new_class)
        self.save_classes(classes)
        return new_class

    def delete_class(self, class_id):
        class_record = self.find_class_by_id(class_id)
        if not class_record:
            raise ValueError("Class not found.")
        classes = [item for item in self.list_classes() if item["id"] != class_id]
        teams = [team for team in self.list_teams() if team.get("class_id") != class_id]
        users = self.list_users()
        for user in users:
            if user.get("class_id") == class_id:
                user["class_id"] = None
                user["team_id"] = None
        projects = self.list_projects()
        for project in projects:
            if project.get("class_id") == class_id:
                project["class_id"] = None
                project["team_id"] = None
        self.save_classes(classes)
        self.save_teams(teams)
        self.save_users(users)
        self.save_projects(projects)
        return class_record

    def list_classes_for_teacher(self, teacher_email):
        return [item for item in self.list_classes() if item["teacher_email"] == teacher_email]

    def find_class_by_id(self, class_id):
        for item in self.list_classes():
            if item["id"] == class_id:
                return item
        return None

    def create_team(self, class_id, team_name):
        teams = self.list_teams()
        new_team = {
            "id": self._next_id(teams),
            "class_id": class_id,
            "name": team_name.strip(),
            "member_ids": [],
            "created_at": self._timestamp(),
        }
        teams.append(new_team)
        self.save_teams(teams)
        return new_team

    def delete_team(self, team_id):
        team = self.find_team_by_id(team_id)
        if not team:
            raise ValueError("Team not found.")
        teams = [item for item in self.list_teams() if item["id"] != team_id]
        users = self.list_users()
        for user in users:
            if user.get("team_id") == team_id:
                user["team_id"] = None
        projects = self.list_projects()
        for project in projects:
            if project.get("team_id") == team_id:
                project["team_id"] = None
        self.save_teams(teams)
        self.save_users(users)
        self.save_projects(projects)
        return team

    def find_team_by_id(self, team_id):
        for item in self.list_teams():
            if item["id"] == team_id:
                return item
        return None

    def list_teams_for_class(self, class_id):
        return [item for item in self.list_teams() if item.get("class_id") == class_id]

    def assign_student_to_class(self, student_id, class_id):
        student = self.find_user_by_id(student_id)
        if not student:
            raise ValueError("Student not found.")
        self.assign_student_to_team(student_id, None)
        updated = self.update_user(student_id, {"class_id": class_id})
        project = self.get_project_for_student(updated["email"])
        if project:
            self.update_project(project["id"], {"class_id": class_id, "team_id": None})
        return updated

    def assign_student_to_team(self, student_id, team_id):
        teams = self.list_teams()
        users = self.list_users()
        target_user = None
        for user in users:
            if user["id"] == student_id:
                target_user = user
                break
        if target_user is None:
            raise ValueError("Student not found.")
        for team in teams:
            if student_id in team.get("member_ids", []):
                team["member_ids"] = [member_id for member_id in team["member_ids"] if member_id != student_id]
        target_user["team_id"] = team_id
        if team_id is not None:
            matching = None
            for team in teams:
                if team["id"] == team_id:
                    matching = team
                    break
            if matching is None:
                raise ValueError("Team not found.")
            if student_id not in matching["member_ids"]:
                matching["member_ids"].append(student_id)
            target_user["class_id"] = matching["class_id"]
        self.save_users(users)
        self.save_teams(teams)
        project = self.get_project_for_student(target_user["email"])
        if project:
            self.update_project(project["id"], {"class_id": target_user.get("class_id"), "team_id": team_id})
        return target_user

    def approve_progress_request(self, project_id):
        project = self._find_project_or_raise(project_id)
        requested = project.get("requested_progress")
        if requested is None:
            raise ValueError("No pending progress request.")
        return self.update_project(
            project_id,
            {
                "progress": requested,
                "requested_progress": None,
                "progress_request_status": "Approved",
            },
            notification=f"Professor approved your progress change. Official progress is now {requested}%.",
        )

    def reject_progress_request(self, project_id):
        project = self._find_project_or_raise(project_id)
        if project.get("requested_progress") is None:
            raise ValueError("No pending progress request.")
        return self.update_project(
            project_id,
            {
                "requested_progress": None,
                "progress_request_status": "Rejected",
            },
            notification="Professor rejected your progress change request.",
        )

    def _find_project_or_raise(self, project_id):
        for project in self.list_projects():
            if project["id"] == project_id:
                return project
        raise ValueError("Project not found.")

    # Aliases for compatibility
    def delete_user(self, user_id):
        return self.delete_student(user_id)

    def get_class_record(self, class_id):
        return self.find_class_by_id(class_id)


# Alias for compatibility
DataStore = MardinDataStore
