from .ozgur_datastore import OzgurDataStore


class GalibDataStore(OzgurDataStore):
    def get_project_for_student(self, student_email):
        for project in self.list_projects():
            if project["student_email"] == student_email:
                return project
        return None

    def save_student_project(self, student, title, notes, priority):
        projects = self.list_projects()
        existing = self.get_project_for_student(student["email"])
        if existing:
            for project in projects:
                if project["id"] == existing["id"]:
                    project["student_name"] = student["name"]
                    project["student_id"] = student.get("student_id", "")
                    project["department"] = student.get("department", "")
                    project["title"] = title
                    project["notes"] = notes or "No notes yet."
                    project["priority"] = priority
                    project["class_id"] = student.get("class_id")
                    project["team_id"] = student.get("team_id")
                    project["last_updated"] = self._timestamp()
                    self.save_projects(projects)
                    return project
        new_project = {
            "id": self._next_id(projects),
            "student_email": student["email"],
            "student_name": student["name"],
            "student_id": student.get("student_id", ""),
            "department": student.get("department", ""),
            "title": title,
            "notes": notes or "No notes yet.",
            "progress": 0,
            "requested_progress": None,
            "progress_request_status": "None",
            "notifications": [
                "Project submitted. Waiting for professor review.",
            ],
            "status": "Pending Approval",
            "professor_notes": "Awaiting professor review.",
            "stage": "Not Set",
            "priority": priority,
            "meeting_status": "Not Scheduled",
            "last_updated": self._timestamp(),
            "class_id": student.get("class_id"),
            "team_id": student.get("team_id"),
        }
        projects.append(new_project)
        self.save_projects(projects)
        return new_project
