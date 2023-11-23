import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import messagebox, ttk, simpledialog
import pandas as pd
import datetime
import random

# Function to generate the filename
def generate_filename(user, system, method, condition, cell_type, position):
    current_date = datetime.date.today().strftime("%Y%m%d")
    return f"{current_date}_{user}_{system}_{method}_{condition}_{cell_type}_{position}"

# Function to get well positions
def get_well_positions(start_row, end_row, start_col, end_col):
    rows = [chr(i) for i in range(ord(start_row), ord(end_row) + 1)]
    columns = [str(i) for i in range(start_col, end_col + 1)]
    return [f"{row}{col}" for row in rows for col in columns]

# Function to get cell type layout info for a single plate
def get_cell_types_info():
    cell_types_info = []
    num_cell_types = simpledialog.askinteger("Input", "Enter the number of different cell types:")
    for _ in range(num_cell_types):
        cell_type = simpledialog.askstring("Input", "Enter cell type:")
        row_range = simpledialog.askstring("Input", f"Enter row range for {cell_type} (e.g., A-F):")
        col_range = simpledialog.askstring("Input", f"Enter column range for {cell_type} (e.g., 1-12):")
        start_row, end_row = row_range.split('-')
        start_col, end_col = col_range.split('-')
        positions = get_well_positions(start_row.strip().upper(), end_row.strip().upper(), int(start_col.strip()), int(end_col.strip()))
        cell_types_info.append((cell_type, positions))
    return cell_types_info

# Function to create CSV
def create_csv():
    num_wells = int(num_wells_var.get())
    num_plates = int(num_plates_var.get())
    user = user_var.get()
    system = system_var.get()
    method = method_var.get()
    path = path_var.get()
    inj_vol = inj_vol_var.get()
    randomize_queue = randomize_var.get()
    cell_types_info = []

    if same_layout_var.get():
        cell_types_info = get_cell_types_info()

    for plate in range(num_plates):
        if not same_layout_var.get():
            cell_types_info = get_cell_types_info()
        tray = trays_var[plate].get()
        for cell_type, positions in cell_types_info:
            for position in positions:
                file_name = generate_filename(user, system, method, tray, cell_type, position)
                df.loc[len(df)] = ["Unknown", file_name, "", path, "", "", "", f"{tray}{position}", inj_vol, "", "", "", "", "", "", "", "", "", "", "", ""]

    if randomize_queue:
        df = df.sample(frac=1).reset_index(drop=True)

    output_file_name = "output.csv"
    df.to_csv(output_file_name, index=False)
    messagebox.showinfo("Success", f"Data exported to {output_file_name}")

root = tk.Tk()
root.title("Well Plate Data Generator")

# Define input variables
num_wells_var = tk.StringVar()
num_plates_var = tk.StringVar()
user_var = tk.StringVar()
system_var = tk.StringVar()
method_var = tk.StringVar()
path_var = tk.StringVar(value="D:\\")
inj_vol_var = tk.StringVar()
randomize_var = tk.BooleanVar(value=False)
same_layout_var = tk.BooleanVar(value=False)

# Define the layout using the grid method
tk.Label(root, text="Number of wells per plate:").grid(row=0, column=0)
num_wells_entry = tk.Entry(root, textvariable=num_wells_var)
num_wells_entry.grid(row=0, column=1)

tk.Label(root, text="Number of plates:").grid(row=1, column=0)
num_plates_entry = tk.Entry(root, textvariable=num_plates_var)
num_plates_entry.grid(row=1, column=1)

tk.Label(root, text="User Identifier:").grid(row=2, column=0)
user_entry = tk.Entry(root, textvariable=user_var)
user_entry.grid(row=2, column=1)

tk.Label(root, text="System Used:").grid(row=3, column=0)
system_entry = tk.Entry(root, textvariable=system_var)
system_entry.grid(row=3, column=1)

tk.Label(root, text="Method Applied:").grid(row=4, column=0)
method_entry = tk.Entry(root, textvariable=method_var)
method_entry.grid(row=4, column=1)

tk.Label(root, text="Path:").grid(row=5, column=0)
path_entry = tk.Entry(root, textvariable=path_var)
path_entry.grid(row=5, column=1)

tk.Label(root, text="Injection Volume:").grid(row=6, column=0)
inj_vol_entry = tk.Entry(root, textvariable=inj_vol_var)
inj_vol_entry.grid(row=6, column=1)

tk.Checkbutton(root, text="Same sample position layout for all plates", variable=same_layout_var).grid(row=7, column=0, columnspan=2)
tk.Checkbutton(root, text="Randomize Queue", variable=randomize_var).grid(row=8, column=0, columnspan=2)

# Placeholder lists for tray variables and optionmenus
trays_var = []
tray_optionmenus = []

# Function to dynamically create tray dropdowns based on the number of plates
def update_tray_widgets(*args):
    # Clear existing tray dropdowns
    for optionmenu in tray_optionmenus:
        optionmenu.destroy()
    tray_optionmenus.clear()
    trays_var.clear()

    try:
        num_plates = int(num_plates_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of plates.")
        return

    for i in range(num_plates):
        tray_var = tk.StringVar(value="B")  # Default value for tray
        tray_dropdown = ttk.Combobox(root, textvariable=tray_var, values=['B', 'G', 'R'], state='readonly')
        tray_dropdown.grid(row=9+i, column=1)
        trays_var.append(tray_var)
        tray_optionmenus.append(tray_dropdown)

# Bind the update_tray_widgets function to the number of plates entry
num_plates_var.trace_add('write', update_tray_widgets)

generate_button = tk.Button(root, text="Generate CSV", command=create_csv)
generate_button.grid(row=9, column=0, pady=20)

root.mainloop()
