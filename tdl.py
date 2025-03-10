import sqlite3
import tkinter as tk
from tkinter import ttk, font, messagebox, PhotoImage

# Creating database
conn = sqlite3.connect("task.db")
cursor = conn.cursor()
cursor.execute("""
                CREATE TABLE IF NOT EXISTS task(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL)
               """)
conn.commit()

# Creating window
window = tk.Tk()
window.title("To-Do App")
window.configure(bg="#F0F0F0")
window.geometry("500x600")

# Load icons
edit_icon = PhotoImage(file="edit.png").subsample(3, 3)
delete_icon = PhotoImage(file="delete.png").subsample(3, 3)

# Global variable for editing task
editing_task_id = None

# Function to add a task
def add_task():
    global editing_task_id
    task = task_entry.get().strip()
    if task and task != "Write your task here":
        if editing_task_id is not None:
            cursor.execute("UPDATE task SET task=? WHERE id=?", (task, editing_task_id))
            conn.commit()
            load_tasks()
            editing_task_id = None
        else:
            cursor.execute("INSERT INTO task (task) VALUES (?)", (task,))
            conn.commit()
            load_tasks()
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Invalid Input", "Please enter a valid task.")

# Function to load tasks from the database
def load_tasks():
    for widget in canvas_inner.winfo_children():
        widget.destroy()
    cursor.execute("SELECT * FROM task")
    tasks = cursor.fetchall()
    for task in tasks:
        add_task_item(task[0], task[1])

# Function to add task to UI
def add_task_item(task_id, task_text):
    task_frame = tk.Frame(canvas_inner, bg="white", bd=1, relief=tk.SOLID)
    task_label = tk.Label(task_frame, text=task_text, font=("Garamond", 16), bg="white", width=25, height=2, anchor="w")
    task_label.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5)

    edit_button = tk.Button(task_frame, command=lambda: prepare_editing(task_id, task_text), image=edit_icon, bg="white")
    edit_button.pack(side=tk.RIGHT, padx=5)

    delete_button = tk.Button(task_frame, command=lambda: delete_task(task_id, task_frame), image=delete_icon, bg="white")
    delete_button.pack(side=tk.RIGHT, padx=5)

    checkbox = ttk.Checkbutton(task_frame, command=lambda: toggle_underline(task_label))
    checkbox.pack(side=tk.RIGHT, padx=5)

    task_frame.pack(fill=tk.X, padx=5, pady=5)
    canvas_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to prepare a task for editing
def prepare_editing(task_id, task_text):
    global editing_task_id
    editing_task_id = task_id
    task_entry.delete(0, tk.END)
    task_entry.insert(0, task_text)

# Function to delete a task
def delete_task(task_id, task_frame):
    cursor.execute("DELETE FROM task WHERE id=?", (task_id,))
    conn.commit()
    task_frame.destroy()
    canvas_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to toggle underline for completed tasks
def toggle_underline(label):
    current_font = label.cget("font")
    if "overstrike" in current_font:
        new_font = current_font.replace("overstrike", "")
    else:
        new_font = current_font + " overstrike"
    label.configure(font=new_font)

# Function to handle input behavior
def on_entry_click(event):
    if task_entry.get() == "Write your task here":
        task_entry.delete(0, tk.END)
        task_entry.configure(fg="black")

def on_focus_out(event):
    if not task_entry.get().strip():
        task_entry.delete(0, tk.END)
        task_entry.insert(0, "Write your task here")
        task_entry.configure(fg="grey")

# UI Elements
header_font = font.Font(family="Garamond", size=24, weight="bold")
header_label = tk.Label(window, text="To-Do-App", font=header_font, bg="#F0F0F0", fg="#333")
header_label.pack(pady=20)

frame = tk.Frame(window, bg="#F0F0F0")
frame.pack(pady=10)

task_entry = tk.Entry(frame, font=("Garamond", 14), bg="white", fg="grey", width=30)
task_entry.insert(0, "Write your task here")
task_entry.bind("<FocusIn>", on_entry_click)
task_entry.bind("<FocusOut>", on_focus_out)
task_entry.pack(side=tk.LEFT, padx=10)

add_button = tk.Button(frame, command=add_task, text="Add Task", bg="#4CAF50", fg="white", height=1, width=15, font=("Roboto", 11))
add_button.pack(side=tk.LEFT, pady=10)

task_list_frame = tk.Frame(window, bg="white")
task_list_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(task_list_frame, bg="white")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(task_list_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

canvas_inner = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=canvas_inner, anchor="nw")

canvas_inner.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

# Load existing tasks from the database
load_tasks()

window.mainloop()

conn.close()
