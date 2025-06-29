# Blitzit_App/widgets/floating_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QMouseEvent
import qtawesome as qta
import database

def format_seconds_to_str(total_seconds):
    is_negative = total_seconds < 0
    if is_negative: total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600); minutes, seconds = divmod(remainder, 60)
    prefix = "-" if is_negative else ""
    if hours > 0: return f"{prefix}{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    else: return f"{prefix}{int(minutes):02}:{int(seconds):02}"

class FloatingWidget(QWidget):
    """The 'Mini Mode' - a compact, always-on-top widget for a single focus task."""
    enlarge_requested = pyqtSignal(); pause_toggled = pyqtSignal(bool)
    skip_requested = pyqtSignal(); task_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self._drag_pos = None
        
        self.is_paused = True; self.time_left_seconds = 0
        self.initial_actual_seconds = 0  # Ensure always defined
        self.session_seconds_elapsed = 0  # Ensure always defined
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_timer)
        
        # --- Create icons ONCE to prevent recursion error ---
        self.play_icon = qta.icon('fa5s.play', color_active='white')
        self.pause_icon = qta.icon('fa5s.pause', color_active='white')

        self.main_frame = QFrame(self); self.main_frame.setObjectName("FloatingFrame")
        main_layout = QVBoxLayout(self.main_frame); main_layout.setContentsMargins(10, 5, 10, 5)
        top_layout = QHBoxLayout(); self.task_label = QLabel("Current Task..."); self.task_label.setObjectName("FloatingTaskLabel")
        self.enlarge_btn = QPushButton(qta.icon('fa5s.expand-arrows-alt'), ""); self.enlarge_btn.setObjectName("FloatingControlButton")
        self.enlarge_btn.clicked.connect(self.enlarge_requested.emit)
        top_layout.addWidget(self.task_label); top_layout.addStretch(); top_layout.addWidget(self.enlarge_btn)
        self.time_label = QLabel("00:00"); self.time_label.setObjectName("FloatingTimerDisplay")
        bottom_layout = QHBoxLayout()
        self.pause_btn = QPushButton(self.play_icon, ""); self.pause_btn.setObjectName("FloatingControlButton")
        self.done_btn = QPushButton(qta.icon('fa5s.check-circle', color_active='#2ecc71'), ""); self.done_btn.setObjectName("FloatingControlButton")
        self.skip_btn = QPushButton(qta.icon('fa5s.forward'), ""); self.skip_btn.setObjectName("FloatingControlButton")
        self.pause_btn.clicked.connect(self.toggle_pause); self.done_btn.clicked.connect(self.task_completed.emit); self.skip_btn.clicked.connect(self.skip_requested.emit)
        bottom_layout.addStretch(); bottom_layout.addWidget(self.pause_btn); bottom_layout.addWidget(self.done_btn); bottom_layout.addWidget(self.skip_btn); bottom_layout.addStretch()
        main_layout.addLayout(top_layout); main_layout.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignCenter); main_layout.addLayout(bottom_layout)
        outer_layout = QVBoxLayout(self); outer_layout.setContentsMargins(0,0,0,0); outer_layout.addWidget(self.main_frame)
        self.setStyleSheet("""
            #FloatingFrame { background-color: #22272e; border: 1px solid #404753; border-radius: 8px; }
            #FloatingFrame[overtime="true"] { border-color: #da4453; }
            #FloatingTaskLabel { color: #cdd9e5; font-size: 11pt; }
            #FloatingTimerDisplay { color: #cdd9e5; font-size: 24pt; font-weight: bold; }
            #FloatingTimerDisplay[overtime="true"] { color: #da4453; }
            #FloatingControlButton { background-color: transparent; border: none; color: #909dab; padding: 4px; }
            #FloatingControlButton:hover { color: white; }
        """)

    def start_session(self, task_data):
        self.timer.stop(); self.task_label.setText(task_data['title'])
        self.initial_actual_seconds = (task_data['actual_time'] or 0) * 60; self.session_seconds_elapsed = 0
        estimated_seconds = (task_data['estimated_time'] or 0) * 60
        self.time_left_seconds = estimated_seconds - self.initial_actual_seconds
        self.is_paused = True; self.toggle_pause() # This will set the correct icon and start the timer
    def update_timer(self):
        self.time_left_seconds -= 1; self.session_seconds_elapsed += 1; self.update_display()
    def update_display(self):
        is_overtime = self.time_left_seconds < 0
        self.time_label.setProperty("overtime", is_overtime); self.main_frame.setProperty("overtime", is_overtime)
        self.time_label.style().unpolish(self.time_label); self.time_label.style().polish(self.time_label)
        self.main_frame.style().unpolish(self.main_frame); self.main_frame.style().polish(self.main_frame)
        self.time_label.setText(format_seconds_to_str(abs(self.time_left_seconds)))
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop(); self.pause_btn.setIcon(self.play_icon)
        else:
            self.timer.start(1000); self.pause_btn.setIcon(self.pause_icon)
        self.pause_toggled.emit(self.is_paused)
    def save_progress(self):
        total_seconds_worked = self.initial_actual_seconds + self.session_seconds_elapsed
        return round(total_seconds_worked / 60)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton: self._drag_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos); self._drag_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event: QMouseEvent): self._drag_pos = None