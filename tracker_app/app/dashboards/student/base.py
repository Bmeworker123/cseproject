class StudentPageBase:
    def __init__(self, app):
        self.app = app

    def refresh_user(self):
        self.app.current_user = self.app.student_repo.refresh_user(self.app.current_user["id"])
        return self.app.current_user

    def current_project(self):
        return self.app.student_repo.project_for(self.app.current_user)

    def is_team_project(self):
        return bool(self.app.current_user.get("team_id"))
