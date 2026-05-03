import tkinter as tk

from tracker_app.app.components import Component
from tracker_app.ui import StatCard


class OverviewStatsCard(Component):
    def __init__(self, page, parent):
        self.page = page
        super().__init__(parent)

    def render(self, parent):
        students = self.page.app.professor_repo.list_students()
        active_projects = self.calculate_active_projects(self.page)
        classes = self.page.teacher_classes()

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        StatCard(
            stats, "Total Students", str(len(students)), "Enrolled in project tracker."
        ).pack(side="left", fill="both", expand=True, padx=6)
        StatCard(
            stats,
            "Active Projects",
            str(active_projects),
            "Submitted for review.",
        ).pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Your Classes", str(len(classes)), "Created by you.").pack(
            side="left", fill="both", expand=True, padx=6
        )

    @staticmethod
    def calculate_active_projects(page):
        teacher_email = page.app.current_user["email"]
        return page.app.professor_repo.count_projects_for_teacher(teacher_email)
