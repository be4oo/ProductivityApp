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
    cursor.execute("PRAGMA table_info(tasks)"); columns = [row['name'] for row in cursor.fetchall()]
    if 'completed_at' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP")
    cursor.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, color TEXT)")
    # *** NEW: Add color column to projects table if it doesn't exist ***
    cursor.execute("PRAGMA table_info(projects)")
    project_columns = [row['name'] for row in cursor.fetchall()]
    if 'color' not in project_columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN color TEXT")
        print("- 'color' column added to 'projects' table.")

    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO projects (name, color) VALUES (?, ?)", ("Inbox", "#909dab"))
        print("- Default 'Inbox' project created.")
    if 'project_id' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id)")
    cursor.execute("UPDATE tasks SET project_id = 1 WHERE project_id IS NULL")
    if 'task_type' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN task_type TEXT")
    if 'task_priority' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN task_priority TEXT")

    if 'due_date' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP")
    if 'reminder_enabled' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN reminder_enabled BOOLEAN DEFAULT 0")
    if 'reminder_offset' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN reminder_offset INTEGER DEFAULT 0")


    conn.commit(); conn.close(); print("All migrations checked.")

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

    conn = get_db_connection()
    tasks = [dict(row) for row in conn.execute('SELECT * FROM tasks WHERE project_id = ? AND status != "archived" ORDER BY priority ASC', (project_id,)).fetchall()]
    conn.close()
    return tasks
def get_all_tasks_from_all_projects():
    conn = get_db_connection()
    tasks = [dict(row) for row in conn.execute('SELECT * FROM tasks WHERE status != "archived" ORDER BY project_id, priority ASC').fetchall()]
    conn.close()
    return tasks
def add_task(title, notes, project_id, column, est_time, task_type, task_priority, due_date=None, reminder_enabled=False, reminder_offset=0):
    conn = get_db_connection(); max_priority = conn.execute('SELECT MAX(priority) FROM tasks WHERE column = ? AND project_id = ?', (column, project_id)).fetchone()[0] or 0
    conn.execute('INSERT INTO tasks (title, notes, project_id, column, estimated_time, task_type, task_priority, priority, due_date, reminder_enabled, reminder_offset) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (title, notes, project_id, column, est_time, task_type, task_priority, max_priority + 1, due_date, reminder_enabled, reminder_offset)); conn.commit(); conn.close()
def update_task_details(task_id, title, notes, est_time, task_type, task_priority, due_date=None, reminder_enabled=False, reminder_offset=0):
    conn = get_db_connection(); conn.execute('UPDATE tasks SET title = ?, notes = ?, estimated_time = ?, task_type = ?, task_priority = ?, due_date = ?, reminder_enabled = ?, reminder_offset = ? WHERE id = ?',
                 (title, notes, est_time, task_type, task_priority, due_date, reminder_enabled, reminder_offset, task_id)); conn.commit(); conn.close()

    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND status != "archived" ORDER BY priority ASC', (project_id,)).fetchall(); conn.close(); return tasks
def get_all_tasks_from_all_projects():
    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE status != "archived" ORDER BY project_id, priority ASC').fetchall(); conn.close(); return tasks
def add_task(title, notes, project_id, column, est_time, task_type, task_priority):
    conn = get_db_connection(); max_priority = conn.execute('SELECT MAX(priority) FROM tasks WHERE column = ? AND project_id = ?', (column, project_id)).fetchone()[0] or 0
    conn.execute('INSERT INTO tasks (title, notes, project_id, column, estimated_time, task_type, task_priority, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (title, notes, project_id, column, est_time, task_type, task_priority, max_priority + 1)); conn.commit(); conn.close()
def update_task_details(task_id, title, notes, est_time, task_type, task_priority):
    conn = get_db_connection(); conn.execute('UPDATE tasks SET title = ?, notes = ?, estimated_time = ?, task_type = ?, task_priority = ? WHERE id = ?',
                 (title, notes, est_time, task_type, task_priority, task_id)); conn.commit(); conn.close()

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