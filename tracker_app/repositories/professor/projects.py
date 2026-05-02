from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorProjectRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def list_projects(self):
        return self.db.list_projects()

    def get_class_name(self, class_id):
        if not class_id:
            return "Not Assigned"
        for item in self.db.list_classes():
            if item["id"] == class_id:
                return f"{item['name']} ({item['term']})"
        return "Not Assigned"

    def get_team_name(self, team_id):
        if not team_id:
            return "Not Assigned"
        for item in self.db.list_teams():
            if item["id"] == team_id:
                return item["name"]
        return "Not Assigned"

    def update_project(self, project_id, updates, notification=None):
        projects = self.db.list_projects()
        for project in projects:
            if project["id"] == project_id:
                project.update(updates)
                project["last_updated"] = self.db.timestamp()
                if notification:
                    self.db.add_project_notification(project, notification)
                self.db.save_projects(projects)
                return project
        raise ValueError("Project not found.")
