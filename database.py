"""SQLite persistence and data-access helpers for StudySync."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "studysync.db"


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE,
            color TEXT NOT NULL DEFAULT '#5B8DEF',
            icon TEXT NOT NULL DEFAULT '📘',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            description TEXT NOT NULL DEFAULT '',
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Low','Medium','High')),
            status TEXT NOT NULL CHECK(status IN ('Pending','In Progress','Completed')) DEFAULT 'Pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            duration_minutes INTEGER NOT NULL CHECK(duration_minutes > 0),
            notes TEXT NOT NULL DEFAULT '',
            studied_at TEXT NOT NULL
        );
        """)


def frame(query: str, params: tuple = ()) -> pd.DataFrame:
    with connection() as db:
        return pd.read_sql_query(query, db, params=params)


def subjects() -> pd.DataFrame:
    return frame("""SELECT s.*, COUNT(t.id) task_count,
        COALESCE(SUM(CASE WHEN t.status='Completed' THEN 1 ELSE 0 END),0) completed_count
        FROM subjects s LEFT JOIN tasks t ON t.subject_id=s.id GROUP BY s.id ORDER BY s.name""")


def tasks() -> pd.DataFrame:
    return frame("""SELECT t.*, s.name subject, s.color subject_color, s.icon subject_icon
        FROM tasks t JOIN subjects s ON s.id=t.subject_id ORDER BY t.deadline, t.priority DESC, t.id DESC""")


def sessions() -> pd.DataFrame:
    return frame("""SELECT x.*, s.name subject, s.color subject_color FROM sessions x
        JOIN subjects s ON s.id=x.subject_id ORDER BY x.studied_at DESC, x.id DESC""")


def add_subject(name: str, color: str, icon: str) -> None:
    with connection() as db:
        db.execute("INSERT INTO subjects(name,color,icon) VALUES(?,?,?)", (name.strip(), color, icon))


def update_subject(subject_id: int, name: str, color: str, icon: str) -> None:
    with connection() as db:
        db.execute("UPDATE subjects SET name=?,color=?,icon=? WHERE id=?", (name.strip(), color, icon, subject_id))


def delete_subject(subject_id: int) -> None:
    with connection() as db:
        db.execute("DELETE FROM subjects WHERE id=?", (subject_id,))


def save_task(task_id: int | None, title: str, subject_id: int, description: str, deadline: date, priority: str, status: str) -> None:
    completed_at = datetime.now().isoformat(timespec="seconds") if status == "Completed" else None
    with connection() as db:
        if task_id is None:
            db.execute("INSERT INTO tasks(title,subject_id,description,deadline,priority,status,completed_at) VALUES(?,?,?,?,?,?,?)",
                       (title.strip(), subject_id, description.strip(), deadline.isoformat(), priority, status, completed_at))
        else:
            db.execute("UPDATE tasks SET title=?,subject_id=?,description=?,deadline=?,priority=?,status=?,completed_at=CASE WHEN ?='Completed' THEN COALESCE(completed_at,?) ELSE NULL END WHERE id=?",
                       (title.strip(), subject_id, description.strip(), deadline.isoformat(), priority, status, status, completed_at, task_id))


def set_task_status(task_id: int, status: str) -> None:
    completed_at = datetime.now().isoformat(timespec="seconds") if status == "Completed" else None
    with connection() as db:
        db.execute("UPDATE tasks SET status=?,completed_at=? WHERE id=?", (status, completed_at, task_id))


def delete_task(task_id: int) -> None:
    with connection() as db:
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))


def add_session(subject_id: int, duration: int, notes: str, studied_at: datetime) -> None:
    with connection() as db:
        db.execute("INSERT INTO sessions(subject_id,duration_minutes,notes,studied_at) VALUES(?,?,?,?)",
                   (subject_id, duration, notes.strip(), studied_at.isoformat(timespec="minutes")))


def reset_all() -> None:
    with connection() as db:
        db.execute("DELETE FROM sessions")
        db.execute("DELETE FROM tasks")
        db.execute("DELETE FROM subjects")


def load_demo_data() -> None:
    if not subjects().empty:
        return
    palette = [('#597EF7','🧠'),('#9254DE','💻'),('#13A8A8','🌐'),('#FA8C16','📐'),('#EB5757','🤖')]
    names = ['Data Structures','Object Oriented Programming','Theory of Computation','Web Development','Artificial Intelligence']
    now = date.today()
    with connection() as db:
        ids = []
        for name, (color, icon) in zip(names, palette):
            cur = db.execute("INSERT INTO subjects(name,color,icon) VALUES(?,?,?)", (name,color,icon))
            ids.append(cur.lastrowid)
        samples = [
            ('Revise binary search trees',0,'Review rotations, traversals, and complexity.','High','In Progress',0),
            ('Implement graph traversal lab',0,'Finish BFS and DFS implementations.','High','Pending',1),
            ('Prepare OOP design patterns notes',1,'Summarise factory and observer patterns.','Medium','Pending',2),
            ('Review finite automata',2,'Practise DFA minimisation exercises.','High','Completed',-1),
            ('Build responsive course page',3,'Polish the mobile layout and navigation.','Medium','In Progress',3),
            ('Explore search algorithms',4,'Compare informed and uninformed search.','Low','Pending',5),
            ('Submit database assignment',3,'Package source and short reflection.','High','Pending',-2),
            ('Read about neural networks',4,'Chapter 4 reading and key terms.','Low','Completed',-4),
        ]
        for title, idx, desc, priority, status, offset in samples:
            created = datetime.combine(now + timedelta(days=min(offset,0)), datetime.min.time()).isoformat(timespec='seconds')
            completed = datetime.now().isoformat(timespec='seconds') if status == 'Completed' else None
            db.execute("INSERT INTO tasks(title,subject_id,description,deadline,priority,status,created_at,completed_at) VALUES(?,?,?,?,?,?,?,?)",
                       (title, ids[idx], desc, (now+timedelta(days=offset)).isoformat(), priority, status, created, completed))
        for idx, mins, days, notes in [(0,50,0,'Binary tree review'),(3,40,1,'Frontend implementation'),(1,35,2,'Design patterns')]:
            db.execute("INSERT INTO sessions(subject_id,duration_minutes,notes,studied_at) VALUES(?,?,?,?)",
                       (ids[idx], mins, notes, (datetime.now()-timedelta(days=days)).isoformat(timespec='minutes')))
