from abc import ABC, abstractmethod
from datetime import datetime


class Migration(ABC):
    name = ""

    @abstractmethod
    def up(self, db):
        raise NotImplementedError

    @abstractmethod
    def down(self, db):
        raise NotImplementedError


class SqlMigration(Migration):
    sql_up = ""
    sql_down = ""

    def up(self, db):
        db.executescript(self.sql_up)

    def down(self, db):
        db.executescript(self.sql_down)


class CreateUsersMigration(SqlMigration):
    name = "001_create_users"
    sql_up = """
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
    """
    sql_down = "DROP TABLE IF EXISTS users;"


class CreateClassesMigration(SqlMigration):
    name = "002_create_classes"
    sql_up = """
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        term TEXT NOT NULL,
        teacher_email TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """
    sql_down = "DROP TABLE IF EXISTS classes;"


class CreateTeamsMigration(SqlMigration):
    name = "003_create_teams"
    sql_up = """
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        class_id INTEGER,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """
    sql_down = "DROP TABLE IF EXISTS teams;"


class CreateTeamMembersMigration(SqlMigration):
    name = "004_create_team_members"
    sql_up = """
    CREATE TABLE IF NOT EXISTS team_members (
        team_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        PRIMARY KEY (team_id, student_id)
    );
    """
    sql_down = "DROP TABLE IF EXISTS team_members;"


class CreateProjectsMigration(SqlMigration):
    name = "005_create_projects"
    sql_up = """
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
    """
    sql_down = "DROP TABLE IF EXISTS projects;"


class CreateProjectNotificationsMigration(SqlMigration):
    name = "006_create_project_notifications"
    sql_up = """
    CREATE TABLE IF NOT EXISTS project_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_order INTEGER NOT NULL
    );
    """
    sql_down = "DROP TABLE IF EXISTS project_notifications;"


class TeamOwnedProjectsMigration(Migration):
    name = "007_team_owned_projects"

    def up(self, db):
        rows = db.execute("SELECT * FROM projects ORDER BY last_updated, id").fetchall()
        notifications = db.execute(
            "SELECT project_id, message, created_order FROM project_notifications ORDER BY project_id, created_order"
        ).fetchall()

        latest_by_team = {}
        unassigned = []
        for row in rows:
            project = dict(row)
            if project.get("team_id") is None:
                unassigned.append(project)
            else:
                latest_by_team[project["team_id"]] = project

        projects = list(latest_by_team.values()) + unassigned
        project_ids = {project["id"] for project in projects}

        db.execute("DROP TABLE IF EXISTS projects_new")
        db.execute(
            """
            CREATE TABLE projects_new (
                id INTEGER PRIMARY KEY,
                student_email TEXT NOT NULL,
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
                team_id INTEGER UNIQUE
            )
            """
        )

        for project in projects:
            db.execute(
                """
                INSERT INTO projects_new (
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
                project,
            )

        db.execute("DELETE FROM project_notifications")
        db.execute("DROP TABLE IF EXISTS projects")
        db.execute("ALTER TABLE projects_new RENAME TO projects")

        for row in notifications:
            if row["project_id"] in project_ids:
                db.execute(
                    "INSERT INTO project_notifications (project_id, message, created_order) VALUES (?, ?, ?)",
                    (row["project_id"], row["message"], row["created_order"]),
                )

    def down(self, db):
        rows = db.execute("SELECT * FROM projects ORDER BY last_updated, id").fetchall()
        notifications = db.execute(
            "SELECT project_id, message, created_order FROM project_notifications ORDER BY project_id, created_order"
        ).fetchall()

        latest_by_email = {}
        for row in rows:
            latest_by_email[row["student_email"]] = dict(row)

        projects = list(latest_by_email.values())
        project_ids = {project["id"] for project in projects}

        db.execute("DROP TABLE IF EXISTS projects_old")
        db.execute(
            """
            CREATE TABLE projects_old (
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
            )
            """
        )

        for project in projects:
            db.execute(
                """
                INSERT INTO projects_old (
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
                project,
            )

        db.execute("DELETE FROM project_notifications")
        db.execute("DROP TABLE IF EXISTS projects")
        db.execute("ALTER TABLE projects_old RENAME TO projects")

        for row in notifications:
            if row["project_id"] in project_ids:
                db.execute(
                    "INSERT INTO project_notifications (project_id, message, created_order) VALUES (?, ?, ?)",
                    (row["project_id"], row["message"], row["created_order"]),
                )


class Migrator:
    def __init__(self, connect_fn, migrations):
        self._connect_fn = connect_fn
        self._migrations = migrations

    def migrate_up(self):
        with self._connect_fn() as db:
            self._ensure_migration_table(db)
            applied = self._applied_migrations(db)
            for migration in self._migrations:
                if migration.name in applied:
                    continue
                migration.up(db)
                db.execute(
                    "INSERT INTO schema_migrations (name, applied_at) VALUES (?, ?)",
                    (migration.name, datetime.now().strftime("%Y-%m-%d %H:%M")),
                )

    def rollback_last(self):
        with self._connect_fn() as db:
            self._ensure_migration_table(db)
            last = db.execute(
                "SELECT name FROM schema_migrations ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if not last:
                return
            name = last["name"]
            migration = next((m for m in self._migrations if m.name == name), None)
            if not migration:
                return
            migration.down(db)
            db.execute("DELETE FROM schema_migrations WHERE name = ?", (name,))

    def _ensure_migration_table(self, db):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                applied_at TEXT NOT NULL
            )
            """
        )

    def _applied_migrations(self, db):
        rows = db.execute("SELECT name FROM schema_migrations").fetchall()
        return {row["name"] for row in rows}


def default_migrations():
    return [
        CreateUsersMigration(),
        CreateClassesMigration(),
        CreateTeamsMigration(),
        CreateTeamMembersMigration(),
        CreateProjectsMigration(),
        CreateProjectNotificationsMigration(),
        TeamOwnedProjectsMigration(),
    ]
