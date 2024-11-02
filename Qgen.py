import sys
from qtpy.QtWidgets import (QApplication, QWidget, QComboBox, QVBoxLayout, QTableWidget, QGridLayout,
                            QTableWidgetItem, QFileDialog, QPushButton, QLabel, QLineEdit, 
                            QTableWidgetSelectionRange, QTextEdit, QCheckBox, QHBoxLayout, QDialog)
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QColor, QDoubleValidator
import pandas as pd

class PlateSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qgenerator")
        
        # Initialize attributes for tracking
        self.selected_positions = []   # Track selected positions on the grid
        self.sample_groups = []        # Store each sample group with identifiers and colors
        self.cell_to_group = {}        # Map each cell to its sample group for easy removal
        self.colors = self.generate_colors(96)  # Initialize a list of distinct colors
        self.current_color_index = 0   # Track current color index

        # Main layout
        self.layout = QVBoxLayout(self)

        # Plate type selection with styling
        self.plate_type_label = QLabel("Select Plate Type:")
        self.plate_type_label.setFont(QFont("Arial", 12))
        self.plate_type_combo = QComboBox()
        self.plate_type_combo.addItems(["96-well", "384-well"])
        self.plate_type_combo.currentTextChanged.connect(self.create_plate_grid)

        self.layout.addWidget(self.plate_type_label)
        self.layout.addWidget(self.plate_type_combo)

        # File Prefix Input for each sample group
        self.file_prefix_label = QLabel("File Prefix:")
        self.file_prefix_input = QLineEdit()
        self.layout.addWidget(self.file_prefix_label)
        self.layout.addWidget(self.file_prefix_input)

        # Sample Name Input
        self.sample_name_label = QLabel("Sample Name:")
        self.sample_name_input = QLineEdit()
        self.layout.addWidget(self.sample_name_label)
        self.layout.addWidget(self.sample_name_input)

        # Tray position selector
        self.tray_color_label = QLabel("Select Tray position:")
        self.tray_color_combo = QComboBox()
        self.tray_color_combo.addItems(["Red", "Green", "Blue", "Yellow"])
        self.layout.addWidget(self.tray_color_label)
        self.layout.addWidget(self.tray_color_combo)

        # Injection Volume Input with numeric-only restriction and checkbox
        self.injection_volume_label = QLabel("Injection Volume:")
        self.injection_volume_input = QLineEdit()
        self.injection_volume_input.setValidator(QDoubleValidator(0.0, 9999.99, 2))
        self.same_inj_vol_checkbox = QCheckBox("Same volume for all samples")
        self.layout.addWidget(self.injection_volume_label)
        self.layout.addWidget(self.injection_volume_input)
        self.layout.addWidget(self.same_inj_vol_checkbox)
        
        # Instrument Method Input
        self.instrument_method_label = QLabel("Instrument Method:")
        self.instrument_method_input = QLineEdit()
        self.instrument_method_button = QPushButton("Browse")
        self.instrument_method_button.clicked.connect(self.browse_instrument_method)
        self.same_instrument_method_checkbox = QCheckBox("Use same method for all samples")
        
        # Path Input
        self.path_label = QLabel("Path:")
        self.path_input = QLineEdit()
        self.path_button = QPushButton("Browse")
        self.path_button.clicked.connect(self.browse_path)
        
        # Add layouts for Path and Instrument Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(self.instrument_method_input)
        method_layout.addWidget(self.instrument_method_button)
        self.layout.addWidget(self.instrument_method_label)
        self.layout.addLayout(method_layout)
        self.layout.addWidget(self.same_instrument_method_checkbox)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_button)
        self.layout.addWidget(self.path_label)
        self.layout.addLayout(path_layout)

        # Mini grid and Sample Overview title
        self.mini_grid = QTableWidget()
        self.mini_grid.setSelectionMode(QTableWidget.NoSelection)
        self.mini_grid.setEditTriggers(QTableWidget.NoEditTriggers)

        # Table for displaying Sample Overview
        self.sample_info_table = QTableWidget(0, 4)
        self.sample_info_table.setHorizontalHeaderLabels(["Sample", "Inj. Vol.", "Instrument Method", "Path"])
        self.sample_info_table.horizontalHeader().setStretchLastSection(True)

        # Sample Overview Title
        self.sample_overview_label = QLabel("Sample Overview")
        self.sample_overview_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Sample log for displaying added samples
        self.sample_log_label = QLabel("Sample Log")
        self.sample_log_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.sample_log = QTextEdit()
        self.sample_log.setReadOnly(True)

        # Layout for Sample Overview and sample log
        self.grid_and_info_layout = QVBoxLayout()
        self.grid_and_info_layout.addWidget(self.sample_overview_label)
        self.grid_and_info_layout.addWidget(self.sample_info_table)
        self.grid_and_info_layout.addWidget(self.sample_log_label)
        self.grid_and_info_layout.addWidget(self.sample_log)

        # Layout for Plate Overview and mini grid
        mini_grid_layout = QVBoxLayout()
        plate_overview_label = QLabel("Plate Overview")
        plate_overview_label.setFont(QFont("Arial", 12, QFont.Bold))
        mini_grid_layout.addWidget(plate_overview_label)
        mini_grid_layout.addWidget(self.mini_grid)

        # Add viewer buttons
        self.mini_grid_viewer_button = QPushButton("Viewer")
        self.mini_grid_viewer_button.clicked.connect(self.show_mini_grid_viewer)
        mini_grid_layout.addWidget(self.mini_grid_viewer_button)

        self.sample_info_viewer_button = QPushButton("Viewer")
        self.sample_info_viewer_button.clicked.connect(self.show_sample_info_viewer)
        self.grid_and_info_layout.addWidget(self.sample_info_viewer_button)

        # Combined layout for grid and sample info
        combined_layout = QHBoxLayout()
        combined_layout.addLayout(mini_grid_layout)
        combined_layout.addLayout(self.grid_and_info_layout)
        self.layout.addLayout(combined_layout)

        # Clear All button
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_all_button)

        # Main grid setup and button to generate queue
        self.select_samples_label = QLabel("Select samples here")
        self.select_samples_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.layout.addWidget(self.select_samples_label)

        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.viewport().installEventFilter(self)
        self.layout.addWidget(self.table)
        self.create_plate_grid()

        self.add_samples_button = QPushButton("Add Samples")
        self.add_samples_button.clicked.connect(self.add_samples)
        self.layout.addWidget(self.add_samples_button)

        self.generate_button = QPushButton("Generate Queue")
        self.generate_button.clicked.connect(self.generate_queue)
        self.layout.addWidget(self.generate_button)

    def show_mini_grid_viewer(self):
        viewer = QDialog(self)
        viewer.setWindowTitle("Plate Overview Viewer")
        viewer.setMinimumSize(600, 400)
        viewer_layout = QVBoxLayout(viewer)

        # Determine grid dimensions based on selected plate type
        plate_type = self.plate_type_combo.currentText()
        rows = "ABCDEFGH" if plate_type == "96-well" else "ABCDEFGHIJKLMNOP"
        cols = 12 if plate_type == "96-well" else 24

        # Create table with appropriate row and column counts
        mini_grid_view = QTableWidget(len(rows), cols)
        mini_grid_view.setHorizontalHeaderLabels([str(i+1) for i in range(cols)])  # Column headers as numbers
        mini_grid_view.setVerticalHeaderLabels(list(rows))  # Row headers as letters
        mini_grid_view.horizontalHeader().setStretchLastSection(True)
        mini_grid_view.verticalHeader().setStretchLastSection(True)

        # Copy contents of mini grid to viewer
        for row in range(len(rows)):
            for col in range(cols):
                item = self.mini_grid.item(row, col)
                if item:
                    new_item = QTableWidgetItem(item.text())
                    new_item.setBackground(item.background())
                    mini_grid_view.setItem(row, col, new_item)
        
        viewer_layout.addWidget(mini_grid_view)
        viewer.setLayout(viewer_layout)
        viewer.resize(800, 600)
        viewer.exec_()


    def show_sample_info_viewer(self):
        viewer = QDialog(self)
        viewer.setWindowTitle("Sample Overview Viewer")
        viewer.setMinimumSize(600, 400)
        viewer_layout = QVBoxLayout(viewer)
        sample_info_view = QTableWidget(self.sample_info_table.rowCount(), self.sample_info_table.columnCount())
        sample_info_view.setHorizontalHeaderLabels(["Sample", "Inj. Vol.", "Instrument Method", "Path"])
        sample_info_view.horizontalHeader().setStretchLastSection(True)
        sample_info_view.verticalHeader().setStretchLastSection(True)

        # Copy contents of sample info table to viewer
        for row in range(self.sample_info_table.rowCount()):
            for col in range(self.sample_info_table.columnCount()):
                item = self.sample_info_table.item(row, col)
                if item:
                    new_item = QTableWidgetItem(item.text())
                    new_item.setBackground(item.background())
                    sample_info_view.setItem(row, col, new_item)

        viewer_layout.addWidget(sample_info_view)
        viewer.setLayout(viewer_layout)
        viewer.resize(800, 600)
        viewer.exec_()
        
    def create_plate_grid(self):
        plate_type = self.plate_type_combo.currentText()
        rows = "ABCDEFGH" if plate_type == "96-well" else "ABCDEFGHIJKLMNOP"
        cols = 12 if plate_type == "96-well" else 24

        # Clear and set up the main grid
        self.table.clear()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(cols)
        self.table.setVerticalHeaderLabels(list(rows))
        self.table.setHorizontalHeaderLabels([str(i+1) for i in range(cols)])
        self.table.clearSelection()

        # Populate table cells with well identifiers
        for row_index, row_label in enumerate(rows):
            for col_index in range(cols):
                well_position = f"{row_label}{col_index + 1}"
                cell = QTableWidgetItem(well_position)
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_index, col_index, cell)

        # Clear and set up the mini grid with the same dimensions
        self.mini_grid.setRowCount(len(rows))
        self.mini_grid.setColumnCount(cols)
        self.mini_grid.setVerticalHeaderLabels(list(rows))
        self.mini_grid.setHorizontalHeaderLabels([str(i+1) for i in range(cols)])

        # Populate the mini grid cells without text to act as visual blocks
        for row in range(len(rows)):
            for col in range(cols):
                mini_cell = QTableWidgetItem()
                mini_cell.setFlags(Qt.ItemIsEnabled)  # Non-selectable
                self.mini_grid.setItem(row, col, mini_cell)

    def eventFilter(self, source, event):
        if source is self.table.viewport():
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                item = self.table.itemAt(event.pos())
                if item:
                    position = item.text()
                    if position in self.cell_to_group:
                        # If the position is already part of a group, remove it
                        group_index = self.cell_to_group[position]
                        self.remove_cell_from_group(position, group_index)
                    else:
                        # Start new selection if it's not defined
                        self.mouse_pressed = True
                        self.start_cell = (item.row(), item.column())
            elif event.type() == event.MouseMove and self.mouse_pressed:
                item = self.table.itemAt(event.pos())
                if item and self.start_cell:
                    end_cell = (item.row(), item.column())
                    self.select_range(self.start_cell, end_cell)
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.mouse_pressed = False
                self.start_cell = None
        return super().eventFilter(source, event)
    
    def remove_cell_from_group(self, position, group_index):
        # Remove the cell from the sample group
        group = self.sample_groups[group_index]
        if position in group["positions"]:
            group["positions"].remove(position)
            del self.cell_to_group[position]

            # Reset the background color of the removed cell in the main grid
            row = ord(position[0]) - ord('A')
            col = int(position[1:]) - 1
            item = self.table.item(row, col)
            if item:
                item.setBackground(Qt.white)

            # Update mini grid colors to reflect changes
            self.update_mini_grid()
            
            # If the group is now empty, remove it entirely
            if not group["positions"]:
                del self.sample_groups[group_index]

            # Update the sample log to reflect the changes
            self.update_sample_log()
            self.update_sample_info_table()

    def update_mini_grid(self):
        # Clear mini grid colors
        for row in range(self.mini_grid.rowCount()):
            for col in range(self.mini_grid.columnCount()):
                self.mini_grid.item(row, col).setBackground(Qt.white)
        
        # Apply current sample group colors
        for group in self.sample_groups:
            color = group["color"]
            for position in group["positions"]:
                # Split the position to get the tray color prefix and actual grid position
                try:
                    tray_prefix, grid_position = position.split(":")
                    row = ord(grid_position[0]) - ord('A')  # Convert 'A'-'P' to row index
                    col = int(grid_position[1:]) - 1  # Convert '1'-'24' to column index
                    mini_item = self.mini_grid.item(row, col)
                    if mini_item:
                        mini_item.setBackground(color)
                except (ValueError, IndexError):
                    print(f"Invalid position format: {position}")



    def update_sample_log(self):
        # Clear the sample log to start fresh
        self.sample_log.clear()

        # Loop through each sample group and add a formatted HTML entry
        for group in self.sample_groups:
            color_hex = group["color"].name()  # Get hex color for the group
            positions_str = ", ".join(group["positions"])  # Join positions as a string
            
            # HTML entry with line break for each group and correct color
            html_entry = (
                f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
                f'<span style="background-color: {color_hex}; width: 12px; height: 12px; '
                f'display: inline-block; border-radius: 2px; margin-right: 6px;"></span>'
                f'<b>{group["name"]}</b>: {positions_str}</div><br>'
            )

            # Insert the formatted HTML entry into the log
            self.sample_log.insertHtml(html_entry)
            
    def clear_all(self):
        # Clear input fields
        self.file_prefix_input.clear()
        self.sample_name_input.clear()
        self.injection_volume_input.clear()
        self.instrument_method_input.clear()

        # Reset checkbox states
        self.same_inj_vol_checkbox.setChecked(False)
        self.same_instrument_method_checkbox.setChecked(False)

        # Clear selected positions, sample groups, and cell-to-group mapping
        self.selected_positions.clear()
        self.sample_groups.clear()
        self.cell_to_group.clear()

        # Clear sample log and sample information table
        self.sample_log.clear()
        self.sample_info_table.setRowCount(0)

        # Reset color index to start fresh colors for new groups
        self.current_color_index = 0

        # Reinitialize the mini grid and main grid to remove existing colors and reset for new selections
        self.create_plate_grid()

        
    def update_sample_info_table(self):
        # Clear the sample info table to prepare for fresh data
        self.sample_info_table.setRowCount(0)

        # Populate the sample info table with each sample group's data
        for group in self.sample_groups:
            row_position = self.sample_info_table.rowCount()
            self.sample_info_table.insertRow(row_position)

            # Sample Name cell with color background
            sample_item = QTableWidgetItem(group["name"])
            sample_item.setBackground(group["color"])
            self.sample_info_table.setItem(row_position, 0, sample_item)

            # Injection Volume cell
            inj_vol_item = QTableWidgetItem(f"{group['inj_vol']} µL")
            self.sample_info_table.setItem(row_position, 1, inj_vol_item)

            # Instrument Method cell
            instrument_method_item = QTableWidgetItem(group.get("instrument_method", "N/A"))
            self.sample_info_table.setItem(row_position, 2, instrument_method_item)

            # Path cell
            path_item = QTableWidgetItem(group.get("path", "N/A"))
            self.sample_info_table.setItem(row_position, 3, path_item)

            

    def select_range(self, start_cell, end_cell):
        start_row, start_col = start_cell
        end_row, end_col = end_cell
        top_row = min(start_row, end_row)
        bottom_row = max(start_row, end_row)
        left_col = min(start_col, end_col)
        right_col = max(start_col, end_col)

        selection_range = QTableWidgetSelectionRange(top_row, left_col, bottom_row, right_col)
        self.table.setRangeSelected(selection_range, True)

        # Add selected positions to the list
        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                item = self.table.item(row, col)
                if item and item.text() not in self.selected_positions:
                    self.selected_positions.append(item.text())
    
    def browse_instrument_method(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Instrument Method")
        if file_path:
            self.instrument_method_input.setText(file_path)
            
            
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Path")  # Corrected line
        if path:
            self.path_input.setText(path)


                    
    def add_samples(self):
        # Get prefix, sample name, injection volume, and instrument method
        file_prefix = self.file_prefix_input.text().strip()
        sample_name = self.sample_name_input.text().strip()
        inj_vol = self.injection_volume_input.text().strip()
        instrument_method = self.instrument_method_input.text().strip()  # Get specified instrument method
        path = self.path_input.text().strip()  # Include path input

        if not sample_name or not inj_vol:
            return  # Skip if no sample name or injection volume is provided

        # Combine prefix and sample name
        full_name = f"{file_prefix}_{sample_name}" if file_prefix else sample_name

        # Get the current color for this sample group
        color = self.colors[self.current_color_index % len(self.colors)]
        self.current_color_index += 1

        # Format positions
        tray_color_prefix = self.tray_color_combo.currentText()[0].upper() + ":"
        formatted_positions = [f"{tray_color_prefix}{pos}" for pos in self.selected_positions]

        # Store the sample group with injection volume, instrument method, and path
        new_group = {
            "name": full_name,
            "positions": formatted_positions,
            "color": color,
            "inj_vol": inj_vol,
            "instrument_method": instrument_method,  # Store instrument method
            "path": path  # Store path
        }
        self.sample_groups.append(new_group)

        # Update UI elements
        self.update_sample_log()
        self.update_sample_info_table()
        self.update_mini_grid()  # Ensure colors are shown in mini grid
        self.selected_positions.clear()
        self.sample_name_input.clear()

        # Clear the instrument method input if the "Use same method" checkbox is not checked
        if not self.same_instrument_method_checkbox.isChecked():
            self.instrument_method_input.clear()


    def generate_queue(self):
        # Prepare data dictionary for columns and data rows
        data = {
            "File Name": [],
            "Position": [],
            "Inj Vol": [],
            "Instrument Method": [],
            "Path": []
        }
        for group in self.sample_groups:
            method_to_use = group.get("instrument_method", self.instrument_method_input.text().strip())
            path_to_use = group.get("path", self.path_input.text().strip())
            
            for position in group["positions"]:
                data["File Name"].append(group["name"])
                data["Position"].append(position)
                data["Inj Vol"].append(group.get("inj_vol", ""))
                data["Instrument Method"].append(method_to_use)
                data["Path"].append(path_to_use)

        # Create DataFrame for data rows
        df = pd.DataFrame(data)

        # Specify the file path
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Queue", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='') as f:
                # Write the custom header row
                f.write("Bracket Type=4\n")
                # Append the actual DataFrame data
                df.to_csv(f, index=False)
            
            print(f"Queue saved to {file_path}")


    def generate_colors(self, n):
        # Generate n visually distinct colors without transparency for clarity in logs
        colors = []
        for i in range(n):
            r = 128 + (i * 73) % 128  # Keep R value in the upper half of the range
            g = 128 + (i * 97) % 128  # Keep G value in the upper half
            b = 128 + (i * 53) % 128  # Keep B value in the upper half
            colors.append(QColor(r, g, b))  # Opaque colors without transparency
        return colors


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlateSelector()
    window.show()
    sys.exit(app.exec_())
