class ProfessorRepository:
    def __init__(self, store):
        self.store = store

    def refresh_user(self, user_id):
        return self.store.find_user_by_id(user_id)

    def classes_for(self, teacher_email):
        return self.store.list_classes_for_teacher(teacher_email)

    def list_students(self):
        return self.store.list_students()

    def list_projects(self):
        return self.store.list_projects()

    def list_teams(self):
        return self.store.list_teams()

    def list_teams_for_class(self, class_id):
        return self.store.list_teams_for_class(class_id)

    def find_class_by_id(self, class_id):
        return self.store.find_class_by_id(class_id)

    def create_class(self, teacher, class_name, term):
        return self.store.create_class(teacher, class_name, term)

    def delete_class(self, class_id):
        return self.store.delete_class(class_id)

    def create_team(self, class_id, team_name):
        return self.store.create_team(class_id, team_name)

    def delete_team(self, team_id):
        return self.store.delete_team(team_id)

    def update_user(self, user_id, updates):
        return self.store.update_user(user_id, updates)

    def delete_student(self, student_id):
        return self.store.delete_student(student_id)

    def update_project(self, project_id, updates, notification=None):
        return self.store.update_project(project_id, updates, notification=notification)

    def get_class_name(self, class_id):
        return self.store.get_class_name(class_id)

    def get_team_name(self, team_id):
        return self.store.get_team_name(team_id)
