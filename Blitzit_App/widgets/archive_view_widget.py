# Blitzit_App/widgets/archive_view_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
import qtawesome as qta

class ArchivedTaskItemWidget(QWidget):
    """Custom widget for displaying an archived task item."""
    unarchive_requested = pyqtSignal(int)

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_id = task_data['id']

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        title_text = f"{task_data['title']}"
        if task_data.get('project_name'): # Assuming project_name might be added to task_data for this view
            title_text += f" (Project: {task_data['project_name']})"

        title_label = QLabel(title_text)
        title_label.setWordWrap(True)

        # Display completion date if available
        completed_at_text = ""
        if task_data.get('completed_at'):
            if isinstance(task_data['completed_at'], str):
                completed_at_text = f" (Completed: {task_data['completed_at'][:10]})" # Show date part
            else: # Assuming it's a datetime object
                completed_at_text = f" (Completed: {task_data['completed_at'].strftime('%Y-%m-%d')})"

        info_label = QLabel(f"ID: {self.task_id}{completed_at_text}")
        info_label.setObjectName("ArchivedTaskInfoLabel")


        unarchive_button = QPushButton(qta.icon('fa5s.undo-alt'), " Unarchive")
        unarchive_button.setObjectName("TaskActionButton")
        unarchive_button.clicked.connect(lambda: self.unarchive_requested.emit(self.task_id))

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(info_label)
        layout.addWidget(unarchive_button)


class ArchivedTasksWidget(QWidget):
    task_unarchive_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ArchivedTasksView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("Archived Tasks")
        title_label.setObjectName("ViewTitle") # Potentially style this like ColumnTitle
        main_layout.addWidget(title_label)

        self.archived_list_widget = QListWidget()
        self.archived_list_widget.setObjectName("ArchivedTasksList")
        main_layout.addWidget(self.archived_list_widget)

    def populate_archived_tasks(self, archived_tasks_data):
        self.archived_list_widget.clear()
        if not archived_tasks_data:
            # Placeholder item if no archived tasks
            placeholder_item = QListWidgetItem("No archived tasks found.")
            placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.archived_list_widget.addItem(placeholder_item)
            return

        for task_data in archived_tasks_data:
            list_item = QListWidgetItem(self.archived_list_widget)
            item_widget = ArchivedTaskItemWidget(task_data)
            item_widget.unarchive_requested.connect(self.task_unarchive_requested) # Forward the signal

            list_item.setSizeHint(item_widget.sizeHint())
            self.archived_list_widget.addItem(list_item)
            self.archived_list_widget.setItemWidget(list_item, item_widget)

    def clear_view(self):
        self.archived_list_widget.clear()
