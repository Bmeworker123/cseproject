from tracker_app.ui import Label
from ...base import ProfessorPageBase
from .components import (
    OverviewNewStudentsCard,
    OverviewProjectStatusCard,
    OverviewStatsCard,
    OverviewTeacherActionsCard,
)

class ProfessorOverviewPage(ProfessorPageBase):
    def __init__(self, dashboard):
        super().__init__(dashboard)

    def render(self, parent):
        Label(
            parent,
            text="Overview",
            size=16,
            bold=True,
            bg="white",
            fg="#1f2933"
        ).pack(anchor="w")

        Label(
            parent,
            text="Quick view of student growth, class setup, and team structure.",
            size=10,
            bg="white",
            fg="#52606d",
        ).pack(anchor="w", pady=6)

        self.stats_card = OverviewStatsCard(self, parent)
        self.project_status_card = OverviewProjectStatusCard(self, parent)
        self.new_students_card = OverviewNewStudentsCard(self, parent)
        self.teacher_actions_card = OverviewTeacherActionsCard(self, parent)

    # Backward-compatible proxy used by existing tests.
    def project_status_breakdown(self):
        return OverviewProjectStatusCard.calculate_status_breakdown(self)
