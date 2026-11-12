from datetime import datetime
from database import add_medicine, get_today_medicines, log_dose

def create_medicine(name, dosage, medicine_time, start_date, end_date, notes=""):
    name = name.strip()
    dosage = dosage.strip()
    notes = notes.strip()

    if not name:
        raise ValueError("Enter a medicine name.")
    if not dosage:
        raise ValueError("Enter the dosage, for example 1 tablet.")
    try:
        datetime.strptime(medicine_time, "%H:%M")
    except ValueError:
        raise ValueError("Enter time in 24-hour HH:MM format, for example 08:30.")
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Enter dates in YYYY-MM-DD format.")
    if end < start:
        raise ValueError("End date cannot be earlier than start date.")

    add_medicine(name, dosage, medicine_time, start_date, end_date, notes)

def mark_dose(medicine_id, scheduled_date, medicine_time, status):
    scheduled_for = f"{scheduled_date} {medicine_time}"
    log_dose(medicine_id, scheduled_for, status)

def todays_schedule():
    return get_today_medicines()
