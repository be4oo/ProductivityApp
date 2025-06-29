# Blitzit_App/notifications.py
from PyQt6.QtCore import QObject, QTimer, QDateTime, Qt
import sqlite3 # For type hinting if needed, actual db calls via database module
from datetime import datetime as py_datetime

# Assuming database.py is in the parent directory or PYTHONPATH is set up
# For direct execution/testing, you might need to adjust imports
try:
    import database
except ImportError:
    # This is a fallback for cases where the module might be run directly
    # or the path isn't correctly set for the linter/IDE in this context.
    # The main app should handle the Python path correctly.
    print("Could not import 'database' directly in notifications.py, ensure PYTHONPATH is correct or Blitzit_App is a package.")
    database = None


class NotificationManager(QObject):
    show_notification_signal = pyqtSignal(str, str) # task_id, task_title

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_reminders)
        self.check_interval_ms = 60 * 1000 # Check every 60 seconds

    def start(self):
        if database is None:
            print("NotificationManager: Database module not available. Cannot start.")
            return
        print("Notification Manager started.")
        self.timer.start(self.check_interval_ms)
        self.check_for_reminders() # Initial check

    def stop(self):
        self.timer.stop()
        print("Notification Manager stopped.")

    def get_tasks_needing_notification(self):
        """
        Fetches tasks from the database that need a notification.
        A task needs notification if:
        1. It has a reminder_at time set.
        2. The reminder_at time is in the past.
        3. It has not been notified yet for this reminder_at time
           (i.e., last_notified_at is NULL or last_notified_at < reminder_at).
        """
        conn = database.get_db_connection()
        cursor = conn.cursor()
        now_iso = QDateTime.currentDateTime().toString(Qt.DateFormat.ISODateWithMs)

        # Query for tasks that have a reminder_at, it's in the past,
        # and (last_notified_at is null OR last_notified_at is older than reminder_at)
        # This ensures if a reminder_at is updated to the past, it can re-notify.
        # Also ensure task is not done or archived.
        query = """
            SELECT id, title, reminder_at
            FROM tasks
            WHERE reminder_at IS NOT NULL
              AND reminder_at <= ?
              AND (last_notified_at IS NULL OR last_notified_at < reminder_at)
              AND status != 'archived'
              AND column != 'Done'
        """
        # Using py_datetime.now().isoformat() might be more robust if QDateTime isn't available easily here
        # For SQLite, storing dates as ISO8601 strings is common and comparable.
        cursor.execute(query, (py_datetime.now().isoformat(),))
        tasks_to_notify = cursor.fetchall()
        conn.close()
        return tasks_to_notify

    def check_for_reminders(self):
        # print(f"Checking for reminders at {QDateTime.currentDateTime().toString()}")
        if database is None:
            return

        tasks = self.get_tasks_needing_notification()
        for task_row in tasks:
            task_id = task_row['id']
            task_title = task_row['title']
            # print(f"Reminder for task ID: {task_id}, Title: {task_title}")
            self.show_notification_signal.emit(str(task_id), task_title)
            # The actual update of last_notified_at will be handled by the main app
            # after the notification is confirmed to be shown.
            # This avoids issues if the notification fails to show.

    def set_check_interval(self, minutes):
        self.check_interval_ms = int(minutes * 60 * 1000)
        if self.timer.isActive():
            self.timer.start(self.check_interval_ms)

# Example of how this might be used (for testing or if run standalone)
if __name__ == '__main__':
    # This part is for testing the NotificationManager independently.
    # It requires database.py to be accessible.
    # You'd need a dummy QApplication for QTimer to work.
    from PyQt6.QtWidgets import QApplication
    import sys

    # Ensure database path is correct if running standalone for testing
    # This assumes tasks.db is in data/ relative to where this script is run
    # or that database.DB_PATH is correctly configured.
    # For this test, we might need to initialize the database if it's empty.

    # A simple way to test if database is available and setup:
    if database:
        # database.migrate_database() # Ensure schema exists
        # Example: Add a test task that needs notification
        # conn = database.get_db_connection()
        # now = QDateTime.currentDateTime()
        # reminder_time = now.addSecs(-60) # 1 minute ago
        # due_time = now.addDays(1)
        # cursor = conn.cursor()
        # try:
        #     cursor.execute("""
        #         INSERT INTO tasks (title, notes, project_id, column, status, due_date, reminder_at)
        #         VALUES (?, ?, ?, ?, ?, ?, ?)
        #     """, ("Test Notification Task", "This is a test.", 1, "Today", "pending",
        #           due_time.toString(Qt.DateFormat.ISODateWithMs),
        #           reminder_time.toString(Qt.DateFormat.ISODateWithMs)))
        #     conn.commit()
        #     print("Test task inserted.")
        # except sqlite3.Error as e:
        #     print(f"Error inserting test task: {e}")
        # finally:
        #     conn.close()

        app = QApplication(sys.argv)
        manager = NotificationManager()

        def handle_notification(task_id, title):
            print(f"--- Main App: Received notification for task ID {task_id}: {title} ---")
            # In real app, here you'd call database.update_task_last_notified
            # For testing, we'll just print.
            # database.update_task_last_notified(int(task_id), QDateTime.currentDateTime().toString(Qt.DateFormat.ISODateWithMs))

        manager.show_notification_signal.connect(handle_notification)
        manager.start()

        # Keep app running for a bit to see timer checks
        # QTimer.singleShot(10 * 1000, app.quit) # Quit after 10 seconds for testing

        print("Test NotificationManager running. Check console for outputs. Will run indefinitely unless quit.")
        sys.exit(app.exec())
    else:
        print("Database module not loaded. Cannot run NotificationManager test.")
