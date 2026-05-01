
class StudentRepository:
    def __init__(self, store):
        self.store = store

    def refresh_user(self, user_id):
        return self.store.find_user_by_id(user_id)

    def project_for(self, user):
        return self.store.get_project_for_student(user["email"])

    def save_project(self, user, title, notes, progress, stage, priority):
        return self.store.save_student_project(user, title, notes, progress, stage, priority)

    def class_name(self, class_id):
        return self.store.get_class_name(class_id)

    def team_name(self, team_id):
        return self.store.get_team_name(team_id)

