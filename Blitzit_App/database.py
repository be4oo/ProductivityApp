# Blitzit_App/database.py
import sqlite3
from datetime import datetime
import random

DB_PATH = 'data/tasks.db'

# Predefined list of nice colors for new projects
PROJECT_COLORS = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFA1", "#FFC300", "#C70039"]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES); conn.row_factory = sqlite3.Row; return conn

def migrate_database():
    conn = get_db_connection(); cursor = conn.cursor(); print("Running all database migrations...")

    # Create projects table IF NOT EXISTS first, as tasks references it.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT
        )
    """)
    print("- Ensured 'projects' table exists.")

    # Create tasks table IF NOT EXISTS including all known columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT,
            project_id INTEGER REFERENCES projects(id) DEFAULT 1, /* Default to Inbox or a general project */
            column TEXT DEFAULT 'Backlog',
            status TEXT, /* e.g., 'pending', 'in-progress', 'completed', 'archived' - current schema seems to use 'column' for this mostly */
            priority INTEGER DEFAULT 0, /* For ordering within a column */
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            estimated_time INTEGER, /* in minutes */
            actual_time INTEGER DEFAULT 0, /* in minutes */
            completed_at TIMESTAMP,
            task_type TEXT,
            task_priority TEXT, /* e.g., Low, Medium, High */
            reminder_at TIMESTAMP
        )
    """)
    print("- Ensured 'tasks' table exists with all columns.")

    # Now, proceed with ALTER TABLE for any columns that might have been added in later migrations
    # This makes the migration more robust if running against an older DB schema.

    # For 'projects' table:
    cursor.execute("PRAGMA table_info(projects)")
    project_columns = [row['name'] for row in cursor.fetchall()]
    if 'color' not in project_columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN color TEXT")
        print("- 'color' column added to 'projects' table.")

    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO projects (name, color) VALUES (?, ?)", ("Inbox", "#909dab"))
        print("- Default 'Inbox' project created.")

    # For 'tasks' table, check and add columns if they don't exist (for older DBs)
    # The CREATE TABLE above should handle new DBs.
    cursor.execute("PRAGMA table_info(tasks)")
    task_columns = [row['name'] for row in cursor.fetchall()]

    if 'project_id' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id)")
        cursor.execute("UPDATE tasks SET project_id = 1 WHERE project_id IS NULL") # Default existing tasks to project 1
        print("- 'project_id' column added to 'tasks' and defaulted.")
    if 'completed_at' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP")
        print("- 'completed_at' column added to 'tasks'.")
    if 'task_type' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN task_type TEXT")
        print("- 'task_type' column added to 'tasks'.")
    if 'task_priority' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN task_priority TEXT")
        print("- 'task_priority' column added to 'tasks'.")
    if 'reminder_at' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN reminder_at TIMESTAMP")
        print("- 'reminder_at' column added to 'tasks'.")
    # Add any other column checks here if introduced in the future.

    conn.commit(); conn.close(); print("All migrations checked and database schema is up-to-date.")

# --- PROJECT MANAGEMENT FUNCTIONS ---
def get_all_projects():
    conn = get_db_connection(); projects = conn.execute('SELECT * FROM projects ORDER BY id ASC').fetchall(); conn.close()
    return projects

def add_project(name):
    conn = get_db_connection()
    try:
        color = random.choice(PROJECT_COLORS)
        conn.execute("INSERT INTO projects (name, color) VALUES (?, ?)", (name, color)); conn.commit()
    except sqlite3.IntegrityError: print(f"Project '{name}' already exists.")
    finally: conn.close()

def rename_project(project_id, new_name):
    conn = get_db_connection()
    conn.execute("UPDATE projects SET name = ? WHERE id = ?", (new_name, project_id))
    conn.commit(); conn.close()
    
def update_project_color(project_id, new_color):
    conn = get_db_connection()
    conn.execute("UPDATE projects SET color = ? WHERE id = ?", (new_color, project_id))
    conn.commit(); conn.close()

def delete_project(project_id):
    """Deletes a project AND all associated tasks."""
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.close()


# --- TASK FUNCTIONS (unchanged) ---
def get_tasks_for_project(project_id):
    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND IFNULL(status, "") != "archived" ORDER BY priority ASC', (project_id,)).fetchall(); conn.close(); return tasks
def get_all_tasks_from_all_projects():
    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE IFNULL(status, "") != "archived" ORDER BY project_id, priority ASC').fetchall(); conn.close(); return tasks
def add_task(title, notes, project_id, column, est_time, task_type, task_priority, reminder_at=None, status='pending'): # Added default status
    conn = get_db_connection(); max_priority = conn.execute('SELECT MAX(priority) FROM tasks WHERE column = ? AND project_id = ?', (column, project_id)).fetchone()[0] or 0
    conn.execute('INSERT INTO tasks (title, notes, project_id, column, status, estimated_time, task_type, task_priority, priority, reminder_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (title, notes, project_id, column, status, est_time, task_type, task_priority, max_priority + 1, reminder_at)); conn.commit(); conn.close()
def update_task_details(task_id, title, notes, est_time, task_type, task_priority, reminder_at=None):
    # This function seems to be duplicated, the second one is more correct. I will remove the first one.
    conn = get_db_connection(); conn.execute('UPDATE tasks SET title = ?, notes = ?, estimated_time = ?, task_type = ?, task_priority = ?, reminder_at = ? WHERE id = ?',
                 (title, notes, est_time, task_type, task_priority, reminder_at, task_id)); conn.commit(); conn.close()
def update_task_column(task_id, new_column):
    conn = get_db_connection()
    if new_column == "Done": conn.execute('UPDATE tasks SET column = ?, completed_at = ? WHERE id = ?', (new_column, datetime.now(), task_id))
    else: conn.execute('UPDATE tasks SET column = ?, completed_at = NULL, priority = 999 WHERE id = ?', (new_column, task_id))
    conn.commit(); conn.close()
def update_task_order(ordered_task_ids):
    conn = get_db_connection()
    with conn:
        for index, task_id in enumerate(ordered_task_ids): conn.execute('UPDATE tasks SET priority = ? WHERE id = ?', (index, task_id))
    conn.close()
def update_task_attributes(task_id, new_column, new_priority):
    conn = get_db_connection(); conn.execute("UPDATE tasks SET column = ?, task_priority = ? WHERE id = ?", (new_column, new_priority, task_id)); conn.commit(); conn.close()
def update_actual_time(task_id, actual_minutes):
    conn = get_db_connection(); conn.execute('UPDATE tasks SET actual_time = ? WHERE id = ?', (actual_minutes, task_id)); conn.commit(); conn.close()
def delete_task(task_id):
    conn = get_db_connection(); conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,)); conn.commit(); conn.close()
def get_report_stats():
    conn = get_db_connection(); total_done = conn.execute('SELECT COUNT(*) FROM tasks WHERE column = "Done"').fetchone()[0]
    total_pending = conn.execute('SELECT COUNT(*) FROM tasks WHERE column != "Done"').fetchone()[0]
    completions_last_7_days = conn.execute("SELECT date(completed_at) as completion_day, COUNT(*) as count FROM tasks WHERE completed_at >= date('now', '-7 days') GROUP BY completion_day").fetchall()
    conn.close(); return {"total_done": total_done, "total_pending": total_pending, "completion_trend": completions_last_7_days}