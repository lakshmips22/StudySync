import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

import database as db


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="studysync-db-test-")
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "test.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def add_subject(self, name="Algorithms"):
        db.add_subject(name, "#4265BD", "📘")
        return int(db.subjects().iloc[0].id)

    def test_subject_crud_and_related_data_cascade(self):
        subject_id = self.add_subject()
        db.save_task(None, "Review trees", subject_id, "Rotations", date.today(), "High", "Pending")
        db.add_session(subject_id, 30, "Review", datetime.now())
        db.update_subject(subject_id, "Data Structures", "#123456", "🧠")
        self.assertEqual(db.subjects().iloc[0]["name"], "Data Structures")
        self.assertEqual(db.subjects().iloc[0].color, "#123456")
        db.delete_subject(subject_id)
        self.assertTrue(db.subjects().empty)
        self.assertTrue(db.tasks().empty)
        self.assertTrue(db.sessions().empty)

    def test_task_status_and_completion_timestamp(self):
        subject_id = self.add_subject()
        db.save_task(None, "Finish lab", subject_id, "", date.today(), "Medium", "Pending")
        task = db.tasks().iloc[0]
        self.assertEqual(task.status, "Pending")
        self.assertIsNone(task.completed_at)
        db.set_task_status(int(task.id), "Completed")
        completed = db.tasks().iloc[0]
        self.assertEqual(completed.status, "Completed")
        self.assertTrue(completed.completed_at)
        db.set_task_status(int(task.id), "In Progress")
        reopened = db.tasks().iloc[0]
        self.assertEqual(reopened.status, "In Progress")
        self.assertIsNone(reopened.completed_at)
        db.save_task(int(task.id), "Updated lab", subject_id, "Notes", date.today() + timedelta(days=2), "High", "Completed")
        updated = db.tasks().iloc[0]
        self.assertEqual(updated.title, "Updated lab")
        self.assertEqual(updated.priority, "High")
        self.assertEqual(updated.deadline, (date.today() + timedelta(days=2)).isoformat())
        self.assertTrue(updated.completed_at)
        db.delete_task(int(task.id))
        self.assertTrue(db.tasks().empty)

    def test_sessions_and_data_survive_database_reinitialization(self):
        subject_id = self.add_subject()
        db.add_session(subject_id, 45, "Practice problems", datetime.now())
        db.init_db()
        sessions = db.sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(int(sessions.iloc[0].duration_minutes), 45)
        self.assertEqual(sessions.iloc[0].notes, "Practice problems")

    def test_demo_data_loads_once_and_only_into_empty_workspace(self):
        db.load_demo_data()
        self.assertEqual((len(db.subjects()), len(db.tasks()), len(db.sessions())), (5, 8, 3))
        db.load_demo_data()
        self.assertEqual((len(db.subjects()), len(db.tasks()), len(db.sessions())), (5, 8, 3))


if __name__ == "__main__":
    unittest.main()
