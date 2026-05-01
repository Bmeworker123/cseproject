from ....ui import Label, Card


class StudentStatusPage:
    def __init__(self, app):
        self.app = app

    def render(self, parent):
        project = self.app.student_repo.project_for(self.app.current_user)
        Label(parent, text="Project Status", size=16, bold=True, bg="white", fg="#1f2933").pack(anchor="w")
        Label(parent, text="See the latest teacher feedback, class, and team context.", size=10, bg="white", fg="#52606d").pack(anchor="w", pady=6)

        if not project:
            empty = Card(parent, bg="#fff7ed", padx=18, pady=18)
            empty.pack(fill="x", pady=20)
            Label(empty, text="No project submitted yet.", size=13, bold=True, bg="#fff7ed", fg="#9a3412").pack(anchor="w")
            Label(empty, text="Create your project in the Project Form page first.", size=10, bg="#fff7ed", fg="#b45309").pack(anchor="w", pady=(6, 0))
            return

        card = Card(parent, bg="#f7f9fb", padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=10)

        lines = [
            f"Project: {project['title']}",
            f"Class: {self.app.student_repo.class_name(self.app.current_user.get('class_id')) or 'Not Assigned'}",
            f"Team: {self.app.student_repo.team_name(self.app.current_user.get('team_id')) or 'Not Assigned'}",
            f"Meeting Status: {project.get('meeting_status', 'Pending')}",
            f"Project Status: {project['status']}",
            f"Last Update: {project.get('last_updated', 'N/A')}",
        ]
        for line in lines:
            Label(card, text=line, size=10, bg="#f7f9fb", fg="#334e68", justify="left").pack(anchor="w", pady=2)

        Label(card, text="Professor Notes:", size=10, bold=True, bg="#f7f9fb", fg="#102a43").pack(anchor="w", pady=(14, 4))
        notes = project.get("professor_notes", "No notes from professor yet.")
        Label(card, text=notes, size=10, bg="#f7f9fb", fg="#334e68", wraplength=720, justify="left").pack(anchor="w")
