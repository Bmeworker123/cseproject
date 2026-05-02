import hashlib
import hmac
import os
import sqlite3
from datetime import datetime


class SqliteGateway:
    def __init__(self, base_dir):
        self.data_dir = os.path.join(base_dir, "data")
        self.db_path = os.path.join(self.data_dir, "project_tracker.sqlite3")
        os.makedirs(self.data_dir, exist_ok=True)

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def next_id(self, records):
        if not records:
            return 1
        return max(record["id"] for record in records) + 1

    def hash_password(self, password):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return f"{salt.hex()}:{digest.hex()}"

    def verify_password(self, password, stored_hash):
        try:
            salt_hex, digest_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_digest = bytes.fromhex(digest_hex)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return hmac.compare_digest(digest, expected_digest)

    def list_users(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [dict(row) for row in rows]

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
                [self.user_defaults(user) for user in users],
            )

    def list_projects(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM projects ORDER BY id").fetchall()
            notifications = db.execute(
                "SELECT project_id, message FROM project_notifications ORDER BY project_id, created_order"
            ).fetchall()
        grouped = {}
        for row in notifications:
            grouped.setdefault(row["project_id"], []).append(row["message"])
        projects = []
        for row in rows:
            project = dict(row)
            project["notifications"] = grouped.get(project["id"], [])
            projects.append(project)
        return projects

    def save_projects(self, projects):
        with self._connect() as db:
            db.execute("DELETE FROM project_notifications")
            db.execute("DELETE FROM projects")
            for project in projects:
                clean = self.project_defaults(project)
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
                    clean,
                )
                for index, message in enumerate(clean["notifications"]):
                    db.execute(
                        "INSERT INTO project_notifications (project_id, message, created_order) VALUES (?, ?, ?)",
                        (clean["id"], message, index),
                    )

    def list_classes(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM classes ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def save_classes(self, classes):
        with self._connect() as db:
            db.execute("DELETE FROM classes")
            db.executemany(
                "INSERT INTO classes (id, name, term, teacher_email, teacher_name, created_at) VALUES (:id, :name, :term, :teacher_email, :teacher_name, :created_at)",
                [self.class_defaults(item) for item in classes],
            )

    def list_teams(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM teams ORDER BY id").fetchall()
            members = db.execute("SELECT team_id, student_id FROM team_members ORDER BY team_id, student_id").fetchall()
        grouped = {}
        for row in members:
            grouped.setdefault(row["team_id"], []).append(row["student_id"])
        teams = []
        for row in rows:
            team = dict(row)
            team["member_ids"] = grouped.get(team["id"], [])
            teams.append(team)
        return teams

    def save_teams(self, teams):
        with self._connect() as db:
            db.execute("DELETE FROM team_members")
            db.execute("DELETE FROM teams")
            for team in teams:
                clean = self.team_defaults(team)
                db.execute(
                    "INSERT INTO teams (id, class_id, name, created_at) VALUES (:id, :class_id, :name, :created_at)",
                    clean,
                )
                for student_id in clean["member_ids"]:
                    db.execute("INSERT INTO team_members (team_id, student_id) VALUES (?, ?)", (clean["id"], student_id))

    def user_defaults(self, user):
        email = user.get("email", "").strip().lower()
        default_name = email.split("@")[0].replace(".", " ").title() if email else "User"
        return {
            "id": user.get("id"),
            "name": user.get("name") or default_name,
            "email": email,
            "password_hash": user.get("password_hash", ""),
            "role": user.get("role", "student"),
            "status": user.get("status", "Active"),
            "created_at": user.get("created_at") or self.timestamp(),
            "last_login": user.get("last_login", ""),
            "student_id": user.get("student_id", ""),
            "department": user.get("department", ""),
            "notes": user.get("notes", ""),
            "class_id": user.get("class_id"),
            "team_id": user.get("team_id"),
        }

    def project_defaults(self, project):
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
            "last_updated": project.get("last_updated") or self.timestamp(),
            "class_id": project.get("class_id"),
            "team_id": project.get("team_id"),
            "notifications": project.get("notifications", []),
        }

    def class_defaults(self, item):
        return {
            "id": item.get("id"),
            "name": item.get("name", ""),
            "term": item.get("term", ""),
            "teacher_email": item.get("teacher_email", ""),
            "teacher_name": item.get("teacher_name", ""),
            "created_at": item.get("created_at") or self.timestamp(),
        }

    def team_defaults(self, item):
        return {
            "id": item.get("id"),
            "class_id": item.get("class_id"),
            "name": item.get("name", ""),
            "member_ids": item.get("member_ids", []),
            "created_at": item.get("created_at") or self.timestamp(),
        }

    def add_project_notification(self, project, message):
        notifications = project.get("notifications", [])
        notifications.insert(0, f"{self.timestamp()} - {message}")
        project["notifications"] = notifications[:10]
