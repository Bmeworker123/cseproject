import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.student.users import StudentUserRepository


class StudentUserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        base_dir = self.tempdir.name
        self.gateway = SqliteGateway(base_dir)

        def connect():
            connection = sqlite3.connect(self.gateway.db_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            return connection

        Migrator(connect, default_migrations()).migrate_up()
        self.repo = StudentUserRepository(base_dir)

        self.users = [
            {
                "id": 1,
                "name": "Student One",
                "email": "student1@example.com",
                "password_hash": "hash",
                "role": "student",
                "status": "Active",
                "created_at": "2026-05-02 10:00",
                "last_login": "",
                "student_id": "S-1",
                "department": "CS",
                "notes": "",
                "class_id": 1,
                "team_id": 10,
            },
            {
                "id": 2,
                "name": "Student Two",
                "email": "student2@example.com",
                "password_hash": "hash",
                "role": "student",
                "status": "Active",
                "created_at": "2026-05-02 10:01",
                "last_login": "",
                "student_id": "S-2",
                "department": "CS",
                "notes": "",
                "class_id": 1,
                "team_id": 10,
            },
            {
                "id": 3,
                "name": "Student Three",
                "email": "student3@example.com",
                "password_hash": "hash",
                "role": "student",
                "status": "Active",
                "created_at": "2026-05-02 10:02",
                "last_login": "",
                "student_id": "S-3",
                "department": "CS",
                "notes": "",
                "class_id": 1,
                "team_id": 20,
            },
        ]
        self.gateway.save_users(self.users)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_teammate_names_excludes_current_student_and_other_teams(self):
        user = self.repo.refresh_user(1)

        self.assertEqual(self.repo.teammate_names(user), ["Student Two"])

    def test_teammate_names_returns_empty_for_unassigned_team(self):
        user = self.repo.refresh_user(1)
        user["team_id"] = None

        self.assertEqual(self.repo.teammate_names(user), [])


if __name__ == "__main__":
    unittest.main()
