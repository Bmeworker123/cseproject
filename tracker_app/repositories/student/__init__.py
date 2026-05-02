from .users import StudentUserRepository
from .projects import StudentProjectRepository


class StudentRepository(StudentUserRepository, StudentProjectRepository):
    pass


__all__ = ["StudentRepository"]
