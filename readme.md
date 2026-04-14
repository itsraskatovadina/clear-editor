# MultiDoc Editor

A multi-tab, cross-platform text editor built with Python and PyQt5. It allows you to open, edit, and save multiple text files simultaneously, as well as track external changes.

![PyQt5](https://img.shields.io/badge/PyQt5-5.15-blue)
![Python](https://img.shields.io/badge/Python-3.6+-green)

## Features

- **Tabbed Interface**: Open and manage multiple documents in separate tabs.
- **File Operations**:
  - Create new files (`Ctrl+N`)
  - Open existing text files (`Ctrl+O`)
  - Save current file (`Ctrl+S`)
  - Save current file with a new name (`Ctrl+Shift+S`)
- **Document Status**:
  - Visual indicator (`*`) in the tab title for unsaved changes.
  - Full file path displayed in the tab tooltip.
- **External Modification Detection**: Warns if a file opened in the editor has been modified by another program.
- **Recent Files List**: Remembers the last 10 opened files for quick access.
- **Session Persistence**: Saves and restores window position, size, and the recent files list between sessions.
- **Status Bar**: Shows brief status messages (e.g., "Saved filename.txt").

## Prerequisites

- **Python 3.6** or higher.
- **PyQt5** library.

## Installation

1.  **Clone the repository** (or download the `cleanmain.py` file directly):
    ```bash
    git clone https://github.com/itsraskatovadina/cleanmain.git
    cd cleanmain
