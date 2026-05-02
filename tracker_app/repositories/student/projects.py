from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class StudentProjectRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def project_for(self, user):
        for project in self.db.list_projects():
            if project.get("team_id") == user.get("team_id"):
                return project
        return None

    def save_project(self, student, title, notes):
        if not student.get("team_id"):
            raise ValueError("Student must be assigned to a team before saving a project.")

        projects = self.db.list_projects()
        existing = None
        for project in projects:
            if project.get("team_id") == student.get("team_id"):
                existing = project
                break
        if existing:
            for project in projects:
                if project["id"] == existing["id"]:
                    project["title"] = title
                    project["notes"] = notes or ""
                    project["class_id"] = student.get("class_id")
                    project["team_id"] = student.get("team_id")
                    project["approval_status"] = "Pending Approval"
                    project["last_updated"] = self.db.timestamp()
                    self.db.save_projects(projects)
                    return project

        new_project = {
            "id": self.db.next_id(projects),
            "team_id": student.get("team_id"),
            "class_id": student.get("class_id"),
            "title": title,
            "notes": notes or "",
            "approval_status": "Pending Approval",
            "last_updated": self.db.timestamp(),
        }
        projects.append(new_project)
        self.db.save_projects(projects)
        return new_project
