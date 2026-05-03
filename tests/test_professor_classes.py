import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor.classes import ProfessorClassRepository


class ProfessorClassRepositoryTests(unittest.TestCase):
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
        self.repo = ProfessorClassRepository(base_dir)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_delete_class_removes_projects_for_deleted_teams(self):
        self.gateway.save_classes(
            [
                {
                    "id": 1,
                    "name": "CS 101",
                    "term": "Fall",
                    "teacher_email": "teacher@example.com",
                    "teacher_name": "Teacher",
                    "created_at": "2026-05-02 10:00",
                },
                {
                    "id": 2,
                    "name": "CS 102",
                    "term": "Fall",
                    "teacher_email": "teacher@example.com",
                    "teacher_name": "Teacher",
                    "created_at": "2026-05-02 10:00",
                },
            ]
        )
        self.gateway.save_teams(
            [
                {
                    "id": 10,
                    "class_id": 1,
                    "name": "Team A",
                    "member_ids": [1],
                    "created_at": "2026-05-02 10:00",
                },
                {
                    "id": 20,
                    "class_id": 2,
                    "name": "Team B",
                    "member_ids": [2],
                    "created_at": "2026-05-02 10:00",
                },
            ]
        )
        self.gateway.save_users(
            [
                {
                    "id": 1,
                    "name": "Student One",
                    "email": "s1@example.com",
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
            ]
        )
        self.gateway.save_projects(
            [
                {
                    "id": 1,
                    "team_id": 10,
                    "class_id": None,
                    "title": "Project Team A",
                    "notes": "",
                    "approval_status": "Pending Approval",
                    "last_updated": "2026-05-02 10:00",
                },
                {
                    "id": 2,
                    "team_id": 20,
                    "class_id": 2,
                    "title": "Project Team B",
                    "notes": "",
                    "approval_status": "Pending Approval",
                    "last_updated": "2026-05-02 10:00",
                },
            ]
        )

        self.repo.delete_class(1)

        projects = self.gateway.list_projects()
        users = self.gateway.list_users()

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["id"], 2)
        self.assertIsNone(users[0]["class_id"])
        self.assertIsNone(users[0]["team_id"])


if __name__ == "__main__":
    unittest.main()
