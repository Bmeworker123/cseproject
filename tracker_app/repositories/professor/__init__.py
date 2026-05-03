from .classes import ProfessorClassRepository
from .projects import ProfessorProjectRepository
from .teams import ProfessorTeamRepository
from .users import ProfessorUserRepository


class ProfessorRepository(
    ProfessorUserRepository,
    ProfessorClassRepository,
    ProfessorTeamRepository,
    ProfessorProjectRepository,
):
    pass


__all__ = ["ProfessorRepository"]
