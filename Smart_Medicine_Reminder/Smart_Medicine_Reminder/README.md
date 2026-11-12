# Smart Medicine Reminder System

A Python desktop mini-project that stores medicine schedules, checks due times while the app is open, displays reminder pop-ups, and records dose status.

## Features
- Add medicine name, dosage, time, start date, end date and notes.
- View medicines scheduled for today.
- Receive an in-app reminder when a scheduled time arrives.
- Mark a dose as taken.
- View today's dose history.
- Deactivate or delete a medicine.
- Store schedules and dose logs locally in SQLite.

## Requirements
- Python 3.9+
- Tkinter (usually included with Python on Windows)
- SQLite (included with Python)

No third-party Python packages are required.

## Run on Windows
1. Extract the ZIP file.
2. Open Command Prompt in the extracted project folder.
3. Run:

   ```bash
   py --version
   py main.py
   ```

   If `py` is unavailable, try `python main.py`.

The database `medicine_reminder.db` is created automatically.

## Entering dates and times
- Time uses 24-hour format, e.g. `08:30` or `20:00`.
- Dates use `YYYY-MM-DD`, e.g. `2026-11-01`.
- Start and end dates include the days on which the schedule is active.

## Important limitations
- The app must remain open for reminders to appear.
- Each scheduled medicine time is prompted once per app session.
- This is a student demonstration tool, not a medical device. It does not recommend medicines or doses. Enter schedules exactly as directed by a qualified healthcare professional.
- A reminder response of "Not confirmed" means the app did not receive confirmation; it does not establish whether a dose was actually missed.
