# Blitzit_App/database.py
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = 'data/tasks.db'

# Predefined list of nice colors for new projects
PROJECT_COLORS = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFA1", "#FFC300", "#C70039"]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES); conn.row_factory = sqlite3.Row; return conn

def migrate_database():
    conn = get_db_connection(); cursor = conn.cursor(); print("Running all database migrations...")
    cursor.execute("PRAGMA table_info(tasks)"); columns = [row['name'] for row in cursor.fetchall()]
    if 'completed_at' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP")
    if 'due_date' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")

    if 'recurrence' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT")

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
    cursor.execute("UPDATE tasks SET project_id = 1 WHERE project_id IS NULL") # Default to Inbox if project_id is NULL
    if 'task_type' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN task_type TEXT")
    if 'task_priority' not in columns: cursor.execute("ALTER TABLE tasks ADD COLUMN task_priority TEXT")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'pending'")
        print("- 'status' column added to 'tasks' table.")
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
    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND status != "archived" ORDER BY priority ASC', (project_id,)).fetchall(); conn.close(); return tasks
def get_all_tasks_from_all_projects():
    conn = get_db_connection(); tasks = conn.execute('SELECT * FROM tasks WHERE status != "archived" ORDER BY project_id, priority ASC').fetchall(); conn.close(); return tasks
def add_task(title, notes, project_id, column, est_time, task_type, task_priority, due_date=None, recurrence=None):
    conn = get_db_connection()
    max_priority = conn.execute('SELECT MAX(priority) FROM tasks WHERE column = ? AND project_id = ?', (column, project_id)).fetchone()[0] or 0
    conn.execute('INSERT INTO tasks (title, notes, project_id, column, estimated_time, task_type, task_priority, priority, due_date, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (title, notes, project_id, column, est_time, task_type, task_priority, max_priority + 1, due_date, recurrence))
    conn.commit(); conn.close()
def update_task_details(task_id, title, notes, est_time, task_type, task_priority, due_date=None, recurrence=None):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET title = ?, notes = ?, estimated_time = ?, task_type = ?, task_priority = ?, due_date = ? WHERE id = ?',
                 (title, notes, est_time, task_type, task_priority, due_date, task_id))
    conn.commit(); conn.close()
def update_task_column(task_id, new_column):

    conn = get_db_connection()
    conn.execute('UPDATE tasks SET title = ?, notes = ?, estimated_time = ?, task_type = ?, task_priority = ?, due_date = ?, recurrence = ? WHERE id = ?',
                 (title, notes, est_time, task_type, task_priority, due_date, recurrence, task_id))
    conn.commit(); conn.close()
def update_task_column(task_id, new_column):
    conn = get_db_connection()
    if new_column == "Done":
        cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.execute('UPDATE tasks SET column = ?, completed_at = ? WHERE id = ?', (new_column, datetime.now(), task_id))
        conn.commit()
        if task and task['recurrence']:
            next_due = None
            if task['due_date']:
                try:
                    dt = datetime.fromisoformat(task['due_date'])
                except ValueError:
                    dt = None
                if dt:
                    if task['recurrence'] == 'Daily':
                        next_due = (dt + timedelta(days=1)).isoformat()
                    elif task['recurrence'] == 'Weekly':
                        next_due = (dt + timedelta(weeks=1)).isoformat()
                    elif task['recurrence'] == 'Monthly':
                        next_due = (dt + timedelta(days=30)).isoformat()
            add_task(task['title'], task['notes'], task['project_id'], 'Backlog', task['estimated_time'], task['task_type'], task['task_priority'], next_due, task['recurrence'])
    else:
        conn.execute('UPDATE tasks SET column = ?, completed_at = NULL, priority = 999 WHERE id = ?', (new_column, task_id))
        conn.commit()
    conn.close()
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

# --- ARCHIVE FUNCTIONS ---
def archive_task(task_id):
    conn = get_db_connection()
    # When archiving, we can set column to NULL or a specific 'Archived' logical column if preferred for unarchiving later.
    # Setting priority to 0 or NULL as it's not relevant for archived tasks in the same way.
    conn.execute('UPDATE tasks SET status = "archived", column = NULL, priority = 0 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def unarchive_task(task_id, target_column="Backlog"):
    conn = get_db_connection()
    # Get max priority for the target column to place the unarchived task at the end.
    # Note: This assumes the target_column is valid for the project the task belongs to.
    # A more robust solution might need project_id if tasks can be unarchived to different projects or if columns are project-specific.
    # For now, we assume unarchiving to a general column like "Backlog" within its original project.
    task_project_id = conn.execute('SELECT project_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task_project_id:
        project_id = task_project_id['project_id']
        max_priority_row = conn.execute('SELECT MAX(priority) FROM tasks WHERE column = ? AND project_id = ? AND status != "archived"', (target_column, project_id)).fetchone()
        max_priority = max_priority_row[0] if max_priority_row and max_priority_row[0] is not None else 0

        conn.execute('UPDATE tasks SET status = "pending", column = ?, priority = ?, completed_at = NULL WHERE id = ?',
                     (target_column, max_priority + 1, task_id))
        conn.commit()
    conn.close()

def get_archived_tasks_for_project(project_id):
    conn = get_db_connection()
    # Order by completion time or archival time if we add an archived_at timestamp
    tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND status = "archived" ORDER BY completed_at DESC, id DESC', (project_id,)).fetchall()
    conn.close()
    return tasks

def get_all_archived_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE status = "archived" ORDER BY project_id, completed_at DESC, id DESC').fetchall()
    conn.close()
    return tasks