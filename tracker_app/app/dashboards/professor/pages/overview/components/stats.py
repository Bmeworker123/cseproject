import tkinter as tk

from tracker_app.app.components import Component
from tracker_app.ui import StatCard


class OverviewStatsCard(Component):
    def __init__(self, page, parent):
        self.page = page
        super().__init__(parent)

    def render(self, parent):
        students = self.page.app.professor_repo.list_students()
        projects = self.page.app.professor_repo.list_projects()
        classes = self.page.teacher_classes()

        stats = tk.Frame(parent, bg="white")
        stats.pack(fill="x", pady=10)
        StatCard(
            stats, "Total Students", str(len(students)), "Enrolled in project tracker."
        ).pack(side="left", fill="both", expand=True, padx=6)
        StatCard(
            stats, "Active Projects", str(len(projects)), "Submitted for review."
        ).pack(side="left", fill="both", expand=True, padx=6)
        StatCard(stats, "Your Classes", str(len(classes)), "Created by you.").pack(
            side="left", fill="both", expand=True, padx=6
        )
