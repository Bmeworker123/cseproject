import abc
from enum import Enum
import tkinter as tk

from .ui import Button


class AuthMode(Enum):
    SIGNIN = "signin"
    SIGNUP = "signup"

class AppState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current_user = None
        self.selected_student_id = None
        self.selected_project_id = None
        self.selected_class_id = None
        self.selected_team_id = None
        self.auth_mode = AuthMode.SIGNIN.value
        self.student_page = "overview"
        self.professor_page = "overview"


class Dashboard(abc.ABC):
    state: AppState
    main_frame: tk.Frame
    
    def show_dashboard(self):
        pass

    @property
    def current_user(self):
        return self.state.current_user

    @current_user.setter
    def current_user(self, value):
        self.state.current_user = value

    @property
    def auth_mode(self):
        return self.state.auth_mode

    @auth_mode.setter
    def auth_mode(self, value):
        self.state.auth_mode = value

    @property
    def student_page(self):
        return self.state.student_page

    @student_page.setter
    def student_page(self, value):
        self.state.student_page = value

    @property
    def professor_page(self):
        return self.state.professor_page

    @professor_page.setter
    def professor_page(self, value):
        self.state.professor_page = value

    @property
    def selected_student_id(self):
        return self.state.selected_student_id

    @selected_student_id.setter
    def selected_student_id(self, value):
        self.state.selected_student_id = value

    @property
    def selected_project_id(self):
        return self.state.selected_project_id

    @selected_project_id.setter
    def selected_project_id(self, value):
        self.state.selected_project_id = value

    @property
    def selected_class_id(self):
        return self.state.selected_class_id

    @selected_class_id.setter
    def selected_class_id(self, value):
        self.state.selected_class_id = value

    @property
    def selected_team_id(self):
        return self.state.selected_team_id

    @selected_team_id.setter
    def selected_team_id(self, value):
        self.state.selected_team_id = value

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
