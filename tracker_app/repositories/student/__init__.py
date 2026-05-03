from .projects import StudentProjectRepository
from .users import StudentUserRepository


class StudentRepository(StudentUserRepository, StudentProjectRepository):
    pass


__all__ = ["StudentRepository"]
