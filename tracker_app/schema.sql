CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_login TEXT,
    student_id TEXT,
    department TEXT,
    notes TEXT,
    class_id INTEGER,
    team_id INTEGER
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    term TEXT NOT NULL,
    teacher_email TEXT NOT NULL,
    teacher_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    class_id INTEGER,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    PRIMARY KEY (team_id, student_id)
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    student_email TEXT NOT NULL,
    student_name TEXT NOT NULL,
    student_id TEXT,
    department TEXT,
    title TEXT NOT NULL,
    notes TEXT,
    progress INTEGER NOT NULL,
    requested_progress INTEGER,
    progress_request_status TEXT NOT NULL,
    status TEXT NOT NULL,
    professor_notes TEXT,
    priority TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    class_id INTEGER,
    team_id INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS project_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    created_order INTEGER NOT NULL
);
