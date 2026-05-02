from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class StudentProjectRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def project_for(self, user):
        for project in self.db.list_projects():
            if project["student_email"] == user["email"]:
                return project
        return None

    def save_project(self, student, title, notes, progress, stage, priority):
        projects = self.db.list_projects()
        existing = None
        for project in projects:
            if project["student_email"] == student["email"]:
                existing = project
                break
        if existing:
            for project in projects:
                if project["id"] == existing["id"]:
                    project["student_name"] = student["name"]
                    project["student_id"] = student.get("student_id", "")
                    project["department"] = student.get("department", "")
                    project["title"] = title
                    project["notes"] = notes or "No notes yet."
                    if progress != project.get("progress", 0):
                        project["requested_progress"] = progress
                        project["progress_request_status"] = "Pending"
                        self.db.add_project_notification(
                            project,
                            f"Your progress change to {progress}% was sent to the professor for approval.",
                        )
                    project["stage"] = stage
                    project["priority"] = priority
                    project["class_id"] = student.get("class_id")
                    project["team_id"] = student.get("team_id")
                    project["last_updated"] = self.db.timestamp()
                    if project["status"] == "Changes Requested":
                        project["status"] = "Resubmitted"
                    self.db.save_projects(projects)
                    return project

        new_project = {
            "id": self.db.next_id(projects),
            "student_email": student["email"],
            "student_name": student["name"],
            "student_id": student.get("student_id", ""),
            "department": student.get("department", ""),
            "title": title,
            "notes": notes or "No notes yet.",
            "progress": progress,
            "requested_progress": None,
            "progress_request_status": "None",
            "notifications": ["Project submitted. Waiting for professor review."],
            "status": "Pending Approval",
            "professor_notes": "Awaiting professor review.",
            "stage": stage,
            "priority": priority,
            "meeting_status": "Not Scheduled",
            "last_updated": self.db.timestamp(),
            "class_id": student.get("class_id"),
            "team_id": student.get("team_id"),
        }
        projects.append(new_project)
        self.db.save_projects(projects)
        return new_project
