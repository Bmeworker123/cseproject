from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorClassRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def classes_for(self, teacher_email):
        return self.db.list_classes_for_teacher(teacher_email)

    def find_class_by_id(self, class_id):
        return self.db.get_class_by_id(class_id)

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
        class_record = self.db.delete_class(class_id)
        if not class_record:
            raise ValueError("Class not found.")
        return class_record
