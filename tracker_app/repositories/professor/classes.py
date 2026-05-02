from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorClassRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def classes_for(self, teacher_email):
        return [item for item in self.db.list_classes() if item["teacher_email"] == teacher_email]

    def find_class_by_id(self, class_id):
        for item in self.db.list_classes():
            if item["id"] == class_id:
                return item
        return None

    def create_class(self, teacher, class_name, term):
        classes = self.db.list_classes()
        new_class = {
            "id": self.db.next_id(classes),
            "name": class_name.strip(),
            "term": term.strip(),
            "teacher_email": teacher["email"],
            "teacher_name": teacher["name"],
            "created_at": self.db.timestamp(),
        }
        classes.append(new_class)
        self.db.save_classes(classes)
        return new_class

    def delete_class(self, class_id):
        class_record = self.find_class_by_id(class_id)
        if not class_record:
            raise ValueError("Class not found.")
        classes = [item for item in self.db.list_classes() if item["id"] != class_id]
        teams = [team for team in self.db.list_teams() if team.get("class_id") != class_id]
        users = self.db.list_users()
        for user in users:
            if user.get("class_id") == class_id:
                user["class_id"] = None
                user["team_id"] = None
        projects = self.db.list_projects()
        for project in projects:
            if project.get("class_id") == class_id:
                project["class_id"] = None
                project["team_id"] = None
        self.db.save_classes(classes)
        self.db.save_teams(teams)
        self.db.save_users(users)
        self.db.save_projects(projects)
        return class_record
