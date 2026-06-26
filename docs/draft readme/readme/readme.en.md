# ClearEditor

A multi-tab text editor with HTML syntax highlighting, plugin system, session persistence, and external file change detection.

[🇬🇧 English version](README.en.md) | [🇷🇺 Русская версия](README.md)

---

## 📚 About the Project

**ClearEditor** is an educational project designed to demonstrate software architecture principles in practice. It shows the evolution of code from a simple "monolithic" structure to a clean, testable, and extensible architecture with a dedicated service layer.

Built with **Python** and **PyQt5**, it's intended for:
- learning design patterns
- mastering SOLID principles
- understanding separation of concerns in GUI applications

---

## ✨ Features

- **Tabbed interface** — open, edit, and save multiple files simultaneously
- **HTML syntax highlighting** and tag auto-completion (`<p>`, `<div>`, `<a>`, etc.)
- **Plugin system** — built-in word counter and text processing
- **External modification detection** — warns when a file changed outside the editor
- **Session persistence** — restores open files, window geometry, and recent files on restart
- **Message panel** — stderr capture and message logging

---

## 🚀 Quick Start

### Install dependencies

```bash
pip install PyQt5
```

### Run the application

```bash
python main.py
```

### Configuration

Requires `config.json` in the working directory:

```json
{"plugins_dir": "plugins"}
```

---

## 📁 Project Structure

| Directory | Contents |
|-----------|----------|
| `core/` | Main window, tab panel, file editor, message panel |
| `services/` | Service layer: file operations, sessions, plugins, settings |
| `models/` | Data classes (FileState, SessionState) |
| `plugins/` | Plugins (wordcount, textprocessing, iclear) |
| `plugins_service/` | Plugin manager, base class, enable/disable dialog |
| `tests/` | Automated and manual tests |
| `specifications/` | Technical requirements (Russian) |
| `docs/` | Documentation (architecture, educational plan) |

---

## 🏗️ Architecture

The project follows a **three-layer architecture**:

1. **Presentation Layer (core/)** — GUI components, display only
2. **Business Logic Layer (services/)** — all business logic, PyQt-agnostic
3. **Data Layer (models/)** — simple data objects (dataclass)

Detailed architecture description is available in:
👉 [Architecture Overview](docs/architecture.html)

---

## 🎓 Educational Plan

The project includes a **step-by-step refactoring plan** from "raw" architecture to a clean one. Perfect for:
- self-study
- software architecture courses
- practical refactoring workshops

📖 [Educational Project Plan](docs/educational_project_plan.html)

### Architecture Versions

- **`legacy-architecture`** — initial version with common beginner mistakes
- **`refactored-architecture`** — final version with dedicated service layer
- **`refactoring-plan`** — detailed refactoring roadmap

---

## 🔌 Plugins

Enable/disable plugins at **Settings → Plugins**.

### Built-in Plugins

- **wordcount** — shows word count in the status bar
- **textprocessing** — adds a "Text" menu with operations:
  - Remove empty lines
  - Capitalize first letters
  - HTML formatting

---

## 🧪 Testing

### Automated Tests

```bash
pytest tests/
```

### Manual Tests (visual inspection)

```bash
python tests/test_file_edit.py
python tests/test_tab_panel.py
python tests/test_msg_panel.py
```

---

## 📚 Learning Resources

- [SOLID Principles (with Python examples)](https://realpython.com/solid-principles-python/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
- [Layered Architecture](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)

---

## 🤝 Contributing

The project is open for improvements and enhancements. If you want to:
- add a new plugin
- improve the architecture
- fix a bug

please create an Issue or Pull Request.

---

## 📄 License

This project is created for educational purposes and can be freely used for learning.

---

## ✍️ Author

**itsraskatovadina**

---

## 🌟 Acknowledgments

This project was inspired by the idea of showing beginner developers how software architecture evolves from "just working" code to "correct" and maintainable code.
```

