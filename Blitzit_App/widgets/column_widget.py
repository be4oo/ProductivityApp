# Blitzit_App/widgets/column_widget.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class DropColumn(QFrame):
    """A QFrame that can accept drops and calculate the drop position."""
    
    # This signal will carry all info needed for both re-ordering and moving columns
    task_dropped = pyqtSignal(str, str, int) # task_id, new_column_name, drop_row_index

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.column_name = title
        self.original_title = title # Store the original title
        self.setAcceptDrops(True)
        self.setObjectName("ColumnFrame")

        self.main_layout = QVBoxLayout(self)
        self.title_label = QLabel(title) # Store title_label as an instance attribute
        self.title_label.setObjectName("ColumnTitle")
        self.main_layout.addWidget(self.title_label)

        self.tasks_layout = QVBoxLayout(); self.tasks_layout.setSpacing(0); self.tasks_layout.setContentsMargins(0,0,0,0)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper_widget = QWidget(); wrapper_widget.setLayout(self.tasks_layout); scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True); scroll_area.setWidget(wrapper_widget); self.main_layout.addWidget(scroll_area)

    def update_task_count_display(self):
        count = self.tasks_layout.count()
        # Special handling for "Today" column's title if it has the "Blitz Now" button
        # The actual title label is within a QHBoxLayout which is the first item in main_layout
        if self.original_title == "Today" and self.main_layout.itemAt(0) and isinstance(self.main_layout.itemAt(0), QHBoxLayout):
            header_layout = self.main_layout.itemAt(0)
            # Assuming the original title QLabel is the first widget in this header_layout
            actual_title_label = header_layout.itemAt(0).widget()
            if actual_title_label and isinstance(actual_title_label, QLabel):
                actual_title_label.setText(f"{self.original_title} ({count})")
        else:
            self.title_label.setText(f"{self.original_title} ({count})")

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