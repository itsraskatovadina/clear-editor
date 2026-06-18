# ClearEditor — AGENTS.md

## Quick start

```bash
pip install PyQt5          # only dependency — no requirements.txt
python main.py             # launch editor
```

**Requires `config.json` in cwd** (raises `ConfigError` if missing). `settings.ini` is auto-created by QSettings and gitignored (`*.ini`).

## Project structure

| Path | Role |
|---|---|
| `main.py` | Entrypoint — bootstraps EditorApp, PluginManager, menu bar |
| `core/editor_app.py` | `QMainWindow` — splitter with TabPanel + MsgPanel, status bar |
| `core/tab_panel.py` | `QTabWidget` — manages FileEditor tabs |
| `core/file_editor.py` | Wraps a `QTextEdit` in a tab — load/save/modified/external-change detection |
| `core/ext_editor.py` | `QTextEdit` subclass — HTML syntax highlighting + tag auto-completion |
| `core/msg_panel.py` | `QTabWidget` with Err/Msg tabs + `ErrorHandler` (redirects stderr) |
| `plugins_service/` | Plugin manager, base class, and enable/disable dialog |
| `plugins/` | Plugin packages — each folder has `manifest.json` + entry script |

## Plugins

Each plugin is a directory under `plugins/` containing a `manifest.json`:

```json
{"name": "...", "description": "...", "entry": "main.py", "class": "PluginClassName"}
```

Activation state is persisted in `settings.ini` (QSettings key `active_plugins`). Dialog at **Settings > Plugins**.

Built-in plugins: `wordcount` (status-bar word counter), `textprocessing` (Text menu: remove empty lines, capitalize first letters).

## Tests

**No test framework.** Test scripts are standalone PyQt `QApplication` windows launched for manual visual inspection:

```bash
python tests/test_file_edit.py
python tests/test_tab_panel.py
python tests/test_msg_panel.py
```

Each opens a window — verify behaviour by interacting with the UI. No automated test runner, no lint/typecheck config in the repo.

## Key conventions

- **Window icon**: `icons/clear.svg`. Test scripts may reference `icons/clear_test.jpg` or `icons/clear1.jpg`.
- **Recent files**: capped at 10, persisted via QSettings.
- **Config `config.json`**: must contain at least `{"plugins_dir": "plugins"}`.
- **readme.md** contains stale references (outdated repo name `cleanmain`, file name `cleanmain.py`).
- **`specifications/`**: Russian-language requirement specs — descriptive, not executable.
- All imports use the repo-root package layout (e.g. `from core.editor_app import EditorApp`).
