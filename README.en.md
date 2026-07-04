# ClearEditor

A multi-tab text editor with HTML syntax highlighting, plugin system, and external file change tracking.

[🇬🇧 English version](README.en.md) | [🇷🇺 Русская версия](README.md)
---

## 📚 About

**ClearEditor** is an educational project created to demonstrate software architecture principles in practice. It shows the evolution of code from a simple "monolithic" structure to a clean, testable, and extensible architecture with a dedicated service layer.

Built with **Python** and **PyQt5**, it is designed as a simple example for learning development technologies with minimal domain and program logic.

---

## ✨ Features

- **Tabs** — open, edit, and save multiple files simultaneously
- **Plugin system** — built-in plugins: word count, text processing
- **Session persistence** — restores open files, window geometry, and recent files on restart
- **Message panel** — stderr capture and logging
- **HTML syntax highlighting** and tag auto-completion
- **External change detection** — warns when a file was modified outside the editor

---

## 🚀 Quick Start

### Install dependencies

```bash
pip install PyQt5
```

### Launch

```bash
python main.py
```

### Configuration

A `config.json` file is required in the working directory:

```json
{"plugins_dir": "plugins"}
```

---

## 📁 Project structure

The project is currently being refactored; the structure may change.

| Directory | Contents |
|-----------|----------|
| `core/` | Main window, tab panel, file editor, message panel |
| `plugins/` | Plugins (wordcount, textprocessing, iclear) |
| `plugins_service/` | Plugin manager, base class, management dialog |
| `tests/` | Tests |
| `docs/` | Documentation |

---

## 🏗️ Architecture

The project follows a **three-layer architecture**:

1. **Presentation Layer (core/)** — GUI components, display only
2. **Business Logic Layer (services/)** — all business logic, independent of PyQt
3. **Data Layer (models/)** — simple data objects (dataclasses)

Detailed architecture description is available in:
👉 [Project Architecture](docs/architecture.en.html)

---

## 🔌 Plugins

Enable/disable plugins in **Settings → Plugins**.

### Built-in plugins

- **wordcount** — shows word count in the status bar
- **textprocessing** — adds a "Text" menu with operations:
  - Remove empty lines
  - Capitalize first letters

---

## 🧪 Testing

### Automated tests

```bash
pytest tests/
```

---

## 📄 License

This project was created for educational purposes and may be freely used for learning.

---

## ✍️ Author

**itsraskatovadina**

---

## 🌟 Acknowledgments

This project was inspired by the idea of showing beginner developers how software architecture evolves from "just working" code to "proper" maintainable code.
Special thanks to the developers of opencode and deepseek services — this project would not exist without your assistants.
