from .users import ProfessorUserRepository
from .classes import ProfessorClassRepository
from .teams import ProfessorTeamRepository
from .projects import ProfessorProjectRepository


class ProfessorRepository(
    ProfessorUserRepository,
    ProfessorClassRepository,
    ProfessorTeamRepository,
    ProfessorProjectRepository,
):
    pass


__all__ = ["ProfessorRepository"]
