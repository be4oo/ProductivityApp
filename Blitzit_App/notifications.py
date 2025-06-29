from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
import database
from datetime import datetime, timedelta

tray_icon = None

def init_notifications(app: QApplication):
    global tray_icon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return
    tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"), app)
    tray_icon.show()
    timer = QTimer()
    timer.timeout.connect(check_due_tasks)
    timer.start(60000)  # check every minute


def show_notification(title, message):
    if tray_icon:
        tray_icon.showMessage(title, message)


def check_due_tasks():
    tasks = database.get_all_tasks_from_all_projects()
    now = datetime.now()
    for t in tasks:
        if t['due_date'] and t['reminder_enabled']:
            due = datetime.fromisoformat(t['due_date'])
            if now >= due and (t['completed_at'] is None):
                show_notification("Task Due", t['title'])
