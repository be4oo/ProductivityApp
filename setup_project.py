import os
import sqlite3

# --- 1. Create Project Directory Structure ---
print("Creating project structure...")
if not os.path.exists("Blitzit_App"):
    os.makedirs("Blitzit_App/assets/icons")
    os.makedirs("Blitzit_App/data")
    os.makedirs("Blitzit_App/ui")
    os.makedirs("Blitzit_App/modules")
print("Project structure created successfully.")

# --- 2. Create the SQLite Database and `tasks` Table ---
db_path = "Blitzit_App/data/tasks.db"
print(f"Setting up database at '{db_path}'...")
try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT,
            list TEXT DEFAULT 'Inbox',
            column TEXT DEFAULT 'Today',
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 0,
            due_date TEXT,
            estimated_time INTEGER, -- in minutes
            actual_time INTEGER DEFAULT 0, -- in minutes
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(parent_id) REFERENCES tasks(id)
        )
    ''')
    con.commit()
    con.close()
    print("Database 'tasks.db' created successfully with 'tasks' and 'subtasks' tables.")
except Exception as e:
    print(f"Error creating database: {e}")

# --- 3. Create the Main Application Python Script ---
main_app_code = """
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt

class BlitzitApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blitzit - Your Productivity Hub")
        self.setGeometry(100, 100, 1200, 800)

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Left Panel (Lists & Navigation) ---
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.addWidget(QLabel("Your Lists"))
        # Placeholder for lists
        left_panel_layout.addStretch()
        main_layout.addWidget(left_panel, 1) # Takes 1/4 of the space

        # --- Right Panel (Task Columns) ---
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel_layout = QVBoxLayout(right_panel)

        # Top Bar
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addWidget(QLabel("Today's Focus"))
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(QPushButton("Start Blitz Mode"))
        right_panel_layout.addLayout(top_bar_layout)

        # Task Columns
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(self.create_column("Backlog"))
        columns_layout.addWidget(self.create_column("This Week"))
        columns_layout.addWidget(self.create_column("Today"))
        right_panel_layout.addLayout(columns_layout)

        main_layout.addWidget(right_panel, 3) # Takes 3/4 of the space

    def create_column(self, title):
        column = QFrame()
        column.setFrameShape(QFrame.Shape.StyledPanel)
        column_layout = QVBoxLayout(column)
        column_layout.addWidget(QLabel(title))
        # Placeholder for tasks
        column_layout.addStretch()
        return column

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlitzitApp()
    window.show()
    sys.exit(app.exec())
"""

main_app_path = "Blitzit_App/main.py"
print(f"Creating main application file at '{main_app_path}'...")
with open(main_app_path, "w") as f:
    f.write(main_app_code)
print("Main application file created successfully.")

print("\n--- Phase 1 Complete ---")
print("To run your new application:")
print("1. Make sure you have PyQt6 installed: pip install PyQt6")
print(f"2. Navigate to the Blitzit_App directory: cd Blitzit_App")
print("3. Run the main script: python main.py")