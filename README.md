# StudySync – Smart Study Planner

StudySync is a local-first productivity app that helps college students organise coursework, track deadlines, and see progress across their subjects. It combines a Streamlit interface with a SQLite database stored on the user's computer. The prototype does not require an account, paid service, or external API.

## Features

- **Dashboard:** task totals, completion progress, subject breakdowns, today's focus, and upcoming deadlines.
- **Subjects:** add, edit, and delete courses; choose an icon and color; review task counts and completion.
- **Study tasks:** create, edit, delete, and update tasks with notes, subjects, due dates, priority, and status.
- **Search and filters:** find tasks by name or notes and filter by subject, priority, status, and deadline.
- **Deadline tracking:** identify overdue, due today, due tomorrow, and upcoming work.
- **Study sessions:** log focused minutes by subject, review session history, and see total study time.
- **Analytics:** interactive charts for subject completion, priority mix, and weekly task completion.
- **CSV exports:** download subjects, tasks, and study sessions from Settings.
- **Demo data and reset:** load sample college data for demonstrations or reset the local workspace after confirmation.
- **Persistent local storage:** SQLite retains data when the app closes and starts again.

## Tech stack

- Python 3.10+
- Streamlit
- SQLite via Python's standard library
- Pandas
- Plotly Express

## Project structure

```text
StudySync/
├── .gitignore             # Excludes local data, environments, and generated files
├── app.py                 # Streamlit pages and interface
├── database.py            # SQLite schema and data-access functions
├── requirements.txt       # Python dependencies
├── README.md
└── data/                  # Created automatically on first launch; local database is Git-ignored
    └── studysync.db
```

The `.venv/`, `__pycache__/`, Python bytecode, and local SQLite files are excluded from Git. The database and `data/` directory are created automatically when the app starts.

## Installation and setup

Open a terminal in the project directory and create a virtual environment.

### Windows PowerShell

```powershell
cd "C:\path\to\StudySync"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run the commands with `\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `\.venv\Scripts\python.exe -m streamlit run app.py` instead.

### macOS / Linux

```bash
cd /path/to/StudySync
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

With the virtual environment activated:

```bash
streamlit run app.py
```

Then open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Load demo data

On a fresh workspace, open **Settings** and select **Load demo data**. StudySync creates sample subjects, tasks, and study sessions so the dashboard and charts are ready to demonstrate. Demo data is only loaded when the workspace has no subjects. Export any data you want to keep before using the reset control.

## Screenshots

Add screenshots captured from the running app to a `screenshots/` folder before publishing. Suggested captures:

- `screenshots/dashboard.png` — dashboard with demo data and today's focus.
- `screenshots/tasks.png` — task list with filters and varied task statuses.
- `screenshots/analytics.png` — progress charts.
- `screenshots/study-sessions.png` — session history and subject study time.

<!-- Optional Markdown image links can be added here after screenshots are saved. -->

## Future enhancements

- Calendar and timetable views.
- Recurring tasks and configurable reminders.
- Study goals, streaks, and weekly planning.
- Database backup and restore tools.
- Expanded historical analytics and accessibility themes.

## Privacy and local data

StudySync does not collect personal information or call external APIs. Subjects, tasks, and study sessions are stored in `data/studysync.db` on the local machine. That database is intentionally excluded from Git; use the CSV export controls to make copies of your data.
