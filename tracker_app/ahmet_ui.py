import os
import sys
import tkinter as tk

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
    def make_button(self, parent, text, command, primary=False):
        bg = "#2f80ed" if primary else "white"
        fg = "white" if primary else "#334e68"
        relief = "flat" if primary else "solid"
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=relief,
            bd=1 if not primary else 0,
            padx=12,
            pady=8,
        )
    def label(self, parent, text, size=10, bold=False, bg="white", fg="#334e68", **pack):
        font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
        widget = tk.Label(parent, text=text, font=font, bg=bg, fg=fg, **{k: v for k, v in pack.items() if k in {"wraplength", "justify"}})
        pack_args = {"anchor": pack.get("anchor", "w"), "pady": pack.get("pady", 0)}
        if pack.get("fill"):
            pack_args["fill"] = pack["fill"]
        widget.pack(**pack_args)
        return widget
    def entry_field(self, parent, label, show=None, bg="white"):
        self.label(parent, label, bg=bg, fg="#000000", pady=(12, 4))
        entry = tk.Entry(parent, show=show, font=("Segoe UI", 11))
        entry.pack(fill="x")
        return entry
    def text_field(self, parent, label, height=4, bg="white"):
        self.label(parent, label, bg=bg, fg="#000000")
        text = tk.Text(parent, height=height, font=("Segoe UI", 10))
        text.pack(fill="x", pady=(4, 10))
        return text
    def option_field(self, parent, label, variable, values, bg="white", fill="x"):
        self.label(parent, label, bg=bg, fg="#000000")
        menu = tk.OptionMenu(parent, variable, *values)
        pack_args = {"pady": (4, 0)}
        if fill:
            pack_args["fill"] = fill
        else:
            pack_args["anchor"] = "w"
        menu.pack(**pack_args)
        return menu
    def render_stat_card(self, parent, title, value, note="", bg="#f7f9fb"):
        card = tk.Frame(parent, bg=bg, padx=14, pady=14)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=bg, fg="#52606d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 17, "bold"), bg=bg, fg="#102a43", pady=4).pack(anchor="w")
        if note:
            tk.Label(card, text=note, font=("Segoe UI", 9), bg=bg, fg="#7b8794", wraplength=220, justify="left").pack(anchor="w")
    def create_header(self, title, subtitle):
        header = tk.Frame(self.main_frame, bg="#eef2f6")
        header.pack(fill="x", pady=(0, 14))
        info = tk.Frame(header, bg="#eef2f6")
        info.pack(side="left")
        tk.Label(info, text=title, font=("Segoe UI", 18, "bold"), bg="#eef2f6", fg="#102a43").pack(anchor="w")
        tk.Label(info, text=subtitle, font=("Segoe UI", 10), bg="#eef2f6", fg="#52606d").pack(anchor="w")
        actions = tk.Frame(header, bg="#eef2f6")
        actions.pack(side="right")
        self.make_button(actions, "Back", self.log_out).pack(side="left", padx=(0, 8))
        self.make_button(actions, "Log Out", self.log_out).pack(side="left")
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
        bg = "#2f80ed" if active else "#16324f"
        self.make_button(parent, text, command, primary=active).pack(fill="x", padx=14, pady=6)
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
