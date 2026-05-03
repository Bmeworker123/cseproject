from tracker_app.ui import Header, Label
from .overview_page import StudentOverviewPage
from .project_form_page import StudentProjectFormPage


class StudentDashboardPage:
    def __init__(self, app):
        self.app = app
        self.sidebar = None
        self.content = None
        self.sidebar_buttons = {}
        self.pages = {
            "overview": StudentOverviewPage(app),
            "project": StudentProjectFormPage(app),
        }

    @staticmethod
    def _clear_frame(frame):
        if not frame:
            return
        for widget in frame.winfo_children():
            widget.destroy()

    def render(self):
        self.app.clear_screen()
        subtitle = f"Signed in as {self.app.current_user['name']} ({self.app.current_user['email']})"
        Header(
            self.app.main_frame, "Student Workspace", subtitle, self.app.log_out
        ).pack(fill="x", pady=(0, 14))

        self.sidebar, self.content = self.app.build_shell()
        self._build_sidebar()
        self._render_content()

    def _build_sidebar(self):
        self._clear_frame(self.sidebar)
        Label(
            self.sidebar,
            text="Student Menu",
            size=15,
            bold=True,
            bg="#16324f",
            fg="white",
        ).pack(anchor="w", padx=14, pady=(16, 8))
        self.sidebar_buttons = {
            "overview": self.app.sidebar_button(
                self.sidebar,
                "Overview",
                lambda: self.set_page("overview"),
                self.app.student_page == "overview",
            ),
            "project": self.app.sidebar_button(
                self.sidebar,
                "Project Form",
                lambda: self.set_page("project"),
                self.app.student_page == "project",
            ),
        }

    def _set_sidebar_active_state(self):
        for key, button in self.sidebar_buttons.items():
            is_active = key == self.app.student_page
            if is_active:
                button.configure(
                    bg="#2f80ed",
                    fg="white",
                    activebackground="#2f80ed",
                    activeforeground="white",
                    relief="flat",
                    bd=0,
                    font=("Segoe UI", 10, "bold"),
                )
            else:
                button.configure(
                    bg="#16324f",
                    fg="white",
                    activebackground="#1d456b",
                    activeforeground="white",
                    relief="flat",
                    bd=1,
                    font=("Segoe UI", 10, "normal"),
                )

    def _render_content(self):
        self._clear_frame(self.content)
        page = self.pages.get(self.app.student_page, self.pages["overview"])
        page.render(self.content)

    def set_page(self, page):
        self.app.student_page = page
        if not self.sidebar or not self.content:
            self.render()
            return
        self._set_sidebar_active_state()
        self._render_content()
