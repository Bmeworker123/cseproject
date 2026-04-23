# Student Project Tracker

Super simple Tkinter desktop app inspired by the structure of the reference project at [krr0ption/cse-102](https://github.com/krr0ption/cse-102), but reduced to the basics:

- create a new account with email and password
- choose student or professor during sign-up
- sign in with only accounts created inside the app
- let students create and update a project with stage, priority, and progress
- let professors see new students, manage student records, and review all projects
- let professors create classes and teams, then assign students into them
- keep accounts and projects stored locally in a SQLite database between runs

## Run

```powershell
python app.py
```

## Notes

- There are no demo accounts.
- User-created accounts, projects, classes, teams, team members, and notifications are stored in SQL tables inside `data/project_tracker.sqlite3`.
- Old JSON files are copied into SQLite automatically the first time the app runs with the new database code.
- Teachers can manage student status (`Active`, `Needs Meeting`, `Archived`) and leave teacher notes.
- Projects can be marked `Approved` or `Changes Requested`, with meeting status and stage updates.
- The code is split across the group-owned files in [tracker_app](C:/Users/cavid/Documents/Codex/2026-04-22-a-tkinter-desktop-app-for-managing/tracker_app), with [app.py](C:/Users/cavid/Documents/Codex/2026-04-22-a-tkinter-desktop-app-for-managing/app.py) as the launcher.
