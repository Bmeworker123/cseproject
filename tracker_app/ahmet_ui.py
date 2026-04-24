import os
import sys
import tkinter as tk

from .ui import Button, Label, Card, EntryField, TextField, OptionField, StatCard, Header
from .galib_student_view import StudentMixin, StudentRepository
from .mardin_datastore import DataStore
from .mardin_professor_view import ProfessorMixin, ProfessorRepository
from .ozgur_auth_view import AuthMixin, AuthRepository


class ProjectApprovalApp(AuthMixin, StudentMixin, ProfessorMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        self.store = DataStore(base_dir)
        self.auth_repo = AuthRepository(self.store)
        self.student_repo = StudentRepository(self.store)
        self.professor_repo = ProfessorRepository(self.store)
        self.current_user = None
        self.auth_mode = "signin"
        self.selected_student_id = None
        self.selected_project_id = None
        self.selected_class_id = None
        self.selected_team_id = None
        self.student_page = "overview"
        self.professor_page = "overview"
        self.title("Student Project Tracker")
        self.geometry("1180x760")
        self.configure(bg="#eef2f6")
        self.resizable(False, False)
        self.main_frame = tk.Frame(self, bg="#eef2f6", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)
        self.show_auth_screen()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def build_shell(self):
        shell = tk.Frame(self.main_frame, bg="#eef2f6")
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg="#16324f", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        content = tk.Frame(shell, bg="white", padx=18, pady=18)
        content.pack(side="left", fill="both", expand=True)
        return sidebar, content

    def sidebar_button(self, parent, text, command, active=False):
        Button(parent, text, command, primary=active).pack(fill="x", padx=14, pady=6)
        if not active:
            parent.winfo_children()[-1].configure(bg="#16324f", fg="white", relief="flat", activebackground="#1d456b", activeforeground="white")

    def log_out(self):
        self.current_user = None
        self.auth_mode = "signin"
        self.selected_student_id = None
        self.selected_project_id = None
        self.selected_class_id = None
        self.selected_team_id = None
        self.show_auth_screen()

    def show_dashboard(self):
        if self.current_user["role"] == "student":
            self.show_student_dashboard()
        else:
            self.show_professor_dashboard()
