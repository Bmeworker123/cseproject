import os
import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor.users import ProfessorUserRepository


class ProfessorUserRepositoryTests(unittest.TestCase):
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
        self.repo = ProfessorUserRepository(base_dir)

        self.user = {
            "id": 1,
            "name": "Student One",
            "email": "student@example.com",
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
        }
        self.project = {
            "id": 1,
            "team_id": 10,
            "class_id": 1,
            "title": "Project Alpha",
            "notes": "Notes",
            "approval_status": "Pending Approval",
            "last_updated": "2026-05-02 10:00",
        }
        self.gateway.save_users([self.user])
        self.gateway.save_projects([self.project])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_team_change_does_not_move_project(self):
        updated = self.repo.update_user(1, {"team_id": 20})

        project = self.gateway.list_projects()[0]

        self.assertEqual(updated["team_id"], 20)
        self.assertEqual(project["team_id"], 10)


if __name__ == "__main__":
    unittest.main()
