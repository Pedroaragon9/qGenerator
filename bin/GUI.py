import tkinter as tk
from tkinter import messagebox, simpledialog, PhotoImage
import pandas as pd
import datetime
import random

# Function to generate a filename based on given parameters
def generate_filename(user, system, method, condition, cell_type, position):
    current_date = datetime.date.today().strftime("%Y%m%d")
    return f"{current_date}_{user}_{system}_{method}_{condition}_{cell_type}_{position}"

# Function to get well positions based on the start and end rows and columns
def get_well_positions(start_row, end_row, start_col, end_col):
    rows = [chr(i) for i in range(ord(start_row), ord(end_row) + 1)]
    columns = [str(i) for i in range(start_col, end_col + 1)]
    return [f"{row}{col}" for row in rows for col in columns]

# Function to gather information about cell types for a plate
def get_cell_types_info(plate_number):
    cell_types_info = []
    num_cell_types = simpledialog.askinteger("Input", f"Enter the number of different cell types for plate {plate_number}:")
    for _ in range(num_cell_types):
        cell_type = simpledialog.askstring("Input", f"Enter cell type for plate {plate_number}:")
        row_range = simpledialog.askstring("Input", f"Enter row range for {cell_type} (e.g., A-F):")
        col_range = simpledialog.askstring("Input", f"Enter column range for {cell_type} (e.g., 1-12):")
        start_row, end_row = row_range.split('-')
        start_col, end_col = col_range.split('-')
        positions = get_well_positions(start_row.strip().upper(), end_row.strip().upper(), int(start_col.strip()), int(end_col.strip()))
        cell_types_info.append((cell_type, positions))
    return cell_types_info

# Function to create a CSV file based on the input data
def create_csv():
    num_wells = int(num_wells_var.get())
    num_plates = int(num_plates_var.get())
    user = user_var.get()
    system = system_var.get()
    method = method_var.get()
    path = path_var.get()
    inj_vol = inj_vol_var.get()
    randomize_queue = randomize_var.get()
    same_layout = same_layout_var.get()

    if same_layout:
        cell_types_info = get_cell_types_info(1)
        all_plates_info = [cell_types_info for _ in range(num_plates)]
    else:
        all_plates_info = [get_cell_types_info(i + 1) for i in range(num_plates)]

    columns = ["Sample Type", "File Name", "Sample ID", "Path", "Instrument Method",
               "Process Method", "Calibration File", "Position", "Inj Vol", "Level",
               "Sample Wt", "Sample Vol", "ISTD Amt", "Dil Factor", "L1 Study",
               "L2 Client", "L3 Laboratory", "L4 Company", "L5 Phone", "Comment", "Sample Name"]
    df = pd.DataFrame(columns=columns)

    for plate, cell_types_info in enumerate(all_plates_info, start=1):
        tray = simpledialog.askstring("Input", f"Enter tray for plate {plate} (B, G, R):").upper()
        condition = simpledialog.askstring("Input", f"Enter condition for plate {plate}:")
        for cell_type, positions in cell_types_info:
            for position in positions:
                file_name = generate_filename(user, system, method, condition, cell_type, position)
                df = df.append({
                    "Sample Type": "Unknown",
                    "File Name": file_name,
                    "Sample ID": 1, 
                    "Path": path,
                    "Position": f"{tray}{position}",
                    "Inj Vol": inj_vol
                    # Update other fields as necessary
                }, ignore_index=True)

    if randomize_queue:
        df = df.sample(frac=1).reset_index(drop=True)

    output_file_name = f"{num_wells * num_plates}_wells_output.csv"
    with open(output_file_name, 'w') as file:
        file.write("Bracket Type=4\n")
    df.to_csv(output_file_name, mode='a', index=False, header=True)

    messagebox.showinfo("Success", f"Data exported to {output_file_name}")

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Well Plate Data Generator")

    # Load the logo image
    logo_path = 'bin/250px-Arwing_Starlink.png'  #logo
    logo_image = PhotoImage(file=logo_path)

    # Display the logo image
    logo_label = tk.Label(root, image=logo_image)
    logo_label.pack()

    # Define variables
    global num_wells_var, num_plates_var, user_var, system_var, method_var, path_var, inj_vol_var, randomize_var, same_layout_var
    num_wells_var = tk.StringVar()
    num_plates_var = tk.StringVar()
    user_var = tk.StringVar()
    system_var = tk.StringVar()
    method_var = tk.StringVar()
    path_var = tk.StringVar(value="D:\\")
    inj_vol_var = tk.StringVar()
    randomize_var = tk.BooleanVar(value=False)
    same_layout_var = tk.BooleanVar(value=False)

    # Define interface
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

    tk.Checkbutton(root, text="Same sample position layout for all plates", variable=same_layout_var).pack()
    tk.Checkbutton(root, text="Randomize Queue", variable=randomize_var).pack()

    generate_button = tk.Button(root, text="Generate CSV", command=create_csv)
    generate_button.pack()

    root.mainloop()

# Call the function to create the GUI with the logo
create_gui()
