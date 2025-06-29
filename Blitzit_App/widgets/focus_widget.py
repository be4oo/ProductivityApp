# Blitzit_App/widgets/focus_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import qtawesome as qta
import database

def format_seconds_to_str(total_seconds): # This helper is now also used by the floating widget
    is_negative = total_seconds < 0
    if is_negative: total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600); minutes, seconds = divmod(remainder, 60)
    prefix = "-" if is_negative else ""
    if hours > 0: return f"{prefix}{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    else: return f"{prefix}{int(minutes):02}:{int(seconds):02}"

class FocusOverlay(QWidget):
    exit_focus_requested = pyqtSignal()
    task_completed_in_focus = pyqtSignal()
    skip_to_next_task = pyqtSignal()
    mini_mode_requested = pyqtSignal() # <--- NEW SIGNAL

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_task_id = None; self.initial_actual_seconds = 0; self.session_seconds_elapsed = 0
        self.is_paused = True; self.is_overtime = False; self.time_left_seconds = 0
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_timer)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        background = QFrame(self); background.setObjectName("FocusBackground"); main_layout = QVBoxLayout(self); main_layout.addWidget(background)
        content_layout = QVBoxLayout(background); content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); content_layout.setSpacing(20)
        self.task_label = QLabel("Focused Task"); self.task_label.setObjectName("FocusTaskTitle")
        self.time_label = QLabel("00:00"); self.time_label.setObjectName("FocusTimerDisplay")
        self.subtext_label = QLabel("Estimated Time"); self.subtext_label.setObjectName("FocusSubtext")
        main_controls_layout = QHBoxLayout(); main_controls_layout.setSpacing(20)
        self.start_pause_btn = QPushButton(qta.icon('fa5s.play'), " Start"); self.done_btn = QPushButton(qta.icon('fa5s.check-circle'), " Done")
        self.start_pause_btn.setObjectName("FocusControlButton"); self.done_btn.setObjectName("FocusControlButton")
        self.start_pause_btn.clicked.connect(self.toggle_start_pause); self.done_btn.clicked.connect(self.task_completed_in_focus.emit)
        main_controls_layout.addWidget(self.start_pause_btn); main_controls_layout.addWidget(self.done_btn)
        secondary_controls_layout = QHBoxLayout(); secondary_controls_layout.setSpacing(15)
        self.break_btn = QPushButton("Take a Break"); self.skip_btn = QPushButton("Skip Task"); self.exit_btn = QPushButton("Exit Focus")
        
        # *** ADD THE NEW PIN BUTTON ***
        self.pin_btn = QPushButton(qta.icon('fa5s.thumbtack'), " Mini Mode")
        self.pin_btn.setObjectName("FocusControlButton")
        self.pin_btn.clicked.connect(self.mini_mode_requested.emit)
        
        self.break_btn.setObjectName("FocusControlButton"); self.skip_btn.setObjectName("FocusControlButton"); self.exit_btn.setObjectName("FocusControlButton")
        self.exit_btn.clicked.connect(self.exit_focus_requested.emit); self.skip_btn.clicked.connect(self.skip_to_next_task.emit)
        secondary_controls_layout.addWidget(self.break_btn); secondary_controls_layout.addWidget(self.skip_btn)
        secondary_controls_layout.addWidget(self.pin_btn) # Add it to the layout
        secondary_controls_layout.addWidget(self.exit_btn)
        
        content_layout.addStretch(); content_layout.addWidget(self.task_label, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignCenter); content_layout.addWidget(self.subtext_label, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacing(40); content_layout.addLayout(main_controls_layout); content_layout.addSpacing(20)
        content_layout.addLayout(secondary_controls_layout); content_layout.addStretch()
    
    # All other methods are unchanged
    def update_timer(self):
        self.time_left_seconds -= 1; self.session_seconds_elapsed += 1
        display_time = self.time_left_seconds
        if self.time_left_seconds < 0:
            if not self.is_overtime:
                self.is_overtime = True; self.time_label.setProperty("overtime", True); self.subtext_label.setText("Overtime")
                self.time_label.style().unpolish(self.time_label); self.time_label.style().polish(self.time_label)
            display_time = abs(self.time_left_seconds)
        self.time_label.setText(format_seconds_to_str(display_time))
    def save_progress(self):
        if self.current_task_id is None: return
        total_seconds_worked = self.initial_actual_seconds + self.session_seconds_elapsed
        total_minutes_worked = round(total_seconds_worked / 60)
        database.update_actual_time(self.current_task_id, total_minutes_worked)
    def start_focus_session(self, task_data):
        self.current_task_id = task_data['id']; self.task_label.setText(task_data['title'])
        self.initial_actual_seconds = (task_data['actual_time'] or 0) * 60; self.session_seconds_elapsed = 0
        self.is_overtime = False; self.time_label.setProperty("overtime", False)
        self.time_label.style().unpolish(self.time_label); self.time_label.style().polish(self.time_label)
        estimated_seconds = (task_data['estimated_time'] or 0) * 60
        self.time_left_seconds = estimated_seconds - self.initial_actual_seconds
        if estimated_seconds > 0: self.subtext_label.setText("Time Remaining")
        else: self.time_left_seconds = (25*60) - self.initial_actual_seconds; self.subtext_label.setText("Focus Session")
        self.time_label.setText(format_seconds_to_str(self.time_left_seconds))
        self.is_paused = True; self.toggle_start_pause()
    def toggle_start_pause(self):
        if self.is_paused:
            self.timer.start(1000); self.start_pause_btn.setText(" Pause"); self.start_pause_btn.setIcon(qta.icon('fa5s.pause'))
        else:
            self.timer.stop(); self.save_progress(); self.start_pause_btn.setText(" Start"); self.start_pause_btn.setIcon(qta.icon('fa5s.play'))
        self.is_paused = not self.is_paused