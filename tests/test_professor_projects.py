import sqlite3
import tempfile
import unittest

from tracker_app.migrations import Migrator, default_migrations
from tracker_app.repositories.common.sqlite_gateway import SqliteGateway
from tracker_app.repositories.professor.projects import ProfessorProjectRepository


class ProfessorProjectRepositoryTests(unittest.TestCase):
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
        self.repo = ProfessorProjectRepository(base_dir)

        self.project = {
            "id": 1,
            "team_id": 10,
            "class_id": 1,
            "title": "Project Alpha",
            "notes": "Notes",
            "approval_status": "Pending Approval",
            "last_updated": "2026-05-02 10:00",
        }
        self.gateway.save_projects([self.project])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_update_project_sets_rejected_status(self):
        updated = self.repo.update_project(1, {"approval_status": "Rejected"})

        self.assertEqual(updated["approval_status"], "Rejected")
        self.assertNotEqual(updated["last_updated"], "2026-05-02 10:00")
        self.assertEqual(self.gateway.list_projects()[0]["approval_status"], "Rejected")


if __name__ == "__main__":
    unittest.main()
