import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor.reports import ProfessorReportRepository


class ProfessorReportRepositoryTests(unittest.TestCase):
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
        self.repo = ProfessorReportRepository(base_dir)

        self.gateway.save_classes(
            [
                {
                    "id": 1,
                    "name": "CS 101",
                    "term": "Fall",
                    "teacher_email": "teacher@example.com",
                    "teacher_name": "Teacher One",
                    "created_at": "2026-05-04 10:00",
                }
            ]
        )
        self.gateway.save_teams(
            [
                {
                    "id": 10,
                    "class_id": 1,
                    "name": "Team A",
                    "member_ids": [1, 2],
                    "created_at": "2026-05-04 10:00",
                },
                {
                    "id": 11,
                    "class_id": 1,
                    "name": "Team B",
                    "member_ids": [3],
                    "created_at": "2026-05-04 10:00",
                },
            ]
        )
        self.gateway.save_users(
            [
                {
                    "id": 1,
                    "name": "Alice",
                    "email": "alice@example.com",
                    "password_hash": "x",
                    "role": "student",
                    "status": "Active",
                    "created_at": "2026-05-04 10:00",
                    "class_id": 1,
                    "team_id": 10,
                },
                {
                    "id": 2,
                    "name": "Bob",
                    "email": "bob@example.com",
                    "password_hash": "x",
                    "role": "student",
                    "status": "Active",
                    "created_at": "2026-05-04 10:00",
                    "class_id": 1,
                    "team_id": 10,
                },
                {
                    "id": 3,
                    "name": "Cara",
                    "email": "cara@example.com",
                    "password_hash": "x",
                    "role": "student",
                    "status": "Active",
                    "created_at": "2026-05-04 10:00",
                    "class_id": 1,
                    "team_id": 11,
                },
            ]
        )
        self.gateway.save_projects(
            [
                {
                    "id": 1,
                    "team_id": 10,
                    "class_id": 1,
                    "title": "Project A",
                    "notes": "",
                    "approval_status": "Approved",
                    "last_updated": "2026-05-04 10:00",
                }
            ]
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_combined_workflow_rows_include_student_team_project(self):
        rows = self.repo.list_combined_workflow_rows("teacher@example.com")

        self.assertEqual(len(rows), 3)
        alice = next(row for row in rows if row["student_name"] == "Alice")
        cara = next(row for row in rows if row["student_name"] == "Cara")

        self.assertEqual(alice["team_name"], "Team A")
        self.assertEqual(alice["project_title"], "Project A")
        self.assertEqual(alice["approval_status"], "Approved")
        self.assertEqual(cara["project_title"], "No Project")
        self.assertEqual(cara["approval_status"], "No Project")

    def test_project_status_counts(self):
        counts = self.repo.project_status_counts("teacher@example.com")

        self.assertEqual(
            counts,
            {
                "No Project": 1,
                "Pending Approval": 0,
                "Approved": 1,
                "Rejected": 0,
            },
        )

    def test_team_size_and_coverage(self):
        team_sizes = dict(self.repo.team_sizes_by_class("teacher@example.com"))
        coverage = self.repo.team_project_coverage("teacher@example.com")

        self.assertEqual(team_sizes["CS 101 (Fall) / Team A"], 2)
        self.assertEqual(team_sizes["CS 101 (Fall) / Team B"], 1)
        self.assertEqual(coverage, {"With Project": 1, "Without Project": 1})


if __name__ == "__main__":
    unittest.main()
