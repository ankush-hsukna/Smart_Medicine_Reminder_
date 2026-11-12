import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from database import (
    initialize_database, get_medicines, get_today_medicines,
    get_today_logs, deactivate_medicine, delete_medicine
)
from medicine import create_medicine, mark_dose
from reminder import ReminderManager

BG = "#F3F7FB"
NAVY = "#17324D"
BLUE = "#2678B8"
GREEN = "#16845B"

class MedicineReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Medicine Reminder System")
        self.root.geometry("1000x700")
        self.root.minsize(820, 600)
        self.root.configure(bg=BG)

        self.reminders = ReminderManager(root, self.refresh)
        self._styles()
        self._build()
        self.refresh()
        self.reminders.start()

    def _styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TButton", font=("Segoe UI", 9), padding=7)
        style.configure("TEntry", padding=6)

    def _build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="💊  Smart Medicine Reminder",
                 font=("Segoe UI", 21, "bold"), bg=NAVY, fg="white").pack(anchor="w")
        tk.Label(header, text="Organize your medication schedule and keep track of doses.",
                 font=("Segoe UI", 10), bg=NAVY, fg="#D7E8F6").pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self.root, bg=BG, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        top = tk.Frame(body, bg=BG)
        top.pack(fill="x", pady=(0, 12))

        self.count_card = self._card(top, "MEDICINES SCHEDULED TODAY", "0", BLUE)
        self.log_card = self._card(top, "DOSES RECORDED TODAY", "0", GREEN)
        self.date_card = self._card(top, "TODAY", date.today().strftime("%d %b %Y"), NAVY)

        form = tk.LabelFrame(body, text=" Add a medicine ", bg="white", fg=NAVY,
                             font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", pady=(0, 12))

        self.name_var = tk.StringVar()
        self.dosage_var = tk.StringVar()
        self.time_var = tk.StringVar(value="08:00")
        self.start_var = tk.StringVar(value=date.today().isoformat())
        self.end_var = tk.StringVar(value=date.today().isoformat())
        self.notes_var = tk.StringVar()

        fields = [
            ("Medicine name", self.name_var, 20),
            ("Dosage (e.g. 1 tablet)", self.dosage_var, 20),
            ("Time (HH:MM)", self.time_var, 12),
            ("Start date (YYYY-MM-DD)", self.start_var, 16),
            ("End date (YYYY-MM-DD)", self.end_var, 16),
            ("Notes (optional)", self.notes_var, 20),
        ]
        grid = tk.Frame(form, bg="white")
        grid.pack(fill="x")
        for index, (label, variable, width) in enumerate(fields):
            row, col = divmod(index, 3)
            cell = tk.Frame(grid, bg="white")
            cell.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
            tk.Label(cell, text=label, bg="white", fg="#536779",
                     font=("Segoe UI", 8)).pack(anchor="w")
            ttk.Entry(cell, textvariable=variable, width=width).pack(fill="x", pady=(3, 0))
        for col in range(3):
            grid.columnconfigure(col, weight=1)

        ttk.Button(form, text="＋ Add medicine", command=self.add_medicine).pack(anchor="e", padx=5, pady=(6, 0))

        schedule_box = tk.LabelFrame(body, text=" Today's medicine schedule ",
                                     bg="white", fg=NAVY, font=("Segoe UI", 10, "bold"),
                                     padx=10, pady=8)
        schedule_box.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("name", "dosage", "time", "period", "notes")
        self.schedule = ttk.Treeview(schedule_box, columns=columns, show="headings", height=7)
        headings = {"name": "MEDICINE", "dosage": "DOSAGE", "time": "TIME",
                    "period": "SCHEDULE", "notes": "NOTES"}
        widths = {"name": 170, "dosage": 130, "time": 90, "period": 160, "notes": 200}
        for col in columns:
            self.schedule.heading(col, text=headings[col])
            self.schedule.column(col, width=widths[col], anchor="w")
        self.schedule.pack(fill="both", expand=True)

        actions = tk.Frame(schedule_box, bg="white")
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Mark selected dose as taken",
                   command=self.mark_selected).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Deactivate selected",
                   command=self.deactivate_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Delete selected",
                   command=self.delete_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Refresh",
                   command=self.refresh).pack(side="right")

        log_box = tk.LabelFrame(body, text=" Today's dose history ",
                                bg="white", fg=NAVY, font=("Segoe UI", 10, "bold"),
                                padx=10, pady=8)
        log_box.pack(fill="both", expand=True)
        log_columns = ("medicine", "dosage", "scheduled", "status")
        self.logs = ttk.Treeview(log_box, columns=log_columns, show="headings", height=4)
        log_headings = {"medicine": "MEDICINE", "dosage": "DOSAGE",
                        "scheduled": "SCHEDULED FOR", "status": "STATUS"}
        for col in log_columns:
            self.logs.heading(col, text=log_headings[col])
            self.logs.column(col, width=180, anchor="w")
        self.logs.pack(fill="both", expand=True)

        tk.Label(self.root,
                 text="Reminder checks run while this application is open. Follow your clinician's instructions.",
                 bg=BG, fg="#718395", font=("Segoe UI", 8)).pack(pady=(0, 8))

    def _card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg="white", padx=14, pady=10,
                         highlightbackground="#DCE6EF", highlightthickness=1)
        frame.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(frame, text=title, bg="white", fg="#718395",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        label = tk.Label(frame, text=value, bg="white", fg=color,
                         font=("Segoe UI", 17, "bold"))
        label.pack(anchor="w", pady=(4, 0))
        return label

    def add_medicine(self):
        try:
            create_medicine(
                self.name_var.get(), self.dosage_var.get(), self.time_var.get(),
                self.start_var.get(), self.end_var.get(), self.notes_var.get()
            )
            self.name_var.set("")
            self.dosage_var.set("")
            self.notes_var.set("")
            self.refresh()
            messagebox.showinfo("Medicine added", "Medicine schedule saved successfully.")
        except (ValueError, Exception) as error:
            messagebox.showerror("Could not add medicine", str(error))

    def selected_medicine_id(self):
        selection = self.schedule.selection()
        if not selection:
            messagebox.showwarning("Select a medicine", "Please select a medicine from today's schedule.")
            return None
        return int(selection[0])

    def mark_selected(self):
        medicine_id = self.selected_medicine_id()
        if medicine_id is None:
            return
        selected = self.schedule.item(str(medicine_id), "values")
        if not selected:
            return
        name, dosage, medicine_time, period, notes = selected
        mark_dose(medicine_id, date.today().isoformat(), medicine_time, "Taken")
        self.refresh()
        messagebox.showinfo("Dose recorded", f"{name} ({dosage}) marked as taken.")

    def deactivate_selected(self):
        medicine_id = self.selected_medicine_id()
        if medicine_id is None:
            return
        if messagebox.askyesno("Deactivate medicine", "Stop showing this medicine in the active schedule?"):
            deactivate_medicine(medicine_id)
            self.refresh()

    def delete_selected(self):
        medicine_id = self.selected_medicine_id()
        if medicine_id is None:
            return
        if messagebox.askyesno("Delete medicine", "Permanently delete this medicine and its dose history?"):
            delete_medicine(medicine_id)
            self.refresh()

    def refresh(self):
        today_meds = get_today_medicines()
        today_logs = get_today_logs()
        self.count_card.config(text=str(len(today_meds)))
        self.log_card.config(text=str(len(today_logs)))
        self.date_card.config(text=date.today().strftime("%d %b %Y"))

        for item in self.schedule.get_children():
            self.schedule.delete(item)
        for medicine_id, name, dosage, medicine_time, start, end, notes in today_meds:
            self.schedule.insert("", "end", iid=str(medicine_id),
                                 values=(name, dosage, medicine_time,
                                         f"{start} to {end}", notes))

        for item in self.logs.get_children():
            self.logs.delete(item)
        for name, dosage, scheduled, status, recorded_at in today_logs:
            self.logs.insert("", "end", values=(name, dosage, scheduled, status))

    def close(self):
        self.reminders.stop()
        self.root.destroy()

if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = MedicineReminderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
