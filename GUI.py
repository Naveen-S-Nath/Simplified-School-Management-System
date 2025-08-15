# GUI.py
import sys, traceback
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import backend  # our db layer

print("Starting GUI...")

# ---------- Helpers ----------
def show_error(err):
    messagebox.showerror("Error", str(err))

def validate_and_get_form():
    name = name_var.get().strip()
    age = age_var.get().strip()
    grade = grade_var.get().strip()
    phone = phone_var.get().strip()
    address = address_var.get().strip()
    dob = dob_var.get().strip()  # DD/MM/YYYY or blank
    if not name:
        raise ValueError("Name is required.")
    if age and not age.isdigit():
        raise ValueError("Age must be a number.")
    if phone and not phone.isdigit():
        raise ValueError("Phone must contain digits only.")
    # backend will validate DOB format too
    return name, age, grade, phone, address, dob

def clear_form():
    name_var.set("")
    age_var.set("")
    grade_var.set("")
    phone_var.set("")
    address_var.set("")
    dob_var.set("")
    search_var.set("")

# ---------- Actions ----------
def view_records():
    try:
        rows = backend.view_all()
        table.delete(*table.get_children())
        for r in rows:
            table.insert("", "end", values=r)
    except Exception as e:
        show_error(e)

def search_records():
    q = search_var.get().strip()
    if not q:
        messagebox.showwarning("Input", "Type something to search.")
        return
    try:
        rows = backend.search(q)
        table.delete(*table.get_children())
        for r in rows:
            table.insert("", "end", values=r)
    except Exception as e:
        show_error(e)

def add_record():
    try:
        name, age, grade, phone, address, dob = validate_and_get_form()
        backend.insert(name, age, grade, phone, address, dob)
        clear_form()
        view_records()
    except Exception as e:
        show_error(e)

def update_record():
    sel = table.focus()
    if not sel:
        messagebox.showwarning("Selection", "Select a row to update.")
        return
    sid = table.item(sel, "values")[0]
    try:
        name, age, grade, phone, address, dob = validate_and_get_form()
        backend.update(sid, name, age, grade, phone, address, dob)
        clear_form()
        view_records()
    except Exception as e:
        show_error(e)

def delete_record():
    sel = table.focus()
    if not sel:
        messagebox.showwarning("Selection", "Select a row to delete.")
        return
    sid, name = table.item(sel, "values")[0], table.item(sel, "values")[1]
    if not messagebox.askyesno("Confirm", f"Delete student #{sid} ({name})?"):
        return
    try:
        backend.delete(sid)
        view_records()
        clear_form()
    except Exception as e:
        show_error(e)

def fill_form_from_table(_event=None):
    sel = table.focus()
    if not sel:
        return
    values = table.item(sel, "values")
    if not values:
        return
    # ID, Name, Age, Grade, Phone, Address, DOB
    name_var.set(values[1] or "")
    age_var.set("" if values[2] in (None, "", "None") else str(values[2]))
    grade_var.set(values[3] or "")
    phone_var.set(values[4] or "")
    address_var.set(values[5] or "")
    dob_var.set(values[6] or "")

# ---------- UI ----------
root = tb.Window(themename="cosmo")
root.title("School Management System")
root.geometry("1200x750")

# Vars
name_var = tk.StringVar()
age_var = tk.StringVar()
grade_var = tk.StringVar()
phone_var = tk.StringVar()
address_var = tk.StringVar()
dob_var = tk.StringVar()      # DD/MM/YYYY
search_var = tk.StringVar()

# Title
tb.Label(root, text="School Database Manager", font=("Helvetica", 18, "bold")).pack(pady=10)

# Form
form = tb.Frame(root)
form.pack(pady=10)

tb.Label(form, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=name_var, width=25).grid(row=0, column=1, padx=6, pady=6)

tb.Label(form, text="Age").grid(row=0, column=2, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=age_var, width=10).grid(row=0, column=3, padx=6, pady=6)

tb.Label(form, text="Grade").grid(row=0, column=4, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=grade_var, width=10).grid(row=0, column=5, padx=6, pady=6)

tb.Label(form, text="Phone").grid(row=1, column=0, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=phone_var, width=20).grid(row=1, column=1, padx=6, pady=6)

tb.Label(form, text="Address").grid(row=1, column=2, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=address_var, width=40).grid(row=1, column=3, columnspan=3, padx=6, pady=6, sticky="we")

tb.Label(form, text="DOB (DD/MM/YYYY)").grid(row=2, column=0, padx=6, pady=6, sticky="e")
tb.Entry(form, textvariable=dob_var, width=20).grid(row=2, column=1, padx=6, pady=6)

# Buttons
btns = tb.Frame(root)
btns.pack(pady=10)
tb.Button(btns, text="Add", bootstyle="success", command=add_record).grid(row=0, column=0, padx=6)
tb.Button(btns, text="Update", bootstyle="info", command=update_record).grid(row=0, column=1, padx=6)
tb.Button(btns, text="Delete", bootstyle="danger", command=delete_record).grid(row=0, column=2, padx=6)
tb.Button(btns, text="View All", bootstyle="secondary", command=view_records).grid(row=0, column=3, padx=6)
tb.Button(btns, text="Clear Form", bootstyle="warning", command=clear_form).grid(row=0, column=4, padx=6)

# Search
search_frame = tb.Frame(root)
search_frame.pack(pady=8)
tb.Entry(search_frame, textvariable=search_var, width=40).grid(row=0, column=0, padx=6)
tb.Button(search_frame, text="Search", bootstyle="primary", command=search_records).grid(row=0, column=1, padx=6)

# Table
cols = ("ID", "Name", "Age", "Grade", "Phone", "Address", "DOB")
table_frame = tb.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

table = ttk.Treeview(table_frame, columns=cols, show="headings", height=22)
for c in cols:
    table.heading(c, text=c)
# sensible widths
table.column("ID", width=60, anchor="center")
table.column("Name", width=180)
table.column("Age", width=60, anchor="center")
table.column("Grade", width=80, anchor="center")
table.column("Phone", width=130)
table.column("Address", width=320)
table.column("DOB", width=120, anchor="center")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
table.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
table.pack(fill="both", expand=True)

table.bind("<<TreeviewSelect>>", fill_form_from_table)

# Initial load
try:
    view_records()
except Exception:
    traceback.print_exc()

print("Launching window...")
root.mainloop()
