from .classes import ProfessorClassRepository
from .projects import ProfessorProjectRepository
from .reports import ProfessorReportRepository
from .teams import ProfessorTeamRepository
from .users import ProfessorUserRepository


class ProfessorRepository(
    ProfessorUserRepository,
    ProfessorClassRepository,
    ProfessorTeamRepository,
    ProfessorProjectRepository,
    ProfessorReportRepository,
):
    pass


__all__ = ["ProfessorRepository"]
