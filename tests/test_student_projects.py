import tempfile
import unittest

from tracker_app.repositories.auth import AuthRepository
from tracker_app.repositories.professor.classes import ProfessorClassRepository
from tracker_app.repositories.professor.teams import ProfessorTeamRepository
from tracker_app.repositories.professor.users import ProfessorUserRepository
from tracker_app.repositories.student import StudentRepository


class StudentProjectRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        base_dir = self.tempdir.name
        self.auth_repo = AuthRepository(base_dir)
        self.class_repo = ProfessorClassRepository(base_dir)
        self.team_repo = ProfessorTeamRepository(base_dir)
        self.professor_user_repo = ProfessorUserRepository(base_dir)
        self.student_repo = StudentRepository(base_dir)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_personal_project_fallback_without_team(self):
        student = self.auth_repo.create_account(
            "Student One",
            "student@example.com",
            "secret123",
            "student",
            student_id="S-1",
            department="CS",
        )

        saved = self.student_repo.save_project(
            student,
            "Solo Project",
            "Initial notes",
            15,
            "Medium",
        )
        loaded = self.student_repo.project_for(student)

        self.assertIsNotNone(loaded)
        self.assertEqual(saved["id"], loaded["id"])
        self.assertIsNone(loaded["team_id"])
        self.assertEqual(loaded["student_email"], "student@example.com")

    def test_duplicate_progress_request_is_not_added_twice(self):
        professor = self.auth_repo.create_account("Prof One", "prof@example.com", "secret123", "professor")
        student = self.auth_repo.create_account(
            "Student One",
            "student@example.com",
            "secret123",
            "student",
            student_id="S-1",
            department="CS",
        )
        klass = self.class_repo.create_class(professor, "Senior Design", "Spring 2026")
        team = self.team_repo.create_team(klass["id"], "Team A")
        self.professor_user_repo.update_user(student["id"], {"class_id": klass["id"], "team_id": team["id"]})
        student = self.professor_user_repo.refresh_user(student["id"])

        self.student_repo.save_project(student, "Team Project", "Initial notes", 10, "Medium")
        first_update = self.student_repo.save_project(student, "Team Project", "Initial notes", 35, "Medium")
        second_update = self.student_repo.save_project(student, "Team Project", "Initial notes", 35, "Medium")

        matching = [
            note for note in second_update["notifications"] if "Your progress change to 35% was sent" in note
        ]
        self.assertEqual(1, len(matching))
        self.assertEqual(35, first_update["requested_progress"])
        self.assertEqual(35, second_update["requested_progress"])
        self.assertEqual("Pending", second_update["progress_request_status"])

    def test_reverting_to_current_progress_clears_pending_request(self):
        professor = self.auth_repo.create_account("Prof One", "prof@example.com", "secret123", "professor")
        student = self.auth_repo.create_account(
            "Student One",
            "student@example.com",
            "secret123",
            "student",
            student_id="S-1",
            department="CS",
        )
        klass = self.class_repo.create_class(professor, "Senior Design", "Spring 2026")
        team = self.team_repo.create_team(klass["id"], "Team A")
        self.professor_user_repo.update_user(student["id"], {"class_id": klass["id"], "team_id": team["id"]})
        student = self.professor_user_repo.refresh_user(student["id"])

        self.student_repo.save_project(student, "Team Project", "Initial notes", 10, "Medium")
        self.student_repo.save_project(student, "Team Project", "Initial notes", 35, "Medium")
        reverted = self.student_repo.save_project(student, "Team Project", "Initial notes", 10, "Medium")

        self.assertIsNone(reverted["requested_progress"])
        self.assertEqual("None", reverted["progress_request_status"])
        self.assertTrue(
            any("cancelled" in note.lower() for note in reverted["notifications"]),
            "Expected a notification when a pending request is cancelled.",
        )

    def test_team_members_for_returns_assigned_teammates(self):
        professor = self.auth_repo.create_account("Prof One", "prof@example.com", "secret123", "professor")
        student = self.auth_repo.create_account("Student One", "student@example.com", "secret123", "student")
        partner = self.auth_repo.create_account("Student Two", "partner@example.com", "secret123", "student")

        klass = self.class_repo.create_class(professor, "Senior Design", "Spring 2026")
        team = self.team_repo.create_team(klass["id"], "Team A")
        self.professor_user_repo.update_user(student["id"], {"class_id": klass["id"], "team_id": team["id"]})
        self.professor_user_repo.update_user(partner["id"], {"class_id": klass["id"], "team_id": team["id"]})
        student = self.professor_user_repo.refresh_user(student["id"])

        members = self.student_repo.team_members_for(student)

        self.assertEqual(2, len(members))
        self.assertEqual(["Student One", "Student Two"], [member["name"] for member in members])


if __name__ == "__main__":
    unittest.main()
