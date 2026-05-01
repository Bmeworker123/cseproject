import os
import json

class DataMigration:
    def __init__(self, store):
        self.store = store

    def run_all(self):
        if self.store.get_version() == 0:
            self._create_tables()
            self._migrate_json_files()
            self._migrate_data_defaults()
            self.store.set_version(1)
            print("Migrations applied successfully (Version 0 -> 1)")

    def _create_tables(self):
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()
        with self.store._connect() as db:
            db.executescript(schema_script)

    def _migrate_json_files(self):
        # Only migrate if the database is currently empty
        if self.store.list_users() or self.store.list_projects() or self.store.list_classes() or self.store.list_teams():
            return

        if os.path.exists(self.store.users_file):
            self.store.save_users(self._read_json_file(self.store.users_file))
        if os.path.exists(self.store.classes_file):
            self.store.save_classes(self._read_json_file(self.store.classes_file))
        if os.path.exists(self.store.teams_file):
            self.store.save_teams(self._read_json_file(self.store.teams_file))
        if os.path.exists(self.store.projects_file):
            self.store.save_projects(self._read_json_file(self.store.projects_file))

    def _read_json_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

    def _migrate_data_defaults(self):
        """Ensures all existing records have proper defaults and aliases."""
        self.store.save_users([self.store._user_defaults(user) for user in self.store.list_users()])
        self.store.save_projects([self.store._project_defaults(project) for project in self.store.list_projects()])
        self.store.save_classes([self.store._class_defaults(item) for item in self.store.list_classes()])
        self.store.save_teams([self.store._team_defaults(item) for item in self.store.list_teams()])
