# Blitzit_App/widgets/column_widget.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class DropColumn(QFrame):
    """A QFrame that can accept drops and calculate the drop position."""
    
    # This signal will carry all info needed for both re-ordering and moving columns
    task_dropped = pyqtSignal(str, str, int) # task_id, new_column_name, drop_row_index

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.column_name = title
        self.setAcceptDrops(True)
        self.setObjectName("ColumnFrame")

        self.main_layout = QVBoxLayout(self); title_label = QLabel(title); title_label.setObjectName("ColumnTitle")
        self.main_layout.addWidget(title_label)
        self.tasks_layout = QVBoxLayout(); self.tasks_layout.setSpacing(0); self.tasks_layout.setContentsMargins(0,0,0,0)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper_widget = QWidget(); wrapper_widget.setLayout(self.tasks_layout); scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True); scroll_area.setWidget(wrapper_widget); self.main_layout.addWidget(scroll_area)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """This event is fired when the item is dropped."""
        task_id = event.mimeData().text()
        
        # --- Calculate drop position (row index) ---
        drop_y = event.position().y()
        insert_pos = 0
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if drop_y > widget.y() + widget.height() / 2:
                insert_pos = i + 1
        
        # Emit our custom signal with all the data
        self.task_dropped.emit(task_id, self.column_name, insert_pos)
        event.acceptProposedAction()