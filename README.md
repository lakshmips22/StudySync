# StudySync — Smart Study Planner

StudySync is a local-first study planner built for college students. It brings subjects, coursework deadlines, focused study sessions, and progress insights into one Streamlit application backed by SQLite.

## The problem

Assignments, revision plans, and study time often end up spread across separate notes and calendars. StudySync provides one place to organise work by subject, track deadlines and priorities, and review progress over time.

## Features

- **Dashboard:** subject and task totals, completion percentage, due-today and overdue counts, subject progress, today's focus, and upcoming deadlines.
- **Subject management:** create, edit, and delete subjects, choose an icon and color, and review completion counts.
- **Task management:** create, edit, delete, and update task status, subject, notes, deadline, and priority.
- **Search and filters:** find tasks by title or notes and filter by subject, priority, status, and deadline.
- **Study sessions:** log study duration and notes, review session history, and see time totals by subject.
- **Analytics:** interactive Plotly charts for subject completion, task priorities, and weekly completions.
- **CSV export:** download subjects, tasks, and study-session data.
- **Demo data and reset:** load sample college records for a presentation or reset local data after confirmation.
- **Local persistence:** SQLite stores data on the computer running the app. No login, paid API, or hosted service is required.

## Technologies

- Python 3.10 or later
- Streamlit
- SQLite through Python's standard library
- Pandas
- Plotly Express

## Screenshots

### Dashboard
![StudySync dashboard](screenshots/dashboard.png)

### Tasks
![StudySync task management](screenshots/tasks.png)

### Subjects
![StudySync subject management](screenshots/subjects.png)

### Study sessions
![StudySync study sessions](screenshots/study-sessions.png)

### Analytics
![StudySync analytics](screenshots/analytics.png)

### Settings
![StudySync settings](screenshots/settings.png)

## Project structure

```text
StudySync/
├── .gitignore
├── app.py                 # Streamlit pages and interface
├── database.py            # SQLite schema and data-access functions
├── requirements.txt
├── screenshots/           # Application screenshots
└── tests/
    ├── test_app.py        # Streamlit page and task workflow checks
    └── test_database.py   # Isolated SQLite persistence checks
```

At first launch, StudySync creates `data/studysync.db`. The database, SQLite sidecar files, `.venv/`, Python bytecode, local secrets, and common editor-generated files are excluded by `.gitignore`.

## Installation and setup

Clone the repository, then open PowerShell in the project directory. Python 3.10+ is required.

```powershell
git clone https://github.com/lakshmips22/StudySync.git
cd StudySync
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell prevents environment activation, install with the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the application

With the virtual environment active:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Load demo data

In a new workspace, open **Settings** and choose **Load demo data**. The sample contains college subjects, tasks with different statuses and deadlines, and study sessions. Demo data is added only when the workspace has no subjects. Use **Settings → Export your data** before resetting anything you want to keep.

## Testing

Run the automated tests from the project root with:

```powershell
python -m unittest discover -s tests -v
```

The test suite uses temporary SQLite databases. It checks database CRUD, task status timestamps, session persistence, demo-data idempotence, empty and populated page rendering, dashboard deadline counts, task add/edit/delete/search/status flows, subject UI CRUD, and study-session UI persistence. Nine automated tests passed on 2026-10-15. Browser checks remain useful for visual layout and downloaded-file inspection.

## Known limitations

- Data is stored only in the local SQLite file; there is no account system, cloud sync, or multi-device backup.
- Reminders, recurring tasks, calendar integration, and collaboration are not implemented.
- CSV downloads are manual exports, not automatic backups.
- Browser-level visual layout and file downloads still need to be checked on the machine used for the presentation.

## Future improvements

- Calendar and timetable views with configurable reminders.
- Recurring tasks, study goals, and streak tracking.
- Database backup and restore controls.
- More historical analytics and accessibility options.

## Privacy

StudySync makes no external API calls and does not require personal account information. Study records remain in `data/studysync.db` on the local machine. The local database is deliberately excluded from Git.
