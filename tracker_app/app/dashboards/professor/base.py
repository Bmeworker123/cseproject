class ProfessorPageBase:
    def __init__(self, dashboard):
        self.dashboard = dashboard

    @property
    def app(self):
        return self.dashboard.app

    def teacher_classes(self):
        return self.app.professor_repo.classes_for(self.app.current_user["email"])
