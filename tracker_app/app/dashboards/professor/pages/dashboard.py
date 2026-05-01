from .....ui import Label, Header

from .overview import ProfessorOverviewPage
from .students import ProfessorStudentsPage
from .classes import ProfessorClassesPage
from .teams import ProfessorTeamsPage
from .projects import ProfessorProjectsPage


class ProfessorDashboardPage:
    def __init__(self, app):
        self.app = app
        self.page_renderers = {
            "overview": ProfessorOverviewPage(self),
            "students": ProfessorStudentsPage(self),
            "classes": ProfessorClassesPage(self),
            "teams": ProfessorTeamsPage(self),
            "projects": ProfessorProjectsPage(self),
        }

    def render(self):
        self.app.clear_screen()
        self.app.current_user = self.app.professor_repo.refresh_user(self.app.current_user["id"])
        subtitle = f"Signed in as {self.app.current_user['name']} ({self.app.current_user['email']})"
        Header(self.app.main_frame, "Professor Workspace", subtitle, self.app.log_out).pack(fill="x", pady=(0, 14))

        sidebar, content = self.app.build_shell()
        Label(sidebar, text="Professor Menu", size=15, bold=True, bg="#16324f", fg="white").pack(anchor="w", padx=14, pady=(16, 8))
        self.app.sidebar_button(sidebar, "Overview", lambda: self.set_page("overview"), self.app.professor_page == "overview")
        self.app.sidebar_button(sidebar, "Students", lambda: self.set_page("students"), self.app.professor_page == "students")
        self.app.sidebar_button(sidebar, "Classes", lambda: self.set_page("classes"), self.app.professor_page == "classes")
        self.app.sidebar_button(sidebar, "Teams", lambda: self.set_page("teams"), self.app.professor_page == "teams")
        self.app.sidebar_button(sidebar, "Projects", lambda: self.set_page("projects"), self.app.professor_page == "projects")

        page = self.page_renderers.get(self.app.professor_page, self.page_renderers["overview"])
        page.render(content)

    def set_page(self, page):
        self.app.professor_page = page
        self.render()
