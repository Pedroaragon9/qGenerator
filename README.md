# QGenerator

**QGenerator** is a GUI-based tool developed in Python, designed to help users select specific sample locations on a 96- or 384-well plate and generate an output CSV file compatible with Xcalibur MS acquisition. It allows for detailed sample selection, file naming conventions, and the inclusion of experimental conditions for mass spectrometry.

## Features

- **Plate Selection**: Supports 96-well and 384-well formats with visual selection.
- **Sample Grouping**: Allows grouping of samples by color-coded sets with custom injection volumes and instrument methods.
- **CSV Output**: Generates an Xcalibur-compatible CSV file, populated with details such as Sample Type, Filename, Path, Instrument Method, Position, and Injection Volume.
- **Viewer Options**: Separate viewer windows for sample overviews and plate layouts.
- **Cross-Platform**: Available for both macOS and Windows.

## Installation

### Requirements

- Python 3.10 or newer
- Required libraries: `qtpy`, `pandas`, `pyinstaller` (for building executables)

### Running the Application

If you prefer not to build from source, you can download the prebuilt binaries:

1. Download the appropriate binary file for your operating system:
   - **Windows**: `QGenerator.exe`
   - **macOS**: `QGenerator.app`

2. Place the executable in a desired folder and run it directly.

If you wish to build the application yourself, follow the steps below.

### Building from Source

To run the application from source or make adjustments:

1. Clone the repository:
   ```bash
   git clone https://github.com/Pedroaragon9/qGenerator.git
   cd qGenerator