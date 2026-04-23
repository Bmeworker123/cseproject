import hashlib
import hmac
import json
import os
from datetime import datetime
class DataStore:
    def __init__(self, base_dir):
        self.data_dir = os.path.join(base_dir, "data")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.classes_file = os.path.join(self.data_dir, "classes.json")
        self.teams_file = os.path.join(self.data_dir, "teams.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._ensure_file(self.users_file, [])
        self._ensure_file(self.projects_file, [])
        self._ensure_file(self.classes_file, [])
        self._ensure_file(self.teams_file, [])
        self.migrate_data()
    def _ensure_file(self, path, default_value):
        if os.path.exists(path):
            return
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_value, file, indent=2)
    def _read_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    def _write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    def _next_id(self, records):
        if not records:
            return 1
        return max(record["id"] for record in records) + 1
    def _hash_password(self, password):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return f"{salt.hex()}:{digest.hex()}"
    def _verify_password(self, password, stored_hash):
        try:
            salt_hex, digest_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_digest = bytes.fromhex(digest_hex)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return hmac.compare_digest(digest, expected_digest)
    def list_users(self):
        return self._read_json(self.users_file)
    def save_users(self, users):
        self._write_json(self.users_file, users)
    def list_projects(self):
        return self._read_json(self.projects_file)
    def save_projects(self, projects):
        self._write_json(self.projects_file, projects)
    def list_classes(self):
        return self._read_json(self.classes_file)
    def save_classes(self, classes):
        self._write_json(self.classes_file, classes)
    def list_teams(self):
        return self._read_json(self.teams_file)
    def save_teams(self, teams):
        self._write_json(self.teams_file, teams)
    def migrate_data(self):
        users = self.list_users()
        users_changed = False
        for user in users:
            email = user.get("email", "").strip().lower()
            default_name = email.split("@")[0].replace(".", " ").title() if email else "User"
            defaults = {
                "name": default_name,
                "role": user.get("role", "student"),
                "status": "Active",
                "created_at": self._timestamp(),
                "last_login": "",
                "student_id": "",
                "department": "",
                "notes": "",
                "class_id": None,
                "team_id": None,
            }
            for key, value in defaults.items():
                if key not in user:
                    user[key] = value
                    users_changed = True
        if users_changed:
            self.save_users(users)
        projects = self.list_projects()
        projects_changed = False
        for project in projects:
            defaults = {
                "status": "Pending Approval",
                "progress": 0,
                "notes": "No notes yet.",
                "professor_notes": "Awaiting professor review.",
                "stage": "Proposal",
                "priority": "Medium",
                "meeting_status": "Not Scheduled",
                "last_updated": self._timestamp(),
                "class_id": None,
                "team_id": None,
                "requested_progress": None,
                "progress_request_status": "None",
                "notifications": [],
            }
            for key, value in defaults.items():
                if key not in project:
                    project[key] = value
                    projects_changed = True
        if projects_changed:
            self.save_projects(projects)
        classes = self.list_classes()
        classes_changed = False
        for item in classes:
            defaults = {
                "teacher_email": "",
                "teacher_name": "",
                "created_at": self._timestamp(),
            }
            for key, value in defaults.items():
                if key not in item:
                    item[key] = value
                    classes_changed = True
        if classes_changed:
            self.save_classes(classes)
        teams = self.list_teams()
        teams_changed = False
        for item in teams:
            defaults = {
                "class_id": None,
                "member_ids": [],
                "created_at": self._timestamp(),
            }
            for key, value in defaults.items():
                if key not in item:
                    item[key] = value
                    teams_changed = True
        if teams_changed:
            self.save_teams(teams)
    def find_user_by_email(self, email):
        clean_email = email.strip().lower()
        for user in self.list_users():
            if user["email"] == clean_email:
                return user
        return None
    def find_user_by_id(self, user_id):
        for user in self.list_users():
            if user["id"] == user_id:
                return user
        return None
    def create_user(self, name, email, password, role, student_id="", department=""):
        users = self.list_users()
        clean_email = email.strip().lower()
        if self.find_user_by_email(clean_email):
            raise ValueError("An account with this email already exists.")
        user = {
            "id": self._next_id(users),
            "name": name.strip(),
            "email": clean_email,
            "password_hash": self._hash_password(password),
            "role": role,
            "status": "Active",
            "created_at": self._timestamp(),
            "last_login": "",
            "student_id": student_id.strip(),
            "department": department.strip(),
            "notes": "",
            "class_id": None,
            "team_id": None,
        }
        users.append(user)
        self.save_users(users)
        return user
    def authenticate(self, email, password):
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password.")
        if user.get("status") == "Archived":
            raise ValueError("This account is archived.")
        if not self._verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password.")
        self.update_user(user["id"], {"last_login": self._timestamp()})
        return self.find_user_by_id(user["id"])
    def update_user(self, user_id, updates):
        users = self.list_users()
        for user in users:
            if user["id"] == user_id:
                user.update(updates)
                self.save_users(users)
                return user
        raise ValueError("User not found.")
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
    def get_project_for_student(self, student_email):
        for project in self.list_projects():
            if project["student_email"] == student_email:
                return project
        return None
    def save_student_project(self, student, title, notes, progress, stage, priority):
        projects = self.list_projects()
        existing = self.get_project_for_student(student["email"])
        if existing:
            for project in projects:
                if project["id"] == existing["id"]:
                    project["student_name"] = student["name"]
                    project["student_id"] = student.get("student_id", "")
                    project["department"] = student.get("department", "")
                    project["title"] = title
                    project["notes"] = notes or "No notes yet."
                    if progress != project.get("progress", 0):
                        project["requested_progress"] = progress
                        project["progress_request_status"] = "Pending"
                        self._add_project_notification(
                            project,
                            f"Your progress change to {progress}% was sent to the professor for approval.",
                        )
                    project["stage"] = stage
                    project["priority"] = priority
                    project["class_id"] = student.get("class_id")
                    project["team_id"] = student.get("team_id")
                    project["last_updated"] = self._timestamp()
                    if project["status"] == "Changes Requested":
                        project["status"] = "Resubmitted"
                    self.save_projects(projects)
                    return project
        new_project = {
            "id": self._next_id(projects),
            "student_email": student["email"],
            "student_name": student["name"],
            "student_id": student.get("student_id", ""),
            "department": student.get("department", ""),
            "title": title,
            "notes": notes or "No notes yet.",
            "progress": progress,
            "requested_progress": None,
            "progress_request_status": "None",
            "notifications": [
                "Project submitted. Waiting for professor review.",
            ],
            "status": "Pending Approval",
            "professor_notes": "Awaiting professor review.",
            "stage": stage,
            "priority": priority,
            "meeting_status": "Not Scheduled",
            "last_updated": self._timestamp(),
            "class_id": student.get("class_id"),
            "team_id": student.get("team_id"),
        }
        projects.append(new_project)
        self.save_projects(projects)
        return new_project
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
    def _add_project_notification(self, project, message):
        notifications = project.get("notifications", [])
        notifications.insert(0, f"{self._timestamp()} - {message}")
        project["notifications"] = notifications[:10]
    def update_project(self, project_id, updates, notification=None):
        projects = self.list_projects()
        for project in projects:
            if project["id"] == project_id:
                project.update(updates)
                project["last_updated"] = self._timestamp()
                if notification:
                    self._add_project_notification(project, notification)
                self.save_projects(projects)
                return project
        raise ValueError("Project not found.")
    def get_class_name(self, class_id):
        if not class_id:
            return "Not Assigned"
        class_record = self.find_class_by_id(class_id)
        if not class_record:
            return "Not Assigned"
        return f"{class_record['name']} ({class_record['term']})"
    def get_team_name(self, team_id):
        if not team_id:
            return "Not Assigned"
        team = self.find_team_by_id(team_id)
        if not team:
            return "Not Assigned"
        return team["name"]
