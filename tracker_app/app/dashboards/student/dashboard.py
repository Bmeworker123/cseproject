from ....ui import Label, Header
from .overview_page import StudentOverviewPage
from .project_form_page import StudentProjectFormPage


class StudentDashboardPage:
    def __init__(self, app):
        self.app = app
        self.pages = {
            "overview": StudentOverviewPage(app),
            "project": StudentProjectFormPage(app),
        }

    def render(self):
        self.app.clear_screen()
        subtitle = f"Signed in as {self.app.current_user['name']} ({self.app.current_user['email']})"
        Header(self.app.main_frame, "Student Workspace", subtitle, self.app.log_out).pack(fill="x", pady=(0, 14))

        sidebar, content = self.app.build_shell()
        Label(sidebar, text="Student Menu", size=15, bold=True, bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.app.sidebar_button(sidebar, "Overview", lambda: self.set_page("overview"), self.app.student_page == "overview")
        self.app.sidebar_button(sidebar, "Project Form", lambda: self.set_page("project"), self.app.student_page == "project")

        page = self.pages.get(self.app.student_page, self.pages["overview"])
        page.render(content)

    def set_page(self, page):
        self.app.student_page = page
        self.render()
