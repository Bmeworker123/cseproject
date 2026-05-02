from .base import RepositoryBase
from .common.sqlite_gateway import SqliteGateway


class AuthRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def find_user_by_email(self, email):
        clean_email = email.strip().lower()
        for user in self.db.list_users():
            if user["email"] == clean_email:
                return user
        return None

    def create_account(self, name, email, password, role, student_id="", department=""):
        users = self.db.list_users()
        clean_email = email.strip().lower()
        if self.find_user_by_email(clean_email):
            raise ValueError("An account with this email already exists.")

        user = {
            "id": self.db.next_id(users),
            "name": name.strip(),
            "email": clean_email,
            "password_hash": self.db.hash_password(password),
            "role": role,
            "status": "Active",
            "created_at": self.db.timestamp(),
            "last_login": "",
            "student_id": student_id.strip(),
            "department": department.strip(),
            "notes": "",
            "class_id": None,
            "team_id": None,
        }
        users.append(user)
        self.db.save_users(users)
        return user

    def sign_in(self, email, password):
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password.")
        if user.get("status") == "Archived":
            raise ValueError("This account is archived.")
        if not self.db.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password.")

        users = self.db.list_users()
        for row in users:
            if row["id"] == user["id"]:
                row["last_login"] = self.db.timestamp()
                break
        self.db.save_users(users)
        for row in users:
            if row["id"] == user["id"]:
                return row
        return None
