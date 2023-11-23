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

def get_cell_types():
    cell_types_info = []
    num_cell_types = int(input("Enter the number of different cell types: "))
    for _ in range(num_cell_types):
        cell_type = input("Enter cell type: ")
        start_row = input(f"Enter start row (e.g., A) for {cell_type}: ").upper()
        end_row = input(f"Enter end row (e.g., F) for {cell_type}: ").upper()
        start_col = int(input(f"Enter start column (e.g., 1) for {cell_type}: "))
        end_col = int(input(f"Enter end column (e.g., 8) for {cell_type}: "))
        positions = get_well_positions(start_row, end_row, start_col, end_col)
        cell_types_info.append((cell_type, positions))
    return cell_types_info

if __name__ == "__main__":
    # Define the columns as per the CSV structure
    columns = ["Sample Type", "File Name", "Sample ID", "Path", "Instrument Method", 
               "Process Method", "Calibration File", "Position", "Inj Vol", "Level", 
               "Sample Wt", "Sample Vol", "ISTD Amt", "Dil Factor", "L1 Study", 
               "L2 Client", "L3 Laboratory", "L4 Company", "L5 Phone", "Comment", "Sample Name"]
    df = pd.DataFrame(columns=columns)

    # General sample information
    num_wells = int(input("Enter the number of wells per plate: "))
    num_plates = int(input("Enter the number of plates (up to 3): "))
    user = input("Enter user identifier: ")
    system = input("Enter system used: ")
    method = input("Enter method applied: ")
    path = input("Enter path (default is D:\\): ")
    path = path if path else "D:\\"
    inj_vol = input("Enter injection volume: ")

    reuse_cell_types = False
    cell_types_info = []

    if num_plates > 1:
        reuse_cell_types = input("Use the same cell types and positions for all plates? (y/n): ").lower() == 'y'

    for plate in range(num_plates):
        # Plate-specific information
        print(f"\nPlate {plate + 1}:")
        condition = input("Enter condition for this plate: ")
        tray = input("Enter tray for this plate (B for Blue, G for Green, R for Red): ").upper()

        if plate == 0 or not reuse_cell_types:
            cell_types_info = get_cell_types()

        for cell_type, positions in cell_types_info:
            for position in positions:
                tray_position = f"{tray}{position}"
                file_name = generate_filename(user, system, method, condition, cell_type, position)
                # Fill the DataFrame with the required and empty values
                df = df.append({
                    "Sample Type": "Unknown",
                    "File Name": file_name,
                    "Sample ID": 1,  # Assuming Sample ID is always 1 as per your CSV
                    "Path": path,
                    "Position": tray_position,
                    "Inj Vol": inj_vol
                    # Other columns are left empty
                }, ignore_index=True)

    # Randomize the queue if requested
    randomize = input("\nDo you want to randomize the queue? (y/n): ").lower()
    if randomize == 'y':
        df = df.sample(frac=1).reset_index(drop=True)

    # Export to CSV
    output_file_name = f"{num_wells * num_plates}_wells_output.csv"
    with open(output_file_name, 'w') as file:
        file.write("Bracket Type=4\n")  # Write the first line

    # Append the DataFrame with the header
    df.to_csv(output_file_name, mode='a', index=False, header=True)

    print(f"Data exported to {output_file_name}")
