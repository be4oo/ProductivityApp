# Blitzit_App/widgets/eisenhower_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal

class QuadrantWidget(QFrame):
    """A Quadrant that can now accept task drops."""
    task_dropped = pyqtSignal(str) 

    def __init__(self, title, is_urgent, is_important, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True); self.setObjectName("QuadrantFrame")
        self.is_urgent = is_urgent; self.is_important = is_important
        layout = QVBoxLayout(self); title_label = QLabel(title); title_label.setObjectName("QuadrantTitle")
        layout.addWidget(title_label); scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(); self.tasks_layout = QVBoxLayout(scroll_content)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop); scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain"): event.acceptProposedAction()

    def dropEvent(self, event):
        task_id = event.mimeData().text().split(',')[0]
        self.task_dropped.emit(task_id); event.acceptProposedAction()
    
    def clear_tasks(self):
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()


class EisenhowerMatrix(QWidget):
    """The main widget for the Eisenhower Matrix view, now droppable."""
    task_dropped_in_quadrant = pyqtSignal(int, bool, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        grid_layout = QGridLayout(self); grid_layout.setSpacing(15)
        self.q1 = QuadrantWidget("Urgent & Important", True, True)
        self.q2 = QuadrantWidget("Not Urgent & Important", False, True)
        self.q3 = QuadrantWidget("Urgent & Not Important", True, False)
        self.q4 = QuadrantWidget("Not Urgent & Not Important", False, False)
        self.q1.task_dropped.connect(lambda tid: self.on_task_dropped(tid, self.q1))
        self.q2.task_dropped.connect(lambda tid: self.on_task_dropped(tid, self.q2))
        self.q3.task_dropped.connect(lambda tid: self.on_task_dropped(tid, self.q3))
        self.q4.task_dropped.connect(lambda tid: self.on_task_dropped(tid, self.q4))
        grid_layout.addWidget(self.q1, 0, 0); grid_layout.addWidget(self.q2, 0, 1)
        grid_layout.addWidget(self.q3, 1, 0); grid_layout.addWidget(self.q4, 1, 1)

    def on_task_dropped(self, task_id_str, quadrant):
        task_id = int(task_id_str)
        self.task_dropped_in_quadrant.emit(task_id, quadrant.is_urgent, quadrant.is_important)
    
    # --- THIS IS THE MISSING FUNCTION, NOW ADDED ---
    def clear_all_quadrants(self):
        """Calls clear_tasks on all quadrant widgets."""
        for q in [self.q1, self.q2, self.q3, self.q4]:
            q.clear_tasks()

    def populate_matrix(self, tasks):
        from .task_widgets import TaskWidget 
        self.clear_all_quadrants() # Now this will work
        for task in tasks:
            is_urgent = task['column'] == "Today"; is_important = task['task_priority'] == "High"
            task_widget = TaskWidget(task)
            if is_urgent and is_important: self.q1.tasks_layout.addWidget(task_widget)
            elif not is_urgent and is_important: self.q2.tasks_layout.addWidget(task_widget)
            elif is_urgent and not is_important: self.q3.tasks_layout.addWidget(task_widget)
            else: self.q4.tasks_layout.addWidget(task_widget)