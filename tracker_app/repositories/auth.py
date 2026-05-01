

class AuthRepository:
    def __init__(self, store):
        self.store = store

    def create_account(self, name, email, password, role, student_id="", department=""):
        return self.store.create_user(name, email, password, role, student_id, department)

    def sign_in(self, email, password):
        return self.store.authenticate(email, password)
