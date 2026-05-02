from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class StudentUserRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

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
