import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
import datetime
import random

def generate_filename(user, system, method, condition, cell_type, position):
    current_date = datetime.date.today().strftime("%Y%m%d")
    return f"{current_date}_{user}_{system}_{method}_{condition}_{cell_type}_{position}"

def get_well_positions(start_row, end_row, start_col, end_col):
    rows = [chr(i) for i in range(ord(start_row), ord(end_row) + 1)]
    columns = list(range(start_col, end_col + 1))
    return [f"{row}{col}" for row in rows for col in columns]

def get_cell_types_info():
    cell_types_info = []
    num_cell_types = simpledialog.askinteger("Input", "Enter the number of different cell types:")
    for _ in range(num_cell_types):
        cell_type = simpledialog.askstring("Input", "Enter cell type:")
        row_range = simpledialog.askstring("Input", f"Enter row range for {cell_type} (e.g., A-F):")
        col_range = simpledialog.askstring("Input", f"Enter column range for {cell_type} (e.g., 1-8):")
        start_row, end_row = row_range.split('-')
        start_col, end_col = col_range.split('-')
        positions = get_well_positions(start_row.strip().upper(), end_row.strip().upper(), int(start_col.strip()), int(end_col.strip()))
        cell_types_info.append((cell_type, positions))
    return cell_types_info


def create_csv():
    num_wells = int(num_wells_var.get())
    num_plates = int(num_plates_var.get())
    user = user_var.get()
    system = system_var.get()
    method = method_var.get()
    path = path_var.get()
    inj_vol = inj_vol_var.get()
    randomize_queue = randomize_var.get()

    columns = ["Sample Type", "File Name", "Sample ID", "Path", "Instrument Method", 
               "Process Method", "Calibration File", "Position", "Inj Vol", "Level", 
               "Sample Wt", "Sample Vol", "ISTD Amt", "Dil Factor", "L1 Study", 
               "L2 Client", "L3 Laboratory", "L4 Company", "L5 Phone", "Comment", "Sample Name"]
    df = pd.DataFrame(columns=columns)

    for plate in range(num_plates):
        condition = simpledialog.askstring("Input", f"Enter condition for plate {plate + 1}:")
        tray = simpledialog.askstring("Input", f"Enter tray for plate {plate + 1} (B, G, R):").upper()
        if plate == 0 or not cell_types_info:
            cell_types_info = get_cell_types_info()

        for cell_type, positions in cell_types_info:
            for position in positions:
                tray_position = f"{tray}{position}"
                file_name = generate_filename(user, system, method, condition, cell_type, position)
                df = df.append({
                    "Sample Type": "Unknown",
                    "File Name": file_name,
                    "Sample ID": 1,
                    "Path": path,
                    "Position": tray_position,
                    "Inj Vol": inj_vol
                }, ignore_index=True)

    if randomize_queue:
        df = df.sample(frac=1).reset_index(drop=True)

    output_file_name = f"{num_wells * num_plates}_wells_output.csv"
    with open(output_file_name, 'w') as file:
        file.write("Bracket Type=4\n")
    df.to_csv(output_file_name, mode='a', index=False, header=True)

    messagebox.showinfo("Success", f"Data exported to {output_file_name}")

root = tk.Tk()
root.title("Well Plate Data Generator")

num_wells_var = tk.StringVar()
num_plates_var = tk.StringVar()
user_var = tk.StringVar()
system_var = tk.StringVar()
method_var = tk.StringVar()
path_var = tk.StringVar(value="D:\\")
inj_vol_var = tk.StringVar()
randomize_var = tk.BooleanVar(value=False)

tk.Label(root, text="Number of wells per plate:").pack()
tk.Entry(root, textvariable=num_wells_var).pack()

tk.Label(root, text="Number of plates:").pack()
tk.Entry(root, textvariable=num_plates_var).pack()

tk.Label(root, text="User Identifier:").pack()
tk.Entry(root, textvariable=user_var).pack()

tk.Label(root, text="System Used:").pack()
tk.Entry(root, textvariable=system_var).pack()

tk.Label(root, text="Method Applied:").pack()
tk.Entry(root, textvariable=method_var).pack()

tk.Label(root, text="Path:").pack()
tk.Entry(root, textvariable=path_var).pack()

tk.Label(root, text="Injection Volume:").pack()
tk.Entry(root, textvariable=inj_vol_var).pack()
tk.Checkbutton(root, text="Randomize Queue", variable=randomize_var).pack()

generate_button = tk.Button(root, text="Generate CSV", command=create_csv)
generate_button.pack()

root.mainloop()
