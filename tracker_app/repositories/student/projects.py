from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class StudentProjectRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def _find_project_for_user(self, projects, user):
        team_id = user.get("team_id")
        if team_id:
            return next((project for project in projects if project.get("team_id") == team_id), None)
        return next((project for project in projects if project.get("student_email") == user["email"]), None)

    def _team_display_details(self, student):
        if not student.get("team_id"):
            return {
                "student_email": student["email"],
                "student_name": student["name"],
                "student_id": student.get("student_id", ""),
                "department": student.get("department", ""),
            }
        members = [user for user in self.db.list_users() if user.get("team_id") == student.get("team_id")]
        members.sort(key=lambda user: user.get("name", ""))
        member_names = ", ".join(member["name"] for member in members) or student["name"]
        team_name = next(
            (team["name"] for team in self.db.list_teams() if team["id"] == student.get("team_id")),
            "Unnamed Team",
        )
        return {
            "student_email": members[0]["email"] if members else student["email"],
            "student_name": f"{team_name}: {member_names}",
            "student_id": "",
            "department": student.get("department", ""),
        }

    def project_for(self, user):
        return self._find_project_for_user(self.db.list_projects(), user)

    def save_project(self, student, title, notes, progress, priority):
        projects = self.db.list_projects()
        existing = self._find_project_for_user(projects, student)
        if existing:
            for project in projects:
                if project["id"] == existing["id"]:
                    display_details = self._team_display_details(student)
                    project["student_name"] = display_details["student_name"]
                    project["student_id"] = display_details["student_id"]
                    project["department"] = display_details["department"]
                    project["student_email"] = display_details["student_email"]
                    project["title"] = title
                    project["notes"] = notes or "No notes yet."
                    current_progress = project.get("progress", 0)
                    requested_progress = project.get("requested_progress")
                    if progress != current_progress and progress != requested_progress:
                        project["requested_progress"] = progress
                        project["progress_request_status"] = "Pending"
                        self.db.add_project_notification(
                            project,
                            f"Your progress change to {progress}% was sent to the professor for approval.",
                        )
                    elif requested_progress is None:
                        project["progress_request_status"] = "None"
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
            **self._team_display_details(student),
            "title": title,
            "notes": notes or "No notes yet.",
            "progress": progress,
            "requested_progress": None,
            "progress_request_status": "None",
            "notifications": ["Project submitted. Waiting for professor review."],
            "status": "Pending Approval",
            "professor_notes": "Awaiting professor review.",
            "priority": priority,
            "last_updated": self.db.timestamp(),
            "class_id": student.get("class_id"),
            "team_id": student.get("team_id"),
        }
        projects.append(new_project)
        self.db.save_projects(projects)
        return new_project
