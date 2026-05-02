import tempfile
import unittest

from tracker_app.repositories.auth import AuthRepository
from tracker_app.repositories.professor.classes import ProfessorClassRepository
from tracker_app.repositories.professor.teams import ProfessorTeamRepository
from tracker_app.repositories.professor.users import ProfessorUserRepository
from tracker_app.repositories.student.projects import StudentProjectRepository


class ProfessorUserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        base_dir = self.tempdir.name
        self.auth_repo = AuthRepository(base_dir)
        self.class_repo = ProfessorClassRepository(base_dir)
        self.team_repo = ProfessorTeamRepository(base_dir)
        self.professor_user_repo = ProfessorUserRepository(base_dir)
        self.student_repo = StudentProjectRepository(base_dir)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_moving_student_keeps_old_team_project_with_remaining_teammates(self):
        professor = self.auth_repo.create_account("Prof One", "prof@example.com", "secret123", "professor")
        s1 = self.auth_repo.create_account("Student One", "s1@example.com", "secret123", "student", student_id="S-1")
        s2 = self.auth_repo.create_account("Student Two", "s2@example.com", "secret123", "student", student_id="S-2")
        s3 = self.auth_repo.create_account("Student Three", "s3@example.com", "secret123", "student", student_id="S-3")

        klass = self.class_repo.create_class(professor, "Senior Design", "Spring 2026")
        team_a = self.team_repo.create_team(klass["id"], "Team A")
        team_b = self.team_repo.create_team(klass["id"], "Team B")

        self.professor_user_repo.update_user(s1["id"], {"class_id": klass["id"], "team_id": team_a["id"]})
        self.professor_user_repo.update_user(s2["id"], {"class_id": klass["id"], "team_id": team_a["id"]})
        self.professor_user_repo.update_user(s3["id"], {"class_id": klass["id"], "team_id": team_b["id"]})

        s1 = self.professor_user_repo.refresh_user(s1["id"])
        s2 = self.professor_user_repo.refresh_user(s2["id"])
        s3 = self.professor_user_repo.refresh_user(s3["id"])

        project_a = self.student_repo.save_project(s1, "Project A", "Notes A", 10, "Medium")
        project_b = self.student_repo.save_project(s3, "Project B", "Notes B", 20, "High")

        self.professor_user_repo.update_user(s1["id"], {"class_id": klass["id"], "team_id": team_b["id"]})

        s1 = self.professor_user_repo.refresh_user(s1["id"])
        s2 = self.professor_user_repo.refresh_user(s2["id"])
        s3 = self.professor_user_repo.refresh_user(s3["id"])

        teammate_project = self.student_repo.project_for(s2)
        moved_student_project = self.student_repo.project_for(s1)
        destination_project = self.student_repo.project_for(s3)

        self.assertIsNotNone(teammate_project)
        self.assertEqual(project_a["id"], teammate_project["id"])
        self.assertEqual(team_a["id"], teammate_project["team_id"])

        self.assertIsNotNone(moved_student_project)
        self.assertIsNotNone(destination_project)
        self.assertEqual(project_b["id"], moved_student_project["id"])
        self.assertEqual(project_b["id"], destination_project["id"])
        self.assertEqual(team_b["id"], moved_student_project["team_id"])

    def test_deleting_last_team_member_removes_orphaned_team_project(self):
        professor = self.auth_repo.create_account("Prof One", "prof@example.com", "secret123", "professor")
        student = self.auth_repo.create_account("Student One", "student@example.com", "secret123", "student")
        klass = self.class_repo.create_class(professor, "Senior Design", "Spring 2026")
        team = self.team_repo.create_team(klass["id"], "Solo Team")

        self.professor_user_repo.update_user(student["id"], {"class_id": klass["id"], "team_id": team["id"]})
        student = self.professor_user_repo.refresh_user(student["id"])
        self.student_repo.save_project(student, "Solo Team Project", "Notes", 10, "Medium")

        self.professor_user_repo.delete_student(student["id"])

        remaining_projects = self.student_repo.db.list_projects()
        self.assertEqual([], remaining_projects)


if __name__ == "__main__":
    unittest.main()
