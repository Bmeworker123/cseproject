import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor.users import ProfessorUserRepository
from tracker_app.repositories.student.projects import StudentProjectRepository


class StudentProjectRepositoryTests(unittest.TestCase):
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
        self.student_repo = StudentProjectRepository(base_dir)
        self.professor_user_repo = ProfessorUserRepository(base_dir)

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
        self.gateway.save_users([self.user])
        self.gateway.save_projects([
            {
                "id": 1,
                "team_id": 10,
                "class_id": 1,
                "title": "Team 10 Project",
                "notes": "Notes",
                "approval_status": "Pending Approval",
                "last_updated": "2026-05-02 10:00",
            }
        ])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_project_is_team_scoped(self):
        project = self.student_repo.project_for(self.user)
        self.assertIsNotNone(project)
        self.assertEqual(project["team_id"], 10)

        updated_user = self.professor_user_repo.update_user(1, {"team_id": 20})
        self.assertIsNone(self.student_repo.project_for(updated_user))

        new_project = self.student_repo.save_project(
            updated_user,
            "Team 20 Project",
            "New notes",
        )

        projects = self.gateway.list_projects()
        self.assertEqual(len(projects), 2)
        self.assertEqual(new_project["team_id"], 20)
        self.assertEqual({project["team_id"] for project in projects}, {10, 20})

    def test_save_project_rejects_students_without_team(self):
        unassigned_user = dict(self.user)
        unassigned_user["team_id"] = None

        with self.assertRaises(ValueError):
            self.student_repo.save_project(unassigned_user, "Orphan Project", "Notes")


if __name__ == "__main__":
    unittest.main()
