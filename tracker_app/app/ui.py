import os
import sys
import tkinter as tk

from ..base import AppState, Dashboard
from ..repositories import AuthRepository, StudentRepository, ProfessorRepository
from .auth import AuthPage
from .dashboards.student.dashboard import StudentDashboardPage
from .dashboards.professor.pages import ProfessorDashboardPage


class ProjectApprovalApp(Dashboard, tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.auth_repo = AuthRepository(base_dir)
        self.student_repo = StudentRepository(base_dir)
        self.professor_repo = ProfessorRepository(base_dir)
        self.state = AppState()

        self.title("Student Project Tracker")
        self.geometry("1180x760")
        self.configure(bg="#eef2f6")
        self.resizable(False, False)

        self.main_frame = tk.Frame(self, bg="#eef2f6", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.auth_page = AuthPage(self)
        self.student_dashboard = StudentDashboardPage(self)
        self.professor_dashboard = ProfessorDashboardPage(self)

        self.show_auth_screen()

    def show_auth_screen(self):
        self.auth_page.render()

    def log_out(self):
        self.state.reset()
        self.show_auth_screen()

    def show_dashboard(self):
        if self.current_user["role"] == "student":
            self.student_dashboard.render()
        else:
            self.professor_dashboard.render()
