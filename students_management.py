
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_FILE = Path(__file__).resolve().parent / "students.db"
print("Database location:", DB_FILE)


def get_db_connection():
    return sqlite3.connect(str(DB_FILE), timeout=15)


def connect_db():
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    course TEXT NOT NULL
                )
            """)
    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not initialize database:\n{error}"
        )
        root.destroy()


# ==========================================
# FORM FUNCTIONS
# ==========================================

def clear_fields():
    selected_id.set("")

    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)

    for item in student_table.selection():
        student_table.selection_remove(item)

    name_entry.focus_set()


def get_form_data():
    name = name_entry.get().strip()
    age_text = age_entry.get().strip()
    course = course_entry.get().strip()

    if not name or not age_text or not course:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return None

    try:
        age = int(age_text)

        if age <= 0:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Invalid Age",
            "Please enter a positive whole number for age."
        )
        age_entry.focus_set()
        return None

    return name, age, course


# ==========================================
# LOAD STUDENTS
# ==========================================

def load_students():
    try:
        with get_db_connection() as conn:
            rows = conn.execute("""
                SELECT id, name, age, course
                FROM students
                ORDER BY id
            """).fetchall()

        for item in student_table.get_children():
            student_table.delete(item)

        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"

            student_table.insert(
                "",
                tk.END,
                values=row,
                tags=(tag,)
            )

        clear_fields()
        status_var.set(f"Total students: {len(rows)}")

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not load student records:\n{error}"
        )


# ==========================================
# ADD STUDENT
# ==========================================

def add_student():
    data = get_form_data()

    if data is None:
        return

    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO students (name, age, course)
                VALUES (?, ?, ?)
            """, data)

        load_students()

        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not add student:\n{error}"
        )


# ==========================================
# SELECT STUDENT
# ==========================================

def select_student(event=None):
    selected = student_table.selection()

    if not selected:
        return

    values = student_table.item(selected[0], "values")

    if not values:
        return

    selected_id.set(str(values[0]))

    name_entry.delete(0, tk.END)
    name_entry.insert(0, values[1])

    age_entry.delete(0, tk.END)
    age_entry.insert(0, values[2])

    course_entry.delete(0, tk.END)
    course_entry.insert(0, values[3])


# ==========================================
# UPDATE STUDENT
# ==========================================

def update_student():
    if not selected_id.get():
        messagebox.showwarning(
            "No Selection",
            "Select a student from the table before updating."
        )
        return

    data = get_form_data()

    if data is None:
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                UPDATE students
                SET name = ?, age = ?, course = ?
                WHERE id = ?
            """, (*data, int(selected_id.get())))

            updated = cursor.rowcount

        if updated == 0:
            messagebox.showwarning(
                "Not Found",
                "The selected student no longer exists."
            )
            load_students()
            return

        load_students()

        messagebox.showinfo(
            "Success",
            "Student updated successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not update student:\n{error}"
        )


# ==========================================
# DELETE STUDENT
# ==========================================

def delete_student():
    if not selected_id.get():
        messagebox.showwarning(
            "No Selection",
            "Select a student from the table before deleting."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this student?"
    )

    if not confirm:
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM students WHERE id = ?",
                (int(selected_id.get()),)
            )

            deleted = cursor.rowcount

        if deleted:
            messagebox.showinfo(
                "Success",
                "Student deleted successfully!"
            )
        else:
            messagebox.showwarning(
                "Not Found",
                "The student record was not found."
            )

        load_students()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not delete student:\n{error}"
        )


# ==========================================
# RESET ALL STUDENTS
# ==========================================

def reset_all_students():
    confirm = messagebox.askyesno(
        "Confirm Reset",
        "WARNING: This will permanently delete ALL student records.\n\n"
        "Do you want to continue?"
    )

    if not confirm:
        return

    confirm_again = messagebox.askyesno(
        "Final Confirmation",
        "Are you absolutely sure?\n\n"
        "This action cannot be undone."
    )

    if not confirm_again:
        return

    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM students")
            conn.execute(
                "DELETE FROM sqlite_sequence WHERE name = ?",
                ("students",)
            )

        load_students()

        messagebox.showinfo(
            "Reset Successful",
            "All student records have been deleted."
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not reset student records:\n{error}"
        )


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("Student Information System")
root.geometry("850x650")
root.resizable(False, False)


# ==========================================
# LAVENDER & BLUSH COLOR PALETTE
# ==========================================

BG_COLOR = "#F7F3FA"

HEADER_BG = "#79658F"
HEADER_FG = "#FFFFFF"

LABEL_FG = "#665477"

ACCENT_COLOR = "#9B83B5"
ACCENT_HOVER = "#806A99"

UPDATE_COLOR = "#A68CB8"
UPDATE_HOVER = "#8E74A3"

DELETE_COLOR = "#D58E9A"
DELETE_HOVER = "#BF7180"

CLEAR_COLOR = "#A9A0B5"
CLEAR_HOVER = "#8D839A"

RESET_COLOR = "#B58A9C"
RESET_HOVER = "#966D80"

SELECTED_COLOR = "#E8DDEB"
BORDER_COLOR = "#DCD0E3"

WHITE = "#FFFFFF"

root.configure(bg=BG_COLOR)

selected_id = tk.StringVar()
status_var = tk.StringVar(value="Total students: 0")


# ==========================================
# STYLES
# ==========================================

style = ttk.Style(root)
style.theme_use("clam")

style.configure(
    "TFrame",
    background=BG_COLOR
)

style.configure(
    "TLabel",
    background=BG_COLOR,
    foreground=LABEL_FG,
    font=("Arial", 10)
)

style.configure(
    "TEntry",
    fieldbackground=WHITE,
    foreground="#51465C",
    padding=7,
    bordercolor=BORDER_COLOR
)

style.configure(
    "TButton",
    background=ACCENT_COLOR,
    foreground=WHITE,
    font=("Arial", 9, "bold"),
    padding=(10, 8),
    borderwidth=0
)

style.map(
    "TButton",
    background=[
        ("disabled", "#DCD0E3"),
        ("active", ACCENT_HOVER),
        ("pressed", ACCENT_HOVER)
    ],
    foreground=[
        ("disabled", WHITE),
        ("active", WHITE)
    ]
)


# Update button

style.configure(
    "Update.TButton",
    background=UPDATE_COLOR,
    foreground=WHITE
)

style.map(
    "Update.TButton",
    background=[
        ("active", UPDATE_HOVER),
        ("pressed", UPDATE_HOVER)
    ]
)


# Delete button

style.configure(
    "Delete.TButton",
    background=DELETE_COLOR,
    foreground=WHITE
)

style.map(
    "Delete.TButton",
    background=[
        ("active", DELETE_HOVER),
        ("pressed", DELETE_HOVER)
    ]
)


# Clear button

style.configure(
    "Clear.TButton",
    background=CLEAR_COLOR,
    foreground=WHITE
)

style.map(
    "Clear.TButton",
    background=[
        ("active", CLEAR_HOVER),
        ("pressed", CLEAR_HOVER)
    ]
)


# Reset button

style.configure(
    "Reset.TButton",
    background=RESET_COLOR,
    foreground=WHITE
)

style.map(
    "Reset.TButton",
    background=[
        ("active", RESET_HOVER),
        ("pressed", RESET_HOVER)
    ]
)


# ==========================================
# TREEVIEW STYLE
# ==========================================

style.configure(
    "Treeview",
    background=WHITE,
    foreground="#51465C",
    fieldbackground=WHITE,
    rowheight=35,
    font=("Arial", 10),
    bordercolor=BORDER_COLOR,
    borderwidth=1
)

style.configure(
    "Treeview.Heading",
    background=HEADER_BG,
    foreground=WHITE,
    font=("Arial", 10, "bold"),
    padding=10,
    relief="flat"
)

style.map(
    "Treeview.Heading",
    background=[("active", ACCENT_COLOR)],
    foreground=[("active", WHITE)]
)

style.map(
    "Treeview",
    background=[("selected", SELECTED_COLOR)],
    foreground=[("selected", "#51465C")]
)


# Scrollbar style

style.configure(
    "Vertical.TScrollbar",
    background="#D6C8DF",
    troughcolor=BG_COLOR,
    arrowcolor=HEADER_BG
)


# ==========================================
# HEADER
# ==========================================

header = tk.Frame(
    root,
    bg=HEADER_BG,
    height=90
)

header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="STUDENT INFORMATION SYSTEM",
    font=("Arial", 17, "bold"),
    bg=HEADER_BG,
    fg=HEADER_FG
).pack(pady=(18, 2))

tk.Label(
    header,
    text="Manage student records easily",
    font=("Arial", 9),
    bg=HEADER_BG,
    fg="#E8DDEB"
).pack()


# ==========================================
# INPUT FORM
# ==========================================

form = ttk.Frame(
    root,
    padding=(22, 15)
)

form.pack(fill="x")


ttk.Label(
    form,
    text="Student Name:"
).grid(
    row=0,
    column=0,
    padx=8,
    pady=8,
    sticky="w"
)

name_entry = ttk.Entry(
    form,
    width=38
)

name_entry.grid(
    row=0,
    column=1,
    padx=8,
    pady=8
)


ttk.Label(
    form,
    text="Age:"
).grid(
    row=1,
    column=0,
    padx=8,
    pady=8,
    sticky="w"
)

age_entry = ttk.Entry(
    form,
    width=38
)

age_entry.grid(
    row=1,
    column=1,
    padx=8,
    pady=8
)


ttk.Label(
    form,
    text="Course:"
).grid(
    row=2,
    column=0,
    padx=8,
    pady=8,
    sticky="w"
)

course_entry = ttk.Entry(
    form,
    width=38
)

course_entry.grid(
    row=2,
    column=1,
    padx=8,
    pady=8
)


# ==========================================
# ACTION BUTTONS
# ==========================================

buttons = ttk.Frame(root)
buttons.pack(pady=(2, 15))


ttk.Button(
    buttons,
    text="Add Student",
    command=add_student
).grid(
    row=0,
    column=0,
    padx=4
)


ttk.Button(
    buttons,
    text="Update",
    style="Update.TButton",
    command=update_student
).grid(
    row=0,
    column=1,
    padx=4
)


ttk.Button(
    buttons,
    text="Delete",
    style="Delete.TButton",
    command=delete_student
).grid(
    row=0,
    column=2,
    padx=4
)


ttk.Button(
    buttons,
    text="Clear",
    style="Clear.TButton",
    command=clear_fields
).grid(
    row=0,
    column=3,
    padx=4
)


ttk.Button(
    buttons,
    text="Refresh",
    command=load_students
).grid(
    row=0,
    column=4,
    padx=4
)


ttk.Button(
    buttons,
    text="Reset All",
    style="Reset.TButton",
    command=reset_all_students
).grid(
    row=0,
    column=5,
    padx=4
)


# ==========================================
# STUDENT TABLE
# ==========================================

table_frame = ttk.Frame(
    root,
    padding=(18, 0, 18, 5)
)

table_frame.pack(
    fill="both",
    expand=True
)

columns = ("id", "name", "age", "course")

student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10,
    selectmode="browse"
)


student_table.heading("id", text="ID")
student_table.heading("name", text="STUDENT NAME")
student_table.heading("age", text="AGE")
student_table.heading("course", text="COURSE")


student_table.column(
    "id",
    width=55,
    anchor="center",
    stretch=False
)

student_table.column(
    "name",
    width=250,
    anchor="w"
)

student_table.column(
    "age",
    width=75,
    anchor="center",
    stretch=False
)

student_table.column(
    "course",
    width=330,
    anchor="w"
)


# Alternating pastel rows

student_table.tag_configure(
    "evenrow",
    background="#FFFFFF"
)

student_table.tag_configure(
    "oddrow",
    background="#F3EDF7"
)


# Scrollbar

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=student_table.yview
)

student_table.configure(
    yscrollcommand=scrollbar.set
)

student_table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# Select student when clicking a row

student_table.bind(
    "<<TreeviewSelect>>",
    select_student
)


# ==========================================
# STATUS BAR
# ==========================================

status_bar = tk.Label(
    root,
    textvariable=status_var,
    bg=BG_COLOR,
    fg=LABEL_FG,
    font=("Arial", 9),
    anchor="w",
    padx=20,
    pady=8
)

status_bar.pack(fill="x")


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":
    connect_db()

    if root.winfo_exists():
        load_students()
        root.mainloop()
