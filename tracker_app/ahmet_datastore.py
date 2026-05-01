import sqlite3
import os
import json
from datetime import datetime
from .migrations import DataMigration


class AhmetDataStore:
    def __init__(self, base_dir):
        self.data_dir = os.path.join(base_dir, "data")
        self.db_path = os.path.join(self.data_dir, "project_tracker.sqlite3")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.classes_file = os.path.join(self.data_dir, "classes.json")
        self.teams_file = os.path.join(self.data_dir, "teams.json")
        os.makedirs(self.data_dir, exist_ok=True)
        DataMigration(self).run_all()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def get_version(self):
        with self._connect() as db:
            return db.execute("PRAGMA user_version").fetchone()[0]

    def set_version(self, version):
        with self._connect() as db:
            db.execute(f"PRAGMA user_version = {version}")

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _next_id(self, records):
        if not records:
            return 1
        return max(record["id"] for record in records) + 1

    def _row_to_dict(self, row):
        d = dict(row)
        if "status" in d:
            d["account_status"] = d["status"]
        if "notes" in d:
            d["teacher_notes"] = d["notes"]
        if "last_updated" in d:
            d["updated_at"] = d["last_updated"]
        return d

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
            "status": user.get("status") or user.get("account_status", "Active"),
            "created_at": user.get("created_at") or self._timestamp(),
            "last_login": user.get("last_login", ""),
            "student_id": user.get("student_id", ""),
            "department": user.get("department", ""),
            "notes": user.get("notes") or user.get("teacher_notes", ""),
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
            "last_updated": project.get("last_updated") or project.get("updated_at") or self._timestamp(),
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

    def get_class_name(self, class_id):
        if not class_id:
            return "Not Assigned"
        with self._connect() as db:
            row = db.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        if not row:
            return "Not Assigned"
        class_record = self._row_to_dict(row)
        return f"{class_record['name']} ({class_record['term']})"

    def get_team_name(self, team_id):
        if not team_id:
            return "Not Assigned"
        with self._connect() as db:
            row = db.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
        if not row:
            return "Not Assigned"
        team = self._row_to_dict(row)
        return team["name"]

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
