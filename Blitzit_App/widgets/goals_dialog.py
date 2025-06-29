from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QInputDialog, QListWidgetItem
from PyQt6.QtCore import Qt
import database

class GoalsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Goals")
        layout = QVBoxLayout(self)

        self.goal_list = QListWidget()
        layout.addWidget(self.goal_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Goal")
        del_btn = QPushButton("Delete Selected")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(self.add_goal)
        del_btn.clicked.connect(self.delete_goal)

        self.refresh_goals()

    def refresh_goals(self):
        self.goal_list.clear()
        for g in database.get_all_goals():
            item = QListWidgetItem(g['name'])
            item.setData(Qt.ItemDataRole.UserRole, g['id'])
            self.goal_list.addItem(item)

    def add_goal(self):
        name, ok = QInputDialog.getText(self, "New Goal", "Goal name:")
        if ok and name:
            database.add_goal(name)
            self.refresh_goals()

    def delete_goal(self):
        item = self.goal_list.currentItem()
        if item:
            goal_id = item.data(Qt.ItemDataRole.UserRole)
            database.delete_goal(goal_id)
            self.refresh_goals()

