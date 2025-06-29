from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton

class WelcomeDialog(QDialog):
    """Simple onboarding dialog shown on first launch."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Blitzit")
        layout = QVBoxLayout(self)
        msg = (
            "<b>Welcome to Blitzit Productivity Hub!</b><br><br>"
            "Use the <i>Board</i> view to organize tasks by column.\n"
            "Switch to the <i>Matrix</i> view to prioritize them by urgency and importance.\n"
            "Use <b>Blitz Now</b> to focus on tasks in your 'Today' list."
        )
        label = QLabel(msg)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.checkbox = QCheckBox("Don't show this again")
        layout.addWidget(self.checkbox)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    def do_not_show_again(self):
        return self.checkbox.isChecked()
