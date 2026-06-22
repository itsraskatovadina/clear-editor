# ClearEditor

A multi-tab text editor built with Python and PyQt5. Open, edit, and save multiple files simultaneously with HTML syntax highlighting, tag auto-completion, and a plugin system.

![PyQt5](https://img.shields.io/badge/PyQt5-5.15-blue)
![Python](https://img.shields.io/badge/Python-3.6+-green)

## Features

- **Tabbed interface** with drag-movable tabs
- **HTML syntax highlighting** and tag auto-completion (`<p>`, `<div>`, `<a>`, etc.)
- **Plugin system** — built-in word counter and text processing
- **External modification detection** — warns when a file changed outside the editor
- **Session persistence** — restores open files, window geometry, and recent files on restart
- **Zoom In / Zoom Out** — global font size adjustment
- **Message panel** — stderr capture and message logging

## Quick start

```bash
pip install PyQt5
python main.py
```

Requires `config.json` in the working directory:

```json
{"plugins_dir": "plugins"}
```

## Project layout

| Directory | Contents |
|---|---|
| `core/` | Main window, tab panel, file editor, message panel |
| `plugins/` | Plugin packages (`manifest.json` + entry script) |
| `plugins_service/` | Plugin manager, base class, enable/disable dialog |
| `tests/` | Manual visual test scripts |
| `specifications/` | Russian-language requirement specs |
| `icons/` | Application icons |

## Plugins

Enable/disable at **Settings > Plugins**. Built-in plugins:

- **wordcount** — shows word count in the status bar
- **textprocessing** — adds a Text menu with "Remove empty lines" and "Capitalize first letters"

## Tests

Tests are standalone PyQt windows for manual visual inspection:

```bash
python tests/test_file_edit.py
python tests/test_tab_panel.py
python tests/test_msg_panel.py
```
