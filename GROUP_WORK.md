# Group Code Ownership Guide

The project is split into 4 clear parts. Each person has UI code and data/repository-style code to explain.

## Person 1 - Advanced / Hardest Work

Files:

- `tracker_app/mardin_datastore.py`
- `tracker_app/mardin_professor_view.py`

What to explain:

- `mardin_datastore.py` is the main local database layer. It reads and writes JSON files for users, projects, classes, and teams.
- `mardin_professor_view.py` contains professor UI plus `ProfessorRepository`, which connects professor buttons to database actions.
- This person explains the hardest features: deleting students/classes/teams, assigning students, approving projects, approving/rejecting progress, changing progress, and sending notifications.

## Person 2 - Authentication

File:

- `tracker_app/ozgur_auth_view.py`

What to explain:

- Contains the sign-in/create-account UI.
- Contains `AuthRepository`, which connects login/signup buttons to the database.
- Validates email/password.
- Creates student/professor accounts and logs users in.

## Person 3 - Student Dashboard

File:

- `tracker_app/galib_student_view.py`

What to explain:

- Contains the student UI.
- Contains `StudentRepository`, which connects student screens to project/database actions.
- Lets students submit projects, request progress changes, see class/team info, and read notifications.

## Person 4 - App Shell / Shared UI

Files:

- `app.py`
- `tracker_app/ahmet_ui.py`
- `tracker_app/__init__.py`

What to explain:

- Starts the app.
- Creates the main Tkinter window.
- Provides shared layout helpers, buttons, labels, navigation, header, and sidebar.
- Connects the authentication, student, professor, and datastore parts together.

## Simple Architecture

- `app.py` starts the program.
- `ahmet_ui.py` creates the main app shell.
- `ozgur_auth_view.py`, `galib_student_view.py`, and `mardin_professor_view.py` contain the role-based screens.
- Each role file has its own repository class.
- `mardin_datastore.py` is the central database/storage file.
