from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway
from ..professor.users import ProfessorUserRepository


class StudentUserRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)
        self._professor_user_repo = ProfessorUserRepository(base_dir)

    def refresh_user(self, user_id):
        for user in self.db.list_users():
            if user["id"] == user_id:
                return user
        return None

    def class_name(self, class_id):
        if not class_id:
            return "Not Assigned"
        for item in self.db.list_classes():
            if item["id"] == class_id:
                return f"{item['name']} ({item['term']})"
        return "Not Assigned"

    def team_name(self, team_id):
        if not team_id:
            return "Not Assigned"
        for item in self.db.list_teams():
            if item["id"] == team_id:
                return item["name"]
        return "Not Assigned"

    def team_members_for(self, user):
        if not user.get("team_id"):
            return [user]
        members = [item for item in self.db.list_users() if item.get("team_id") == user.get("team_id")]
        members.sort(key=lambda item: item.get("name", ""))
        return members

    def classmates_for(self, user):
        class_id = user.get("class_id")
        if not class_id:
            return []
        classmates = [
            item
            for item in self.db.list_users()
            if item.get("role") == "student" and item.get("class_id") == class_id and item["id"] != user["id"]
        ]
        classmates.sort(key=lambda item: item.get("name", ""))
        return classmates

    def available_pairing_candidates(self, user):
        return [item for item in self.classmates_for(user) if item.get("team_id") != user.get("team_id")]

    def pair_with_student(self, user_id, partner_id):
        user = self.refresh_user(user_id)
        partner = self.refresh_user(partner_id)
        if not user or user.get("role") != "student":
            raise ValueError("Student account not found.")
        if not partner or partner.get("role") != "student":
            raise ValueError("Selected classmate was not found.")
        if user["id"] == partner["id"]:
            raise ValueError("You cannot pair with yourself.")
        if not user.get("class_id"):
            raise ValueError("You need to be assigned to a class before creating a team.")
        if user.get("class_id") != partner.get("class_id"):
            raise ValueError("You can only pair with students from your class.")
        if user.get("team_id") and user.get("team_id") == partner.get("team_id"):
            raise ValueError("You are already on the same team.")
        if user.get("team_id") and partner.get("team_id") and user.get("team_id") != partner.get("team_id"):
            raise ValueError("Both students are already assigned to different teams.")

        target_team_id = user.get("team_id") or partner.get("team_id")
        team_name = None
        if not target_team_id:
            teams = self.db.list_teams()
            target_team_id = self.db.next_id(teams)
            team_name = self._generated_team_name(user, partner)
            teams.append(
                {
                    "id": target_team_id,
                    "class_id": user.get("class_id"),
                    "name": team_name,
                    "member_ids": [],
                    "created_at": self.db.timestamp(),
                }
            )
            self.db.save_teams(teams)

        if user.get("team_id") != target_team_id:
            self._professor_user_repo.update_user(user["id"], {"class_id": user.get("class_id"), "team_id": target_team_id})
        if partner.get("team_id") != target_team_id:
            self._professor_user_repo.update_user(partner["id"], {"class_id": partner.get("class_id"), "team_id": target_team_id})

        team_name = team_name or self.team_name(target_team_id)
        return {
            "team_id": target_team_id,
            "team_name": team_name,
            "members": self.team_members_for(self.refresh_user(user_id)),
        }

    def leave_team(self, user_id):
        user = self.refresh_user(user_id)
        if not user or user.get("role") != "student":
            raise ValueError("Student account not found.")
        if not user.get("team_id"):
            raise ValueError("You are not assigned to a team.")
        self._professor_user_repo.update_user(user_id, {"class_id": user.get("class_id"), "team_id": None})
        return self.refresh_user(user_id)

    def _generated_team_name(self, first_student, second_student):
        first = first_student.get("name", "Student").split()[0]
        second = second_student.get("name", "Student").split()[0]
        return f"{first} & {second}"
