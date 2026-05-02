from ..base import RepositoryBase
from ..common.sqlite_gateway import SqliteGateway


class ProfessorUserRepository(RepositoryBase):
    def __init__(self, base_dir):
        self.db = SqliteGateway(base_dir)

    def _project_for_team(self, projects, team_id):
        if not team_id:
            return None
        return next((project for project in projects if project.get("team_id") == team_id), None)

    def _project_for_student(self, projects, email):
        return next(
            (
                project
                for project in projects
                if not project.get("team_id") and project.get("student_email") == email
            ),
            None,
        )

    def _project_for_user(self, projects, user):
        team_id = user.get("team_id")
        if team_id:
            return self._project_for_team(projects, team_id)
        return self._project_for_student(projects, user["email"])

    def _team_display_details(self, users, teams, user):
        if not user.get("team_id"):
            return {
                "student_email": user["email"],
                "student_name": user["name"],
                "student_id": user.get("student_id", ""),
                "department": user.get("department", ""),
            }
        members = [member for member in users if member.get("team_id") == user.get("team_id")]
        members.sort(key=lambda member: member.get("name", ""))
        member_names = ", ".join(member["name"] for member in members) or user["name"]
        team_name = next((team["name"] for team in teams if team["id"] == user.get("team_id")), "Unnamed Team")
        return {
            "student_email": members[0]["email"] if members else user["email"],
            "student_name": f"{team_name}: {member_names}",
            "student_id": "",
            "department": user.get("department", ""),
        }

    def _sync_team_memberships(self, teams, user_id, old_team_id, new_team_id):
        for team in teams:
            member_ids = list(team.get("member_ids", []))
            if team["id"] == old_team_id and user_id in member_ids:
                member_ids = [member_id for member_id in member_ids if member_id != user_id]
            if team["id"] == new_team_id and user_id not in member_ids:
                member_ids.append(user_id)
            team["member_ids"] = member_ids

    def _team_member_count(self, teams, team_id):
        team = next((row for row in teams if row["id"] == team_id), None)
        if not team:
            return 0
        return len(team.get("member_ids", []))

    def _refresh_project_details_for_user(self, users, teams, project, user):
        if not project or not user:
            return
        project["class_id"] = user.get("class_id")
        project["team_id"] = user.get("team_id")
        project.update(self._team_display_details(users, teams, user))

    def _first_user_for_team(self, users, team_id):
        members = [user for user in users if user.get("team_id") == team_id]
        members.sort(key=lambda user: user.get("name", ""))
        return members[0] if members else None

    def _remove_project(self, projects, project):
        if not project:
            return
        projects[:] = [row for row in projects if row["id"] != project["id"]]

    def _sync_projects_for_user_change(self, users, teams, projects, previous_user, updated_user):
        previous_project = self._project_for_user(projects, previous_user)
        current_project = self._project_for_user(projects, updated_user)
        personal_project = self._project_for_student(projects, updated_user["email"])
        old_team_id = previous_user.get("team_id")
        new_team_id = updated_user.get("team_id")
        old_team_size = self._team_member_count(teams, old_team_id)

        if old_team_id == new_team_id:
            target_project = current_project or previous_project
            self._refresh_project_details_for_user(users, teams, target_project, updated_user)
            return

        if new_team_id:
            target_project = current_project
            if not target_project and old_team_id and old_team_size == 0:
                target_project = previous_project
            if not target_project and personal_project:
                target_project = personal_project
            if target_project:
                self._refresh_project_details_for_user(users, teams, target_project, updated_user)

            if personal_project and target_project and personal_project["id"] != target_project["id"]:
                self._remove_project(projects, personal_project)

            if old_team_id and previous_project and previous_project.get("team_id") == old_team_id:
                if old_team_size == 0 and previous_project is not target_project:
                    self._remove_project(projects, previous_project)
                elif old_team_size > 0:
                    remaining_member = self._first_user_for_team(users, old_team_id)
                    self._refresh_project_details_for_user(users, teams, previous_project, remaining_member)
            return

        if old_team_id and previous_project and previous_project.get("team_id") == old_team_id:
            if old_team_size == 0:
                previous_project["team_id"] = None
                self._refresh_project_details_for_user(users, teams, previous_project, updated_user)
            else:
                remaining_member = self._first_user_for_team(users, old_team_id)
                self._refresh_project_details_for_user(users, teams, previous_project, remaining_member)
            return

        if current_project:
            self._refresh_project_details_for_user(users, teams, current_project, updated_user)

    def refresh_user(self, user_id):
        for user in self.db.list_users():
            if user["id"] == user_id:
                return user
        return None

    def list_students(self):
        return [user for user in self.db.list_users() if user.get("role") == "student"]

    def update_user(self, user_id, updates):
        users = self.db.list_users()
        teams = self.db.list_teams()
        projects = self.db.list_projects()
        for user in users:
            if user["id"] == user_id:
                previous_user = dict(user)
                user.update(updates)
                if "team_id" in updates:
                    self._sync_team_memberships(teams, user_id, previous_user.get("team_id"), user.get("team_id"))
                if "class_id" in updates or "team_id" in updates:
                    self._sync_projects_for_user_change(users, teams, projects, previous_user, user)
                self.db.save_users(users)
                self.db.save_teams(teams)
                self.db.save_projects(projects)
                return user
        raise ValueError("User not found.")

    def delete_student(self, student_id):
        users = self.db.list_users()
        student = next((u for u in users if u["id"] == student_id), None)
        if not student or student.get("role") != "student":
            raise ValueError("Student not found.")
        users = [user for user in users if user["id"] != student_id]
        teams = self.db.list_teams()
        for team in teams:
            if student_id in team.get("member_ids", []):
                team["member_ids"] = [member_id for member_id in team["member_ids"] if member_id != student_id]

        remaining_team_sizes = {team["id"]: len(team.get("member_ids", [])) for team in teams}
        projects = []
        for project in self.db.list_projects():
            project_team_id = project.get("team_id")
            if project_team_id:
                if project_team_id == student.get("team_id") and remaining_team_sizes.get(project_team_id, 0) == 0:
                    continue
                projects.append(project)
                continue
            if project.get("student_email") != student["email"]:
                projects.append(project)

        self.db.save_users(users)
        self.db.save_teams(teams)
        self.db.save_projects(projects)
        return student
