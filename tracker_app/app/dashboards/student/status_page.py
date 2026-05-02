from ....ui import Label, Card
from .base import StudentPageBase
from .components import render_empty_state, render_page_header, render_detail_lines


class StudentStatusPage(StudentPageBase):
    def __init__(self, app):
        super().__init__(app)

    def render(self, parent):
        project = self.app.student_repo.project_for(self.app.current_user)
        render_page_header(parent, "Project Status", "See the latest teacher feedback, class, and team context.")

        if not project:
            empty = render_empty_state(
                parent,
                "No project submitted yet.",
                "Create your project in the Project Form page first.",
                bg="#fff7ed",
                title_fg="#9a3412",
                message_fg="#b45309",
            )
            empty.pack(fill="x", pady=20)
            return

        card = Card(parent, bg="#f7f9fb", padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=10)

        render_detail_lines(card, [
            f"Project: {project['title']}",
            f"Class: {self.app.student_repo.class_name(self.app.current_user.get('class_id')) or 'Not Assigned'}",
            f"Team: {self.app.student_repo.team_name(self.app.current_user.get('team_id')) or 'Not Assigned'}",
            f"Meeting Status: {project.get('meeting_status', 'Pending')}",
            f"Project Status: {project['status']}",
            f"Last Update: {project.get('last_updated', 'N/A')}",
        ], bg="#f7f9fb", fg="#334e68", wraplength=720)

        Label(card, text="Professor Notes:", size=10, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w", pady=(14, 4))
        notes = project.get("professor_notes", "No notes from professor yet.")
        Label(card, text=notes, size=10, bg="#f7f9fb", fg="#334e68", wraplength=720, justify="left").pack(anchor="w")
