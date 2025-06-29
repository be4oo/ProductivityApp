# Blitzit_App/widgets/task_widgets.py
import re
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox, QDialogButtonBox, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QPixmap
import qtawesome as qta

# Helper functions are unchanged
def format_time(minutes):
    if not minutes or minutes == 0: return ""
    hours, mins = divmod(minutes, 60); parts = []
    if hours > 0: parts.append(f"{hours}h")
    if mins > 0: parts.append(f"{mins}m")
    return " ".join(parts)
def parse_time_string_to_minutes(time_str: str) -> int:
    if not time_str: return 0
    total_minutes = 0; matches = re.findall(r'(\d+)\s*(h|m)', time_str, re.IGNORECASE)
    if not matches and time_str.strip().isdigit(): return int(time_str.strip())
    for value, unit in matches:
        value = int(value)
        if unit.lower() == 'h': total_minutes += value * 60
        elif unit.lower() == 'm': total_minutes += value
    return total_minutes

class TaskWidget(QFrame):
    task_completed = pyqtSignal(int); task_deleted = pyqtSignal(int); task_edit_requested = pyqtSignal(int)
    focus_requested = pyqtSignal(int); task_reopened = pyqtSignal(int)

    def __init__(self, task):
        super().__init__(); self.task_id = task['id']; self.setObjectName("TaskWidget"); self.column_name = task['column']
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(12, 12, 12, 12); main_layout.setSpacing(8)
        top_row_layout = QHBoxLayout(); top_row_layout.setSpacing(10)
        title_label = QLabel(task['title']); title_label.setObjectName("TaskTitle")
        top_row_layout.addWidget(title_label); top_row_layout.addStretch()
        if task['task_priority']:
            priority_label = QLabel(task['task_priority']); priority_label.setObjectName(f"Priority{task['task_priority']}")
            top_row_layout.addWidget(priority_label)
        if task['task_type']:
            type_label = QLabel(task['task_type']); type_label.setObjectName(f"Type{task['task_type']}")
            top_row_layout.addWidget(type_label)
        main_layout.addLayout(top_row_layout)
        notes_label = QLabel(task['notes']); notes_label.setObjectName("TaskNotes"); notes_label.setWordWrap(True)
        main_layout.addWidget(notes_label)
        time_layout = QHBoxLayout(); time_layout.setContentsMargins(0, 8, 0, 0)
        est_time_str = format_time(task['estimated_time']); est_time_label = QLabel(f"Est: {est_time_str}")
        act_time_str = format_time(task['actual_time']); act_time_label = QLabel(f"Actual: {act_time_str}")
        est_time_label.setObjectName("TimeEstLabel"); act_time_label.setObjectName("TimeActLabel")
        time_layout.addWidget(est_time_label); time_layout.addStretch(); time_layout.addWidget(act_time_label)
        main_layout.addLayout(time_layout)
        button_layout = QHBoxLayout(); button_layout.setContentsMargins(0, 8, 0, 0)
        if self.column_name == "Done":
            self.setProperty("class", "done-task")
            reopen_btn = QPushButton(qta.icon('fa5s.undo-alt'), " Re-open"); delete_btn = QPushButton(qta.icon('fa5s.trash-alt'), "")
            reopen_btn.setObjectName("TaskActionButton"); delete_btn.setObjectName("TaskActionButton")
            reopen_btn.clicked.connect(lambda: self.task_reopened.emit(self.task_id)); delete_btn.clicked.connect(lambda: self.task_deleted.emit(self.task_id))
            button_layout.addStretch(); button_layout.addWidget(reopen_btn); button_layout.addWidget(delete_btn)
        else:
            focus_btn = QPushButton(qta.icon('fa5s.play-circle'), ""); edit_btn = QPushButton(qta.icon('fa5s.pencil-alt'), "")
            done_btn = QPushButton(qta.icon('fa5s.check-circle'), " Done")
            for btn in [focus_btn, edit_btn, done_btn]: btn.setObjectName("TaskActionButton")
            focus_btn.clicked.connect(lambda: self.focus_requested.emit(self.task_id)); edit_btn.clicked.connect(lambda: self.task_edit_requested.emit(self.task_id))
            done_btn.clicked.connect(lambda: self.task_completed.emit(self.task_id))
            button_layout.addStretch(); button_layout.addWidget(focus_btn); button_layout.addWidget(edit_btn); button_layout.addWidget(done_btn)
        main_layout.addLayout(button_layout)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.MouseButton.LeftButton: return
        drag = QDrag(self); mime_data = QMimeData()
        # *** THE SIMPLIFIED DRAG DATA ***
        mime_data.setText(str(self.task_id))
        drag.setMimeData(mime_data); pixmap = self.grab(); pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        drag.setPixmap(pixmap); drag.setHotSpot(event.position().toPoint()); drag.exec(Qt.DropAction.MoveAction)

# AddTaskDialog and EditTaskDialog classes are unchanged
class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Add New Task"); self.layout = QVBoxLayout(self); form_layout = QFormLayout()
        self.title_input = QLineEdit(); self.notes_input = QTextEdit(); self.notes_input.setFixedHeight(80)
        self.time_input = QLineEdit(); self.time_input.setPlaceholderText("e.g., 1h 30m or 45m")
        self.type_input = QComboBox(); self.type_input.addItems(["", "Work", "Personal", "Other"])
        self.priority_input = QComboBox(); self.priority_input.addItems(["", "Low", "Medium", "High"])
        form_layout.addRow("Title:", self.title_input); form_layout.addRow("Notes:", self.notes_input)
        form_layout.addRow("Est. Time:", self.time_input); form_layout.addRow("Type:", self.type_input)
        form_layout.addRow("Priority:", self.priority_input); self.layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept); button_box.rejected.connect(self.reject); self.layout.addWidget(button_box)
    def get_task_data(self):
        return {"title": self.title_input.text(), "notes": self.notes_input.toPlainText(), "estimated_time": parse_time_string_to_minutes(self.time_input.text()), "task_type": self.type_input.currentText(), "task_priority": self.priority_input.currentText()}
class EditTaskDialog(QDialog):
    def __init__(self, task_data, parent=None):
        super().__init__(parent); self.setWindowTitle("Edit Task"); self.layout = QVBoxLayout(self); form_layout = QFormLayout()
        self.title_input = QLineEdit(task_data['title']); self.notes_input = QTextEdit(task_data['notes']); self.notes_input.setFixedHeight(80)
        self.time_input = QLineEdit(); self.time_input.setText(format_time(task_data['estimated_time']))
        self.type_input = QComboBox(); self.type_input.addItems(["", "Work", "Personal", "Other"]); self.type_input.setCurrentText(task_data['task_type'] or "")
        self.priority_input = QComboBox(); self.priority_input.addItems(["", "Low", "Medium", "High"]); self.priority_input.setCurrentText(task_data['task_priority'] or "")
        form_layout.addRow("Title:", self.title_input); form_layout.addRow("Notes:", self.notes_input)
        form_layout.addRow("Est. Time:", self.time_input); form_layout.addRow("Type:", self.type_input); form_layout.addRow("Priority:", self.priority_input)
        self.layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept); button_box.rejected.connect(self.reject); self.layout.addWidget(button_box)
    def get_updated_data(self):
        return {"title": self.title_input.text(), "notes": self.notes_input.toPlainText(), "estimated_time": parse_time_string_to_minutes(self.time_input.text()), "task_type": self.type_input.currentText(), "task_priority": self.priority_input.currentText()}