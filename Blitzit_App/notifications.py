# Blitzit_App/notifications.py




import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon


_tray_icon = None
_activation_callback = None

def show_notification(title, message):
    global _tray_icon
    if _tray_icon is None:
        _tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"))
        _tray_icon.setVisible(True)
        if _activation_callback:
            _tray_icon.activated.connect(_activation_callback)
    _tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information)

def init_notifications(app, activation_callback=None):
    # Ensure tray icon is created at app startup
    global _tray_icon, _activation_callback
    _activation_callback = activation_callback
    if _tray_icon is None:
        _tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"))
        _tray_icon.setVisible(True)
        if _activation_callback:
            _tray_icon.activated.connect(_activation_callback)
