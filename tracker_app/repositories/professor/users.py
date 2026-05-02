from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorUserRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def refresh_user(self, user_id):
        for user in self.db.list_users():
            if user["id"] == user_id:
                return user
        return None

    def list_students(self):
        return [user for user in self.db.list_users() if user.get("role") == "student"]

    def update_user(self, user_id, updates):
        users = self.db.list_users()
        for user in users:
            if user["id"] == user_id:
                user.update(updates)
                self.db.save_users(users)
                return user
        raise ValueError("User not found.")

    def delete_student(self, student_id):
        users = self.db.list_users()
        student = next((u for u in users if u["id"] == student_id), None)
        if not student or student.get("role") != "student":
            raise ValueError("Student not found.")
        users = [user for user in users if user["id"] != student_id]
        teams = self.db.list_teams()
        for team in teams:
            if student_id in team.get("member_ids", []):
                team["member_ids"] = [member_id for member_id in team["member_ids"] if member_id != student_id]
        self.db.save_users(users)
        self.db.save_teams(teams)
        return student
