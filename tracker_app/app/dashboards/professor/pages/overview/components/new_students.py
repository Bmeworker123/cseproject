from tracker_app.app.components import Component
from tracker_app.ui import Card, Label


class OverviewNewStudentsCard(Component):
    def __init__(self, page, parent):
        self.page = page
        super().__init__(parent)

    def render(self, parent):
        students = self.page.app.professor_repo.list_students()

        recent_card = Card(parent, bg="#f7f9fb")
        recent_card.pack(fill="x", pady=14)
        Label(
            recent_card,
            text="New Students",
            size=13,
            bold=True,
            bg="#f7f9fb",
            fg="#102a43",
        ).pack(anchor="w")

        new_students = sorted(
            students, key=lambda user: user.get("created_at", ""), reverse=True
        )[:5]
        if not new_students:
            Label(
                recent_card,
                text="No student accounts yet.",
                size=10,
                bg="#f7f9fb",
                fg="#52606d",
            ).pack(anchor="w", pady=(6, 0))
            return

        for user in new_students:
            line = f"{user['name']} ({user['email']}) | Joined: {user.get('created_at', 'N/A')}"
            Label(recent_card, text=line, size=10, bg="#f7f9fb", fg="#334e68").pack(
                anchor="w", pady=2
            )
