import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import database as db
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class StreamlitAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="studysync-app-test-")
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "studysync.db"
        db.init_db()
        db.add_subject("Test Subject", "#4265BD", "📘")
        self.subject_id = int(db.subjects().iloc[0].id)
        db.save_task(None, "Task one", self.subject_id, "Initial notes", date.today(), "High", "Pending")
        db.save_task(None, "Task two", self.subject_id, "Other notes", date.today() + timedelta(days=2), "Low", "Pending")

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def run_app(self, page="🏠  Dashboard"):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        app.radio[0].set_value(page).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        return app

    def test_all_navigation_pages_render(self):
        pages = ["🏠  Dashboard", "📚  Subjects", "📝  Tasks", "⏱️  Study Sessions", "📊  Analytics", "⚙️  Settings"]
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        for page in pages:
            app.radio[0].set_value(page).run()
            self.assertFalse(app.exception, f"{page}: {[str(error.value) for error in app.exception]}")

    def test_empty_states_render_without_exceptions(self):
        db.reset_all()
        pages = ["🏠  Dashboard", "📚  Subjects", "📝  Tasks", "⏱️  Study Sessions", "📊  Analytics", "⚙️  Settings"]
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        for page in pages:
            app.radio[0].set_value(page).run()
            self.assertFalse(app.exception, f"{page}: {[str(error.value) for error in app.exception]}")

    def test_dashboard_deadline_metrics_and_task_crud_search_status(self):
        app = self.run_app()
        dashboard_text = " ".join(item.value for item in app.markdown)
        self.assertIn('metric-label">Due today</div><div class="metric-value">1</div>', dashboard_text)
        self.assertIn('metric-label">Overdue</div><div class="metric-value">0</div>', dashboard_text)

        app = self.run_app("📝  Tasks")
        app.text_input[0].set_value("Task three")
        app.button(key="FormSubmitter:task_form_new-＋ Add task").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertIn("Task three", db.tasks().title.tolist())

        app.button(key="edit_1").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        app.text_input[2].set_value("Task one revised")
        app.button(key="FormSubmitter:task_form_1-Save task").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertIn("Task one revised", db.tasks().title.tolist())

        app.text_input[1].set_value("[").run()
        self.assertFalse(app.exception, "Literal regex characters should not break search")
        app.text_input[1].set_value("Task one revised").run()
        self.assertIn("1 task shown", [item.value for item in app.caption])

        app.text_input[1].set_value("").run()
        app.selectbox(key="status_2").set_value("Completed").run()
        self.assertEqual(db.tasks().set_index("id").loc[2, "status"], "Completed")
        app.button(key="delete_1").click().run()
        app.button(key="confirm_del_1").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertNotIn(1, db.tasks().id.tolist())

    def test_subject_create_edit_delete_ui(self):
        app = self.run_app("📚  Subjects")
        app.text_input[0].set_value("Discrete Math")
        app.button(key="FormSubmitter:add_subject-Add subject").click().run()
        self.assertIn("Discrete Math", db.subjects().name.tolist())

        subject_id = int(db.subjects().loc[db.subjects().name == "Discrete Math", "id"].iloc[0])
        app.button(key=f"sub_edit_{subject_id}").click().run()
        app.text_input[1].set_value("Discrete Mathematics")
        app.button(key=f"FormSubmitter:edit_subject_{subject_id}-Save changes").click().run()
        self.assertIn("Discrete Mathematics", db.subjects().name.tolist())

        app.button(key=f"sub_del_{subject_id}").click().run()
        confirm = next(button for button in app.button if button.label == "Confirm delete subject")
        confirm.click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertNotIn(subject_id, db.subjects().id.tolist())

    def test_study_session_form_persists_session(self):
        app = self.run_app("⏱️  Study Sessions")
        app.number_input[0].set_value(55)
        app.text_input[0].set_value("Focused practice")
        app.button(key="FormSubmitter:session_form-Save session").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        sessions = db.sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(int(sessions.iloc[0].duration_minutes), 55)
        self.assertEqual(sessions.iloc[0].notes, "Focused practice")


if __name__ == "__main__":
    unittest.main()
