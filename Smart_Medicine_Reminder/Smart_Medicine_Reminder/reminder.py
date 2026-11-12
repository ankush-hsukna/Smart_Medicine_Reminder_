from datetime import date, datetime
from tkinter import messagebox
from database import get_due_medicines, log_dose

class ReminderManager:
    """
    Checks due medicines while the app is open.
    Each scheduled dose is prompted once per application session.
    """
    def __init__(self, root, on_update, interval_seconds=20):
        self.root = root
        self.on_update = on_update
        self.interval_ms = interval_seconds * 1000
        self.running = False
        self.after_id = None
        self.prompted = set()

    def start(self):
        if not self.running:
            self.running = True
            self.check_due()

    def stop(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def check_due(self):
        if not self.running:
            return

        now = datetime.now()
        today = date.today().isoformat()
        current_time = now.strftime("%H:%M")

        for medicine_id, name, dosage, medicine_time in get_due_medicines(current_time):
            scheduled_key = (medicine_id, today, medicine_time)
            if scheduled_key in self.prompted:
                continue

            self.prompted.add(scheduled_key)
            answer = messagebox.askyesno(
                "Medicine Reminder",
                f"It's time for your scheduled medicine:\n\n"
                f"Medicine: {name}\nDosage: {dosage}\nTime: {medicine_time}\n\n"
                "Have you taken this dose?"
            )
            status = "Taken" if answer else "Not confirmed"
            log_dose(medicine_id, f"{today} {medicine_time}", status)
            self.on_update()

        self.after_id = self.root.after(self.interval_ms, self.check_due)
