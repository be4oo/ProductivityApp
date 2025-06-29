# Blitzit_App/widgets/today_list_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea, QSizeGrip
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
import qtawesome as qta

class TodayListWidget(QWidget):
    """A floating, always-on-top widget to display the 'Today' list."""
    
    enlarge_requested = pyqtSignal()
    focus_on_task_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(350)
        self._drag_pos = None

        self.main_frame = QFrame(self); self.main_frame.setObjectName("FloatingFrame")
        main_layout = QVBoxLayout(self.main_frame); main_layout.setContentsMargins(15, 10, 15, 10); main_layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Today's Focus"); title_label.setObjectName("FloatingTaskLabel")
        self.enlarge_btn = QPushButton(qta.icon('fa5s.expand-arrows-alt'), ""); self.enlarge_btn.setObjectName("FloatingControlButton")
        self.enlarge_btn.clicked.connect(self.enlarge_requested.emit)
        header_layout.addWidget(title_label); header_layout.addStretch(); header_layout.addWidget(self.enlarge_btn)
        
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setObjectName("TodayListScroll")
        scroll_content = QWidget()
        self.tasks_layout = QVBoxLayout(scroll_content); self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.tasks_layout.setSpacing(5)
        scroll_area.setWidget(scroll_content)

        # --- NEW: Add a size grip for resizing ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        size_grip = QSizeGrip(self)
        bottom_layout.addWidget(size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(bottom_layout) # Add the size grip to the layout

        outer_layout = QVBoxLayout(self); outer_layout.setContentsMargins(0,0,0,0); outer_layout.addWidget(self.main_frame)
        
    def populate_tasks(self, tasks):
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        for task in tasks:
            task_item = self._create_task_item(task)
            self.tasks_layout.addWidget(task_item)

    def _create_task_item(self, task):
        widget = QFrame(); widget.setObjectName("TodayListItem")
        layout = QHBoxLayout(widget)
        title = QLabel(task['title'])
        focus_btn = QPushButton(qta.icon('fa5s.play-circle', color_active='#2ecc71'), "")
        focus_btn.setObjectName("FloatingControlButton")
        focus_btn.clicked.connect(lambda checked, tid=task['id']: self.focus_on_task_requested.emit(tid))
        layout.addWidget(title); layout.addStretch(); layout.addWidget(focus_btn)
        return widget

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton: self._drag_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos); self._drag_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event: QMouseEvent): self._drag_pos = None