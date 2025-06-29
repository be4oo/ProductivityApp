# Blitzit_App/main.py
import sys, os, json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QListWidget, QListWidgetItem, QInputDialog, 
                             QMessageBox, QSpacerItem, QSizePolicy, QStackedWidget, QMenu, QColorDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QFontDatabase # <--- Import QFontDatabase
import qtawesome as qta

import database
from widgets.task_widgets import AddTaskDialog, EditTaskDialog, TaskWidget
from widgets.focus_widget import FocusOverlay
from widgets.reporting_dialog import ReportingDialog
from widgets.celebration_widget import CelebrationWidget
from widgets.column_widget import DropColumn
from widgets.eisenhower_widget import EisenhowerMatrix, QuadrantWidget
from widgets.floating_widget import FloatingWidget
from widgets.today_list_widget import TodayListWidget

# --- CONFIG AND STYLESHEET MANAGEMENT ---
CONFIG_FILE = "config.json"

def load_config():
    """Loads the configuration file (e.g., for theme choice)."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"theme": "dark"} # Default to dark theme

def save_config(config):
    """Saves the configuration file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_stylesheet(theme_name="dark"):
    """Loads an external QSS stylesheet based on the theme name."""
    file_name = "dark_theme.qss" if theme_name == "dark" else "light_theme.qss"
    try:
        with open(f"ui/{file_name}", "r") as f: return f.read()
    except FileNotFoundError:
        print(f"Stylesheet '{file_name}' not found. Using default styles.")
        return ""

class BlitzitApp(QMainWindow):
    def __init__(self, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.setWindowTitle("Blitzit Productivity Hub")
        self.setMinimumSize(1200, 750)
        
        # --- App State ---
        self.column_order = ["Backlog", "This Week", "Today"]
        self.current_focus_task_id = None
        self.current_project_id = None

        # --- Main Window Structure ---
        self.main_app_widget = QWidget()
        self.setCentralWidget(self.main_app_widget)
        main_layout = QHBoxLayout(self.main_app_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # --- Left Panel ---
        left_panel = QFrame()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(15,15,15,15)
        left_panel_layout.setSpacing(10)
        
        projects_title = QLabel("Projects")
        projects_title.setObjectName("ColumnTitle")
        self.project_list_widget = QListWidget()
        self.project_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_list_widget.customContextMenuRequested.connect(self.open_project_context_menu)
        self.project_list_widget.currentItemChanged.connect(self.on_project_selected)
        
        add_project_btn = QPushButton(qta.icon('fa5s.plus'), " Add Project")
        add_project_btn.clicked.connect(self.add_new_project)
        
        view_switcher_label = QLabel("Views")
        view_switcher_label.setObjectName("ColumnTitle")
        self.board_view_btn = QPushButton(qta.icon('fa5s.columns'), " Board View")
        self.board_view_btn.clicked.connect(lambda: self.switch_view(0))
        self.matrix_view_btn = QPushButton(qta.icon('fa5s.th-large'), " Matrix View")
        self.matrix_view_btn.clicked.connect(lambda: self.switch_view(1))
        
        self.float_btn = QPushButton(qta.icon('fa5s.window-restore'), " Float Today List")
        self.float_btn.clicked.connect(self.enter_today_list_mode)
        
        theme_label = QLabel("Theme")
        theme_label.setObjectName("ColumnTitle")
        theme_button_layout = QHBoxLayout()
        self.dark_theme_btn = QPushButton("Midnight")
        self.dark_theme_btn.clicked.connect(lambda: self.change_theme("dark"))
        self.light_theme_btn = QPushButton("Arctic")
        self.light_theme_btn.clicked.connect(lambda: self.change_theme("light"))
        theme_button_layout.addWidget(self.dark_theme_btn)
        theme_button_layout.addWidget(self.light_theme_btn)

        actions_label = QLabel("Actions")
        actions_label.setObjectName("ColumnTitle")
        self.add_task_btn = QPushButton(qta.icon('fa5s.plus-circle'), " Add Task")
        self.add_task_btn.setObjectName("AddTaskButton")
        self.add_task_btn.clicked.connect(self.open_add_task_dialog)
        self.reports_btn = QPushButton(qta.icon('fa5s.chart-line'), " View Reports")
        self.reports_btn.clicked.connect(self.open_reporting_dialog)
        
        left_panel_layout.addWidget(projects_title)
        left_panel_layout.addWidget(self.project_list_widget)
        left_panel_layout.addWidget(add_project_btn)
        left_panel_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        left_panel_layout.addWidget(view_switcher_label)
        left_panel_layout.addWidget(self.board_view_btn)
        left_panel_layout.addWidget(self.matrix_view_btn)
        left_panel_layout.addWidget(self.float_btn)
        left_panel_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        left_panel_layout.addWidget(theme_label)
        left_panel_layout.addLayout(theme_button_layout)
        left_panel_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        left_panel_layout.addWidget(actions_label)
        left_panel_layout.addWidget(self.add_task_btn)
        left_panel_layout.addWidget(self.reports_btn)
        main_layout.addWidget(left_panel, 2)
        
        # --- Right Panel & View Stack ---
        right_panel = QFrame()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(10,10,10,10)
        self.view_stack = QStackedWidget()
        right_panel_layout.addWidget(self.view_stack)
        main_layout.addWidget(right_panel, 8)

        # --- View 1: The Column-Based Board ---
        board_view_widget = QWidget()
        board_view_layout = QVBoxLayout(board_view_widget)
        board_view_layout.setContentsMargins(0,0,0,0)
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)
        self.columns = {}
        for col_name in self.column_order + ["Done"]:
            column = self.create_column(col_name)
            column.task_dropped.connect(self.handle_task_drop)
            self.columns[col_name] = column
            columns_layout.addWidget(column)
        board_view_layout.addLayout(columns_layout)
        
        # --- View 2: The Eisenhower Matrix ---
        self.matrix_view = EisenhowerMatrix()
        self.matrix_view.task_dropped_in_quadrant.connect(self.handle_matrix_drop)
        
        self.view_stack.addWidget(board_view_widget)
        self.view_stack.addWidget(self.matrix_view)
        
        # --- Overlays & Floating Widgets ---
        self.celebration = CelebrationWidget(self)
        self.celebration.animation_finished.connect(self.start_next_task_in_flow)
        
        self.single_task_float = FloatingWidget()
        self.single_task_float.enlarge_requested.connect(self.return_to_today_list)
        self.single_task_float.task_completed.connect(self.complete_task_from_focus)
        self.single_task_float.skip_requested.connect(self.skip_to_next_task)
        self.single_task_float.pause_toggled.connect(self.pause_from_float)
        
        self.today_list_float = TodayListWidget()
        self.today_list_float.enlarge_requested.connect(self.show_main_window_from_float)
        self.today_list_float.focus_on_task_requested.connect(self.enter_mini_mode)
        
        self.celebration.hide()
        self.single_task_float.hide()
        self.today_list_float.hide()
        
        self.load_projects()

    def change_theme(self, theme_name):
        """Loads and applies a new theme stylesheet and saves the choice."""
        config = load_config()
        config['theme'] = theme_name
        save_config(config)
        stylesheet = load_stylesheet(theme_name)
        if self.parent_app:
            self.parent_app.setStyleSheet(stylesheet)

    def find_widget_by_id(self, task_id_to_find):
        """Finds a task widget in any view and returns it, its layout, and its container."""
        for view_index in range(self.view_stack.count()):
            view = self.view_stack.widget(view_index)
            if view and hasattr(view, 'columns'): # Board view
                for column in view.columns.values():
                    layout = column.tasks_layout
                    for i in range(layout.count()):
                        widget = layout.itemAt(i).widget()
                        if widget and isinstance(widget, TaskWidget) and widget.task_id == task_id_to_find:
                            return widget, layout, column
            elif isinstance(view, EisenhowerMatrix): # Matrix view
                for quadrant in [view.q1, view.q2, view.q3, view.q4]:
                    layout = quadrant.tasks_layout
                    for i in range(layout.count()):
                        widget = layout.itemAt(i).widget()
                        if widget and isinstance(widget, TaskWidget) and widget.task_id == task_id_to_find:
                            return widget, layout, quadrant
        return None, None, None

    def create_column(self, title):
        """Creates a column, adding the Blitz Now button to the Today column."""
        column = DropColumn(title)
        if title == "Today":
            header_layout = QHBoxLayout()
            original_title_widget = column.main_layout.takeAt(0).widget()
            self.blitz_now_btn = QPushButton(qta.icon('fa5s.bolt'), " Blitz Now")
            self.blitz_now_btn.setObjectName("BlitzButton")
            self.blitz_now_btn.clicked.connect(self.start_blitz_now)
            header_layout.addWidget(original_title_widget)
            header_layout.addStretch()
            header_layout.addWidget(self.blitz_now_btn)
            column.main_layout.insertLayout(0, header_layout)
        return column

    def open_project_context_menu(self, position):
        item = self.project_list_widget.itemAt(position);
        if not item: return
        project_id = item.data(Qt.ItemDataRole.UserRole)
        if project_id in [-1, 1]: return
        menu = QMenu(); rename_action = menu.addAction(qta.icon('fa5s.pencil-alt'), "Rename Project"); color_action = menu.addAction(qta.icon('fa5s.palette'), "Change Color"); delete_action = menu.addAction(qta.icon('fa5s.trash-alt'), "Delete Project")
        action = menu.exec(self.project_list_widget.mapToGlobal(position))
        if action == rename_action: self.rename_project(item)
        elif action == color_action: self.change_project_color(item)
        elif action == delete_action: self.delete_project(item)

    def rename_project(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole); current_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename Project", "New project name:", text=current_name)
        if ok and new_name and new_name != current_name: database.rename_project(project_id, new_name); self.load_projects()

    def change_project_color(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole); color = QColorDialog.getColor()
        if color.isValid(): database.update_project_color(project_id, color.name()); self.load_projects()

    def delete_project(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole); project_name = item.text()
        reply = QMessageBox.warning(self, "Delete Project", f"Are you sure you want to delete '{project_name}'?\nALL TASKS within this project will be permanently deleted.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes: database.delete_project(project_id); self.load_projects()

    def add_new_project(self):
        project_name, ok = QInputDialog.getText(self, "Add New Project", "Project Name:")
        if ok and project_name: database.add_project(project_name); self.load_projects()
        
    def load_projects(self):
        self.project_list_widget.blockSignals(True); self.project_list_widget.clear(); all_projects_item = QListWidgetItem(qta.icon('fa5s.inbox', color='#909dab'), "All Projects (Inbox)"); all_projects_item.setData(Qt.ItemDataRole.UserRole, -1)
        self.project_list_widget.addItem(all_projects_item); projects = database.get_all_projects(); current_project_id_to_restore = self.current_project_id
        for i, project in enumerate(projects):
            color = project['color'] or '#909dab'; icon = qta.icon('fa5s.circle', color=color)
            item = QListWidgetItem(icon, project['name']); item.setData(Qt.ItemDataRole.UserRole, project['id']); self.project_list_widget.addItem(item)
            if project['id'] == current_project_id_to_restore: self.project_list_widget.setCurrentItem(item)
        self.project_list_widget.blockSignals(False)
        if self.project_list_widget.count() > 0 and self.project_list_widget.currentRow() == -1: self.project_list_widget.setCurrentRow(0)
        elif self.project_list_widget.count() == 0: self.on_project_selected(None, None)
    
    def on_project_selected(self, current_item, previous_item):
        if current_item is None: self.current_project_id = None; self.refresh_all_views(); return
        project_id = current_item.data(Qt.ItemDataRole.UserRole)
        if self.current_project_id != project_id: self.current_project_id = project_id; self.refresh_all_views()

    def switch_view(self, index): self.view_stack.setCurrentIndex(index); self.refresh_all_views()
    
    def refresh_all_views(self):
        tasks_to_display = []
        if self.current_project_id == -1: tasks_to_display = database.get_all_tasks_from_all_projects(); self.add_task_btn.setEnabled(False)
        elif self.current_project_id is not None: tasks_to_display = database.get_tasks_for_project(self.current_project_id); self.add_task_btn.setEnabled(True)
        self.clear_all_columns(); self.matrix_view.clear_all_quadrants()
        for task in tasks_to_display:
            task_widget = TaskWidget(task); task_widget.task_completed.connect(self.complete_task); task_widget.task_deleted.connect(self.delete_task)
            task_widget.task_edit_requested.connect(self.open_edit_task_dialog); task_widget.focus_requested.connect(self.start_focus_mode); task_widget.task_reopened.connect(self.reopen_task)
            if task["column"] in self.columns: self.columns[task["column"]].tasks_layout.addWidget(task_widget)
        active_tasks = [t for t in tasks_to_display if t['column'] != 'Done']
        self.matrix_view.populate_matrix(active_tasks)

    def clear_all_columns(self):
        for column in self.columns.values():
            layout = column.tasks_layout;
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()

    def handle_task_drop(self, task_id_str, new_column_name, drop_row):
            """Handles drops with a 'surgical' UI update for a smooth animation."""
            task_id = int(task_id_str)
            widget_to_move, source_layout, source_container = self.find_widget_by_id(task_id)

            # If the drag started from the matrix, we must do a full refresh for stability
            if isinstance(source_container, QuadrantWidget):
                database.update_task_column(task_id, new_column_name)
                self.refresh_all_views()
                return
                
            # If the drag is within the Board view, perform the smooth move
            if widget_to_move and source_layout and source_container:
                # 1. Perform the UI move first for instant feedback
                source_layout.removeWidget(widget_to_move)
                dest_layout = self.columns[new_column_name].tasks_layout
                dest_layout.insertWidget(drop_row, widget_to_move)
                widget_to_move.column_name = new_column_name
                
                # 2. Update the database in the background
                database.update_task_column(task_id, new_column_name)
                
                # 3. Get the new order of IDs from the destination column's layout
                dest_ids = [dest_layout.itemAt(i).widget().task_id for i in range(dest_layout.count())]
                database.update_task_order(dest_ids)
                
                # 4. If the task moved between columns, update the source column's order too
                if source_container.column_name != new_column_name:
                    source_ids = [source_layout.itemAt(i).widget().task_id for i in range(source_layout.count())]
                    database.update_task_order(source_ids)
            else:
                # Fallback to a full refresh if something goes wrong
                self.refresh_all_views()

    def handle_matrix_drop(self, task_id, is_urgent, is_important):
        new_column = "Today" if is_urgent else "This Week"; new_priority = "High" if is_important else "Medium"
        database.update_task_attributes(task_id, new_column, new_priority); self.refresh_all_views()

    def enter_today_list_mode(self):
        tasks = database.get_tasks_for_project(self.current_project_id) if self.current_project_id not in [None, -1] else database.get_all_tasks_from_all_projects()
        today_tasks = [t for t in tasks if t['column'] == 'Today']
        if not today_tasks: QMessageBox.information(self, "Blitz Now", "There are no tasks in your 'Today' list to blitz!"); return
        self.today_list_float.populate_tasks(today_tasks); self.hide(); self.today_list_float.show()

    def enter_mini_mode(self, task_id):
        self.current_focus_task_id = task_id; task_data = self.get_current_focus_task_data()
        if not task_data: return
        self.today_list_float.hide(); self.single_task_float.start_session(task_data); self.single_task_float.show()

    def return_to_today_list(self):
        self.pause_from_float(True); self.single_task_float.hide(); self.enter_today_list_mode()

    def show_main_window_from_float(self):
        self.end_focus_mode(save_progress=True); self.show()

    def pause_from_float(self, is_paused):
        if is_paused and self.current_focus_task_id:
            new_minutes = self.single_task_float.save_progress(); database.update_actual_time(self.current_focus_task_id, new_minutes); self.refresh_all_views()

    def complete_task_from_focus(self):
        if self.current_focus_task_id:
            new_minutes = self.single_task_float.save_progress(); database.update_actual_time(self.current_focus_task_id, new_minutes)
            self.complete_task(self.current_focus_task_id)

    def get_current_focus_task_data(self):
        if not self.current_focus_task_id: return None
        task_data_source = database.get_tasks_for_project(self.current_project_id) if self.current_project_id != -1 else database.get_all_tasks_from_all_projects()
        return next((t for t in task_data_source if t['id'] == self.current_focus_task_id), None)
        
    def end_focus_mode(self, save_progress=True):
        if save_progress and self.current_focus_task_id: self.single_task_float.save_progress()
        self.current_focus_task_id = None; self.single_task_float.hide(); self.today_list_float.hide()
        if not self.isVisible(): self.show()
        self.refresh_all_views()

    def start_blitz_now(self): self.enter_today_list_mode()
    def start_focus_mode(self, task_id): self.current_focus_task_id = task_id; self.enter_today_list_mode()

    def skip_to_next_task(self):
        if self.current_focus_task_id:
            new_minutes = self.single_task_float.save_progress(); database.update_actual_time(self.current_focus_task_id, new_minutes)
        self.start_next_task_in_flow(from_skip=True)

    def start_next_task_in_flow(self, from_skip=False):
        task_list_source = database.get_tasks_for_project(self.current_project_id) if self.current_project_id not in [None, -1] else database.get_all_tasks_from_all_projects()
        all_today_tasks = [t for t in task_list_source if t['column'] == 'Today']
        last_task_index = -1
        for i, task in enumerate(all_today_tasks):
            if task['id'] == self.current_focus_task_id:
                last_task_index = i
                break
        next_index = last_task_index if not from_skip else last_task_index + 1
        # Fix: Only proceed if next_index is valid
        if 0 <= next_index < len(all_today_tasks):
            next_task = all_today_tasks[next_index]
            self.enter_mini_mode(next_task['id'])
        else:
            self.show_main_window_from_float()

    def reopen_task(self, task_id): database.update_task_column(task_id, "Today"); self.refresh_all_views()
    
    def complete_task(self, task_id):
        database.update_task_column(task_id, "Done"); self.celebration.show_celebration()

    def open_add_task_dialog(self):
        if self.current_project_id is None or self.current_project_id == -1: QMessageBox.warning(self, "Cannot Add Task", "Please select a specific project to add a new task."); return
        dialog = AddTaskDialog(self);
        if dialog.exec():
            task_data = dialog.get_task_data();
            if task_data["title"]: database.add_task(title=task_data["title"], notes=task_data["notes"], project_id=self.current_project_id, column="Backlog", est_time=task_data["estimated_time"], task_type=task_data["task_type"], task_priority=task_data["task_priority"]); self.refresh_all_views()
    
    def open_edit_task_dialog(self, task_id):
        task_data_source = database.get_tasks_for_project(self.current_project_id) if self.current_project_id != -1 else database.get_all_tasks_from_all_projects()
        task_data = next((t for t in task_data_source if t['id'] == task_id), None)
        if not task_data: return
        dialog = EditTaskDialog(task_data, self)
        if dialog.exec():
            updated_data = dialog.get_updated_data()
            if updated_data["title"]: database.update_task_details(task_id, updated_data["title"], updated_data["notes"], updated_data["estimated_time"], updated_data["task_type"], updated_data["task_priority"]); self.refresh_all_views()
    
    def open_reporting_dialog(self):
        all_tasks_stats = database.get_report_stats(); dialog = ReportingDialog(all_tasks_stats, self); dialog.exec()
    
    def delete_task(self, task_id):
        reply = QMessageBox.question(self, 'Delete Task', "Are you sure you want to delete this task?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes: database.delete_task(task_id); self.refresh_all_views()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.celebration.setGeometry(self.rect())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- NEW: LOAD CUSTOM FONT ---
    font_dir = "assets/fonts"
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if font_file.endswith(".ttf"):
                QFontDatabase.addApplicationFont(os.path.join(font_dir, font_file))

    # --- THEME LOADING LOGIC ---
    # database.migrate_database() 
    app.setWindowIcon(QIcon("assets/icon.png"))
    config = load_config()
    stylesheet = load_stylesheet(config.get("theme", "dark"))
    if stylesheet:
        app.setStyleSheet(stylesheet)
        
    window = BlitzitApp(app)
    window.show()
    sys.exit(app.exec())