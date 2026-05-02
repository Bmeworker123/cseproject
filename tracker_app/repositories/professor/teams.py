from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorTeamRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def list_teams(self):
        return self.db.list_teams()

    def list_teams_for_class(self, class_id):
        return [item for item in self.db.list_teams() if item.get("class_id") == class_id]

    def create_team(self, class_id, team_name):
        teams = self.db.list_teams()
        new_team = {
            "id": self.db.next_id(teams),
            "class_id": class_id,
            "name": team_name.strip(),
            "member_ids": [],
            "created_at": self.db.timestamp(),
        }
        teams.append(new_team)
        self.db.save_teams(teams)
        return new_team

    def delete_team(self, team_id):
        teams = self.db.list_teams()
        team = next((item for item in teams if item["id"] == team_id), None)
        if not team:
            raise ValueError("Team not found.")

        teams = [item for item in teams if item["id"] != team_id]
        users = self.db.list_users()
        for user in users:
            if user.get("team_id") == team_id:
                user["team_id"] = None
        projects = [project for project in self.db.list_projects() if project.get("team_id") != team_id]
        self.db.save_teams(teams)
        self.db.save_users(users)
        self.db.save_projects(projects)
        return team
