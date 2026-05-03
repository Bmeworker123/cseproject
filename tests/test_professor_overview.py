import sqlite3
import tempfile
import unittest

from tracker_app.app.dashboards.professor.pages.overview.overview import (
    ProfessorOverviewPage,
)
from tracker_app.app.dashboards.professor.pages.overview.components import (
    OverviewStatsCard,
)
from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor import ProfessorRepository


class DummyDashboard:
    def __init__(self, app):
        self.app = app


class ProfessorOverviewTests(unittest.TestCase):
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
        self.repo = ProfessorRepository(base_dir)
        self.app = type("App", (), {})()
        self.app.professor_repo = self.repo
        self.app.current_user = {"email": "teacher@example.com", "name": "Teacher One"}

        self.gateway.save_classes(
            [
                {
                    "id": 1,
                    "name": "CS 101",
                    "term": "Fall",
                    "teacher_email": "teacher@example.com",
                    "teacher_name": "Teacher One",
                    "created_at": "2026-05-02 10:00",
                }
            ]
        )
        self.gateway.save_teams(
            [
                {
                    "id": 10,
                    "class_id": 1,
                    "name": "Team Approved",
                    "member_ids": [1, 2],
                    "created_at": "2026-05-02 10:00",
                },
                {
                    "id": 11,
                    "class_id": 1,
                    "name": "Team Rejected",
                    "member_ids": [3, 4],
                    "created_at": "2026-05-02 10:00",
                },
                {
                    "id": 12,
                    "class_id": 1,
                    "name": "Team Pending",
                    "member_ids": [5, 6],
                    "created_at": "2026-05-02 10:00",
                },
                {
                    "id": 13,
                    "class_id": 1,
                    "name": "Team Empty",
                    "member_ids": [7, 8],
                    "created_at": "2026-05-02 10:00",
                },
            ]
        )
        self.gateway.save_projects(
            [
                {
                    "id": 1,
                    "team_id": 10,
                    "class_id": 1,
                    "title": "Approved",
                    "notes": "",
                    "approval_status": "Approved",
                    "last_updated": "2026-05-02 10:00",
                },
                {
                    "id": 2,
                    "team_id": 11,
                    "class_id": 1,
                    "title": "Rejected",
                    "notes": "",
                    "approval_status": "Rejected",
                    "last_updated": "2026-05-02 10:00",
                },
                {
                    "id": 3,
                    "team_id": 12,
                    "class_id": 1,
                    "title": "Pending",
                    "notes": "",
                    "approval_status": "Pending Approval",
                    "last_updated": "2026-05-02 10:00",
                },
            ]
        )

        self.page = ProfessorOverviewPage(DummyDashboard(self.app))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_project_status_breakdown_counts_each_bucket(self):
        self.assertEqual(
            self.page.project_status_breakdown(),
            {
                "No Project": 1,
                "Not Approved": 1,
                "Approved": 1,
                "Rejected": 1,
            },
        )

    def test_active_projects_only_count_teacher_classes(self):
        self.gateway.save_classes(
            self.gateway.list_classes()
            + [
                {
                    "id": 2,
                    "name": "CS 999",
                    "term": "Fall",
                    "teacher_email": "other@example.com",
                    "teacher_name": "Other Teacher",
                    "created_at": "2026-05-02 10:00",
                }
            ]
        )
        self.gateway.save_projects(
            self.gateway.list_projects()
            + [
                {
                    "id": 99,
                    "team_id": 999,
                    "class_id": 2,
                    "title": "Other Teacher Project",
                    "notes": "",
                    "approval_status": "Approved",
                    "last_updated": "2026-05-02 10:00",
                }
            ]
        )

        self.assertEqual(OverviewStatsCard.calculate_active_projects(self.page), 3)


if __name__ == "__main__":
    unittest.main()
