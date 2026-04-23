import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime


class DataStore:
    def __init__(self, base_dir):
        self.data_dir = os.path.join(base_dir, "data")
        self.db_path = os.path.join(self.data_dir, "project_tracker.sqlite3")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.classes_file = os.path.join(self.data_dir, "classes.json")
        self.teams_file = os.path.join(self.data_dir, "teams.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._create_tables()
        self._migrate_json_files()
        self.migrate_data()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _create_tables(self):
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    student_id TEXT,
                    department TEXT,
                    notes TEXT,
                    class_id INTEGER,
                    team_id INTEGER
                );

                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    term TEXT NOT NULL,
                    teacher_email TEXT NOT NULL,
                    teacher_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    class_id INTEGER,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS team_members (
                    team_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    PRIMARY KEY (team_id, student_id)
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    student_email TEXT NOT NULL UNIQUE,
                    student_name TEXT NOT NULL,
                    student_id TEXT,
                    department TEXT,
                    title TEXT NOT NULL,
                    notes TEXT,
                    progress INTEGER NOT NULL,
                    requested_progress INTEGER,
                    progress_request_status TEXT NOT NULL,
                    status TEXT NOT NULL,
                    professor_notes TEXT,
                    stage TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    meeting_status TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    class_id INTEGER,
                    team_id INTEGER
                );

                CREATE TABLE IF NOT EXISTS project_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    created_order INTEGER NOT NULL
                );
                """
            )

    def _migrate_json_files(self):
        if self.list_users() or self.list_projects() or self.list_classes() or self.list_teams():
            return
        if os.path.exists(self.users_file):
            self.save_users(self._read_json_file(self.users_file))
        if os.path.exists(self.classes_file):
            self.save_classes(self._read_json_file(self.classes_file))
        if os.path.exists(self.teams_file):
            self.save_teams(self._read_json_file(self.teams_file))
        if os.path.exists(self.projects_file):
            self.save_projects(self._read_json_file(self.projects_file))

    def _read_json_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

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

    def _row_to_dict(self, row):
        return dict(row)

    def list_users(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [self._row_to_dict(row) for row in rows]

    def save_users(self, users):
        with self._connect() as db:
            db.execute("DELETE FROM users")
            db.executemany(
                """
                INSERT INTO users (
                    id, name, email, password_hash, role, status, created_at, last_login,
                    student_id, department, notes, class_id, team_id
                )
                VALUES (
                    :id, :name, :email, :password_hash, :role, :status, :created_at, :last_login,
                    :student_id, :department, :notes, :class_id, :team_id
                )
                """,
                [self._user_defaults(user) for user in users],
            )

    def list_projects(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM projects ORDER BY id").fetchall()
            notifications = db.execute(
                "SELECT project_id, message FROM project_notifications ORDER BY project_id, created_order"
            ).fetchall()
        grouped_notifications = {}
        for row in notifications:
            grouped_notifications.setdefault(row["project_id"], []).append(row["message"])
        projects = []
        for row in rows:
            project = self._row_to_dict(row)
            project["notifications"] = grouped_notifications.get(project["id"], [])
            projects.append(project)
        return projects

    def save_projects(self, projects):
        with self._connect() as db:
            db.execute("DELETE FROM project_notifications")
            db.execute("DELETE FROM projects")
            for project in projects:
                clean_project = self._project_defaults(project)
                db.execute(
                    """
                    INSERT INTO projects (
                        id, student_email, student_name, student_id, department, title, notes,
                        progress, requested_progress, progress_request_status, status,
                        professor_notes, stage, priority, meeting_status, last_updated,
                        class_id, team_id
                    )
                    VALUES (
                        :id, :student_email, :student_name, :student_id, :department, :title, :notes,
                        :progress, :requested_progress, :progress_request_status, :status,
                        :professor_notes, :stage, :priority, :meeting_status, :last_updated,
                        :class_id, :team_id
                    )
                    """,
                    clean_project,
                )
                for index, message in enumerate(clean_project["notifications"]):
                    db.execute(
                        """
                        INSERT INTO project_notifications (project_id, message, created_order)
                        VALUES (?, ?, ?)
                        """,
                        (clean_project["id"], message, index),
                    )

    def list_classes(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM classes ORDER BY id").fetchall()
        return [self._row_to_dict(row) for row in rows]

    def save_classes(self, classes):
        with self._connect() as db:
            db.execute("DELETE FROM classes")
            db.executemany(
                """
                INSERT INTO classes (id, name, term, teacher_email, teacher_name, created_at)
                VALUES (:id, :name, :term, :teacher_email, :teacher_name, :created_at)
                """,
                [self._class_defaults(item) for item in classes],
            )

    def list_teams(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM teams ORDER BY id").fetchall()
            members = db.execute(
                "SELECT team_id, student_id FROM team_members ORDER BY team_id, student_id"
            ).fetchall()
        grouped_members = {}
        for row in members:
            grouped_members.setdefault(row["team_id"], []).append(row["student_id"])
        teams = []
        for row in rows:
            team = self._row_to_dict(row)
            team["member_ids"] = grouped_members.get(team["id"], [])
            teams.append(team)
        return teams

    def save_teams(self, teams):
        with self._connect() as db:
            db.execute("DELETE FROM team_members")
            db.execute("DELETE FROM teams")
            for team in teams:
                clean_team = self._team_defaults(team)
                db.execute(
                    """
                    INSERT INTO teams (id, class_id, name, created_at)
                    VALUES (:id, :class_id, :name, :created_at)
                    """,
                    clean_team,
                )
                for student_id in clean_team["member_ids"]:
                    db.execute(
                        "INSERT INTO team_members (team_id, student_id) VALUES (?, ?)",
                        (clean_team["id"], student_id),
                    )

    def _user_defaults(self, user):
        email = user.get("email", "").strip().lower()
        default_name = email.split("@")[0].replace(".", " ").title() if email else "User"
        return {
            "id": user.get("id"),
            "name": user.get("name") or default_name,
            "email": email,
            "password_hash": user.get("password_hash", ""),
            "role": user.get("role", "student"),
            "status": user.get("status", "Active"),
            "created_at": user.get("created_at") or self._timestamp(),
            "last_login": user.get("last_login", ""),
            "student_id": user.get("student_id", ""),
            "department": user.get("department", ""),
            "notes": user.get("notes", ""),
            "class_id": user.get("class_id"),
            "team_id": user.get("team_id"),
        }

    def _project_defaults(self, project):
        return {
            "id": project.get("id"),
            "student_email": project.get("student_email", ""),
            "student_name": project.get("student_name", ""),
            "student_id": project.get("student_id", ""),
            "department": project.get("department", ""),
            "title": project.get("title", ""),
            "notes": project.get("notes") or "No notes yet.",
            "progress": int(project.get("progress", 0)),
            "requested_progress": project.get("requested_progress"),
            "progress_request_status": project.get("progress_request_status", "None"),
            "status": project.get("status", "Pending Approval"),
            "professor_notes": project.get("professor_notes", "Awaiting professor review."),
            "stage": project.get("stage", "Proposal"),
            "priority": project.get("priority", "Medium"),
            "meeting_status": project.get("meeting_status", "Not Scheduled"),
            "last_updated": project.get("last_updated") or self._timestamp(),
            "class_id": project.get("class_id"),
            "team_id": project.get("team_id"),
            "notifications": project.get("notifications", []),
        }

    def _class_defaults(self, item):
        return {
            "id": item.get("id"),
            "name": item.get("name", ""),
            "term": item.get("term", ""),
            "teacher_email": item.get("teacher_email", ""),
            "teacher_name": item.get("teacher_name", ""),
            "created_at": item.get("created_at") or self._timestamp(),
        }

    def _team_defaults(self, item):
        return {
            "id": item.get("id"),
            "class_id": item.get("class_id"),
            "name": item.get("name", ""),
            "member_ids": item.get("member_ids", []),
            "created_at": item.get("created_at") or self._timestamp(),
        }

    def migrate_data(self):
        self.save_users([self._user_defaults(user) for user in self.list_users()])
        self.save_projects([self._project_defaults(project) for project in self.list_projects()])
        self.save_classes([self._class_defaults(item) for item in self.list_classes()])
        self.save_teams([self._team_defaults(item) for item in self.list_teams()])

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
