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
            existing_ids = {
                row["id"] for row in db.execute("SELECT id FROM users").fetchall()
            }
            current_ids = {user.get("id") for user in users}

            for user_id in existing_ids - current_ids:
                db.execute("DELETE FROM users WHERE id = ?", (user_id,))

            for user in users:
                clean = self.user_defaults(user)
                db.execute(
                    """
                    INSERT INTO users (
                        id, name, email, password_hash, role, status, created_at, last_login,
                        student_id, department, notes, class_id, team_id
                    )
                    VALUES (
                        :id, :name, :email, :password_hash, :role, :status, :created_at, :last_login,
                        :student_id, :department, :notes, :class_id, :team_id
                    )
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        email = excluded.email,
                        password_hash = excluded.password_hash,
                        role = excluded.role,
                        status = excluded.status,
                        created_at = excluded.created_at,
                        last_login = excluded.last_login,
                        student_id = excluded.student_id,
                        department = excluded.department,
                        notes = excluded.notes,
                        class_id = excluded.class_id,
                        team_id = excluded.team_id
                    """,
                    clean,
                )

    def list_projects(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM projects ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def list_projects_for_teacher(self, teacher_email):
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT p.*
                FROM projects p
                INNER JOIN classes c ON c.id = p.class_id
                WHERE c.teacher_email = ?
                ORDER BY p.id
                """,
                (teacher_email,),
            ).fetchall()
        return [dict(row) for row in rows]

    def count_projects_for_teacher(self, teacher_email):
        with self._connect() as db:
            row = db.execute(
                """
                SELECT COUNT(*) AS total
                FROM projects p
                INNER JOIN classes c ON c.id = p.class_id
                WHERE c.teacher_email = ?
                """,
                (teacher_email,),
            ).fetchone()
        return int(row["total"] if row else 0)

    def save_projects(self, projects):
        with self._connect() as db:
            existing_ids = {
                row["id"] for row in db.execute("SELECT id FROM projects").fetchall()
            }
            current_ids = {project.get("id") for project in projects}

            for project_id in existing_ids - current_ids:
                db.execute("DELETE FROM projects WHERE id = ?", (project_id,))

            for project in projects:
                clean = self.project_defaults(project)
                db.execute(
                    """
                    INSERT INTO projects (id, team_id, class_id, title, notes, approval_status, last_updated)
                    VALUES (:id, :team_id, :class_id, :title, :notes, :approval_status, :last_updated)
                    ON CONFLICT(id) DO UPDATE SET
                        team_id = excluded.team_id,
                        class_id = excluded.class_id,
                        title = excluded.title,
                        notes = excluded.notes,
                        approval_status = excluded.approval_status,
                        last_updated = excluded.last_updated
                    """,
                    clean,
                )

    def list_classes(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM classes ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def list_classes_for_teacher(self, teacher_email):
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM classes WHERE teacher_email = ? ORDER BY id",
                (teacher_email,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_class_by_id(self, class_id):
        with self._connect() as db:
            row = db.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        return dict(row) if row else None

    def delete_class(self, class_id):
        with self._connect() as db:
            class_row = db.execute(
                "SELECT * FROM classes WHERE id = ?", (class_id,)
            ).fetchone()
            if not class_row:
                return None

            db.execute(
                "UPDATE users SET class_id = NULL, team_id = NULL WHERE class_id = ?",
                (class_id,),
            )
            notifications_table = db.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'project_notifications'
                """
            ).fetchone()
            if notifications_table:
                db.execute(
                    """
                    DELETE FROM project_notifications
                    WHERE project_id IN (
                        SELECT p.id
                        FROM projects p
                        LEFT JOIN teams t ON t.id = p.team_id
                        WHERE p.class_id = ? OR t.class_id = ?
                    )
                    """,
                    (class_id, class_id),
                )
            db.execute(
                """
                DELETE FROM projects
                WHERE class_id = ?
                   OR team_id IN (
                       SELECT id FROM teams WHERE class_id = ?
                   )
                """,
                (class_id, class_id),
            )
            db.execute(
                """
                DELETE FROM team_members
                WHERE team_id IN (
                    SELECT id FROM teams WHERE class_id = ?
                )
                """,
                (class_id,),
            )
            db.execute("DELETE FROM teams WHERE class_id = ?", (class_id,))
            db.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        return dict(class_row)

    def save_classes(self, classes):
        with self._connect() as db:
            existing_ids = {
                row["id"] for row in db.execute("SELECT id FROM classes").fetchall()
            }
            current_ids = {item.get("id") for item in classes}

            for class_id in existing_ids - current_ids:
                db.execute("DELETE FROM classes WHERE id = ?", (class_id,))

            for item in classes:
                clean = self.class_defaults(item)
                db.execute(
                    """
                    INSERT INTO classes (id, name, term, teacher_email, teacher_name, created_at)
                    VALUES (:id, :name, :term, :teacher_email, :teacher_name, :created_at)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        term = excluded.term,
                        teacher_email = excluded.teacher_email,
                        teacher_name = excluded.teacher_name,
                        created_at = excluded.created_at
                    """,
                    clean,
                )

    def list_teams(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM teams ORDER BY id").fetchall()
            members = db.execute(
                "SELECT team_id, student_id FROM team_members ORDER BY team_id, student_id"
            ).fetchall()
        grouped = {}
        for row in members:
            grouped.setdefault(row["team_id"], []).append(row["student_id"])
        teams = []
        for row in rows:
            team = dict(row)
            team["member_ids"] = grouped.get(team["id"], [])
            teams.append(team)
        return teams

    def list_teams_for_class(self, class_id):
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM teams WHERE class_id = ? ORDER BY id", (class_id,)
            ).fetchall()
            team_ids = [row["id"] for row in rows]
            if not team_ids:
                return []
            placeholders = ",".join(["?"] * len(team_ids))
            members = db.execute(
                f"""
                SELECT team_id, student_id
                FROM team_members
                WHERE team_id IN ({placeholders})
                ORDER BY team_id, student_id
                """,
                tuple(team_ids),
            ).fetchall()

        grouped = {}
        for row in members:
            grouped.setdefault(row["team_id"], []).append(row["student_id"])

        teams = []
        for row in rows:
            team = dict(row)
            team["member_ids"] = grouped.get(team["id"], [])
            teams.append(team)
        return teams

    def list_teams_for_teacher(self, teacher_email):
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT t.*
                FROM teams t
                INNER JOIN classes c ON c.id = t.class_id
                WHERE c.teacher_email = ?
                ORDER BY t.id
                """,
                (teacher_email,),
            ).fetchall()
            team_ids = [row["id"] for row in rows]
            if not team_ids:
                return []
            placeholders = ",".join(["?"] * len(team_ids))
            members = db.execute(
                f"""
                SELECT team_id, student_id
                FROM team_members
                WHERE team_id IN ({placeholders})
                ORDER BY team_id, student_id
                """,
                tuple(team_ids),
            ).fetchall()

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
            existing_ids = {
                row["id"] for row in db.execute("SELECT id FROM teams").fetchall()
            }
            current_ids = {team.get("id") for team in teams}

            for team_id in existing_ids - current_ids:
                db.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
                db.execute("DELETE FROM teams WHERE id = ?", (team_id,))

            for team in teams:
                clean = self.team_defaults(team)
                db.execute(
                    """
                    INSERT INTO teams (id, class_id, name, created_at)
                    VALUES (:id, :class_id, :name, :created_at)
                    ON CONFLICT(id) DO UPDATE SET
                        class_id = excluded.class_id,
                        name = excluded.name,
                        created_at = excluded.created_at
                    """,
                    clean,
                )
                db.execute("DELETE FROM team_members WHERE team_id = ?", (clean["id"],))
                for student_id in clean["member_ids"]:
                    db.execute(
                        "INSERT INTO team_members (team_id, student_id) VALUES (?, ?)",
                        (clean["id"], student_id),
                    )

    def user_defaults(self, user):
        email = user.get("email", "").strip().lower()
        default_name = (
            email.split("@")[0].replace(".", " ").title() if email else "User"
        )
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
            "team_id": project.get("team_id"),
            "class_id": project.get("class_id"),
            "title": project.get("title", ""),
            "notes": project.get("notes") or "",
            "approval_status": project.get(
                "approval_status", project.get("status", "Pending Approval")
            ),
            "last_updated": project.get("last_updated") or self.timestamp(),
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
