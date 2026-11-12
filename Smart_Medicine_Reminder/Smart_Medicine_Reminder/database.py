import sqlite3
from datetime import date, datetime

DB_NAME = "medicine_reminder.db"

def connect():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                medicine_time TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dose_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                scheduled_for TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Taken',
                recorded_at TEXT NOT NULL,
                UNIQUE(medicine_id, scheduled_for),
                FOREIGN KEY(medicine_id) REFERENCES medicines(id)
            )
        """)

def add_medicine(name, dosage, medicine_time, start_date, end_date, notes=""):
    with connect() as conn:
        conn.execute("""
            INSERT INTO medicines
            (name, dosage, medicine_time, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, dosage, medicine_time, start_date, end_date, notes))

def get_medicines():
    with connect() as conn:
        return conn.execute("""
            SELECT id, name, dosage, medicine_time, start_date, end_date, notes, active
            FROM medicines
            ORDER BY medicine_time
        """).fetchall()

def get_today_medicines():
    today = date.today().isoformat()
    with connect() as conn:
        return conn.execute("""
            SELECT id, name, dosage, medicine_time, start_date, end_date, notes
            FROM medicines
            WHERE active = 1 AND start_date <= ? AND end_date >= ?
            ORDER BY medicine_time
        """, (today, today)).fetchall()

def get_due_medicines(current_time):
    today = date.today().isoformat()
    with connect() as conn:
        return conn.execute("""
            SELECT id, name, dosage, medicine_time
            FROM medicines
            WHERE active = 1
              AND start_date <= ? AND end_date >= ?
              AND medicine_time <= ?
        """, (today, today, current_time)).fetchall()

def log_dose(medicine_id, scheduled_for, status):
    with connect() as conn:
        conn.execute("""
            INSERT INTO dose_log (medicine_id, scheduled_for, status, recorded_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(medicine_id, scheduled_for)
            DO UPDATE SET status = excluded.status, recorded_at = excluded.recorded_at
        """, (medicine_id, scheduled_for, status, datetime.now().isoformat(timespec="seconds")))

def get_today_logs():
    today = date.today().isoformat()
    with connect() as conn:
        return conn.execute("""
            SELECT m.name, m.dosage, l.scheduled_for, l.status, l.recorded_at
            FROM dose_log l
            JOIN medicines m ON m.id = l.medicine_id
            WHERE date(l.scheduled_for) = ?
            ORDER BY l.scheduled_for DESC
        """, (today,)).fetchall()

def deactivate_medicine(medicine_id):
    with connect() as conn:
        conn.execute("UPDATE medicines SET active = 0 WHERE id = ?", (medicine_id,))

def delete_medicine(medicine_id):
    with connect() as conn:
        conn.execute("DELETE FROM dose_log WHERE medicine_id = ?", (medicine_id,))
        conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
