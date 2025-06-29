# Blitzit_App/widgets/timer_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QFont

class TimerWidget(QWidget):
    """A widget implementing full Pomodoro cycles."""

    # Define Pomodoro session lengths in minutes
    WORK_MINUTES = 25
    SHORT_BREAK_MINUTES = 5
    LONG_BREAK_MINUTES = 15
    CYCLES_BEFORE_LONG_BREAK = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.is_work_session = True
        self.session_count = 0
        self.is_paused = True
        
        # QTimer is the heart of our countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        
        # Set the initial time
        self.time_left = QTime(0, self.WORK_MINUTES, 0)

        # --- UI Setup ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Status Label (Work/Break)
        self.status_label = QLabel("Work Session")
        self.status_label.setObjectName("TimerStatus")

        # Time Display Label
        self.time_label = QLabel(self.time_left.toString("mm:ss"))
        self.time_label.setObjectName("TimerDisplay")
        # Make the font bigger and bold
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.time_label.setFont(font)

        # Control Buttons
        self.start_pause_btn = QPushButton("Start")
        self.reset_btn = QPushButton("Reset")

        # Connect buttons to their functions
        self.start_pause_btn.clicked.connect(self.toggle_start_pause)
        self.reset_btn.clicked.connect(self.reset_timer)

        layout.addWidget(self.status_label)
        layout.addSpacing(20)
        layout.addWidget(self.time_label)
        layout.addSpacing(10)
        layout.addWidget(self.start_pause_btn)
        layout.addWidget(self.reset_btn)

        self.setStyleSheet("""
            #TimerStatus { font-style: italic; color: #666; }
            #TimerDisplay { color: #333; }
        """)

    def update_countdown(self):
        """This method is called every second by the QTimer."""
        self.time_left = self.time_left.addSecs(-1)
        self.time_label.setText(self.time_left.toString("mm:ss"))

        # Check if the timer has reached zero
        if self.time_left == QTime(0, 0, 0):
            self.timer.stop()
            self.switch_session()

    def toggle_start_pause(self):
        """Starts or pauses the timer."""
        if self.is_paused:
            self.timer.start(1000) # Start timer, timeout signal will be emitted every 1000ms (1s)
            self.start_pause_btn.setText("Pause")
        else:
            self.timer.stop()
            self.start_pause_btn.setText("Start")
        self.is_paused = not self.is_paused

    def current_session_minutes(self):
        if self.is_work_session:
            return self.WORK_MINUTES
        if self.session_count % self.CYCLES_BEFORE_LONG_BREAK == 0:
            return self.LONG_BREAK_MINUTES
        return self.SHORT_BREAK_MINUTES

    def reset_timer(self):
        """Resets the timer to the current session's default time."""
        self.timer.stop()
        minutes = self.current_session_minutes()
        self.time_left = QTime(0, minutes, 0)
        self.time_label.setText(self.time_left.toString("mm:ss"))
        self.is_paused = True
        self.start_pause_btn.setText("Start")

    def switch_session(self):
        """Switches between work and break sessions automatically."""
        if self.is_work_session:
            self.session_count += 1
            self.is_work_session = False
        else:
            self.is_work_session = True
        if self.is_work_session:
            self.status_label.setText("Work Session")
        else:
            if self.session_count % self.CYCLES_BEFORE_LONG_BREAK == 0:
                self.status_label.setText("Long Break")
            else:
                self.status_label.setText("Break Time!")
        self.reset_timer()
        self.toggle_start_pause()
