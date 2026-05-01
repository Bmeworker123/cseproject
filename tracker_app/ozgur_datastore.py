import hashlib
import hmac
import os
from .ahmet_datastore import AhmetDataStore


class OzgurDataStore(AhmetDataStore):
    def _hash_password(self, password):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return f"{salt.hex()}:{digest.hex()}"

    def _verify_password(self, password, stored_hash):
        try:
            salt_hex, digest_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_digest = bytes.fromhex(digest_hex)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
        return hmac.compare_digest(digest, expected_digest)

    def find_user_by_email(self, email):
        clean_email = email.strip().lower()
        for user in self.list_users():
            if user["email"] == clean_email:
                return user
        return None

    def find_user_by_name(self, name):
        clean_name = name.strip().lower()
        for user in self.list_users():
            if user["name"].strip().lower() == clean_name:
                return user
        return None

    def find_user_by_id(self, user_id):
        for user in self.list_users():
            if user["id"] == user_id:
                return user
        return None

    def create_user(self, name, email, password, role, student_id="", department=""):
        users = self.list_users()
        clean_email = email.strip().lower()
        if self.find_user_by_email(clean_email):
            raise ValueError("An account with this email already exists.")
        user = {
            "id": self._next_id(users),
            "name": name.strip(),
            "email": clean_email,
            "password_hash": self._hash_password(password),
            "role": role,
            "status": "Active",
            "created_at": self._timestamp(),
            "last_login": "",
            "student_id": student_id.strip(),
            "department": department.strip(),
            "notes": "",
            "class_id": None,
            "team_id": None,
        }
        users.append(user)
        self.save_users(users)
        return user

    def authenticate(self, name, password):
        user = self.find_user_by_name(name)
        if not user:
            raise ValueError("Invalid name or password.")
        if user.get("status") == "Archived":
            raise ValueError("This account is archived.")
        if not self._verify_password(password, user["password_hash"]):
            raise ValueError("Invalid name or password.")
        self.update_user(user["id"], {"last_login": self._timestamp()})
        return self.find_user_by_id(user["id"])

    def update_user(self, user_id, updates):
        users = self.list_users()
        for user in users:
            if user["id"] == user_id:
                user.update(updates)
                self.save_users(users)
                return user
        raise ValueError("User not found.")
