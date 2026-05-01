import os

class DataMigration:
    def __init__(self, store):
        self.store = store

    def run_all(self):
        if self.store.get_version() == 0:
            self._create_tables()
            self._migrate_data_defaults()
            self.store.set_version(1)
            print("Migrations applied successfully (Version 0 -> 1)")

    def _create_tables(self):
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()
        with self.store._connect() as db:
            db.executescript(schema_script)

    def _migrate_data_defaults(self):
        """Ensures all existing records have proper defaults and aliases."""
        self.store.save_users([self.store._user_defaults(user) for user in self.store.list_users()])
        self.store.save_projects([self.store._project_defaults(project) for project in self.store.list_projects()])
        self.store.save_classes([self.store._class_defaults(item) for item in self.store.list_classes()])
        self.store.save_teams([self.store._team_defaults(item) for item in self.store.list_teams()])
