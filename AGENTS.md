# ClearEditor — AGENTS.md

## Quick start

```bash
pip install PyQt5          # only dependency — no requirements.txt
python3 main.py            # launch editor
```

**⚠️ В системе нет `python`, только `python3`.** Все команды выполнять через `python3`.

**Requires `config.json` in cwd** (raises `ConfigError` if missing). `settings.ini` is auto-created by QSettings and gitignored (`*.ini`).

## Project structure

**Architecture pattern:** Model-View-Service (MVS).
- `core/models/` — pure Python data classes, no Qt dependency
- `core/views/` — Qt widgets (UI only)
- `core/services/` — QObject subclasses (business logic, signals)
- `plugins_service/` follows the same MVS layout
- `core/editor_app.py` — orchestrator / composition root

## Project structure

| Path | Role |
|---|---|
| `main.py` | Entrypoint — bootstraps EditorApp, PluginManager, menu bar |
| `core/editor_app.py` | `QMainWindow` — splitter with FileTabView + MsgPanel, status bar |
| `core/models/` | Data models (Document, FileTabModel, etc.) — pure Python, no Qt |
| `core/views/` | UI widgets (FileTabView, EditorWidget, HtmlEditorWidget, etc.) |
| `core/services/` | Business logic (FileTabSrv, etc.) — QObject with signals |
| `core/msg_panel.py` | `QTabWidget` with Err/Msg tabs + `ErrorHandler` (redirects stderr) |
| `plugins_service/` | Plugin manager, base class, and enable/disable dialog (models/services/views subpackages) |
| `plugins/` | Plugin packages — each folder has `manifest.json` + entry script |

## Plugins

Each plugin is a directory under `plugins/` containing a `manifest.json`:

```json
{"name": "...", "description": "...", "entry": "main.py", "class": "PluginClassName"}
```

Activation state is persisted in `settings.ini` (QSettings key `active_plugins`). Dialog at **Settings > Plugins**.

Built-in plugins: `wordcount` (status-bar word counter), `textprocessing` (Text menu: remove empty lines, capitalize first letters).

## Tests

**No test framework.** Model tests run with assertions and print pass/fail. Visual tests use standalone PyQt windows.

```bash
python3 tests/test_document.py         # Document model — auto-assert (needs display)
python3 tests/test_file_tab_model.py   # FileTabModel — auto-assert (pure Python, no Qt)
python3 tests/test_file_tab_srv.py     # FileTabSrv — visual test window
```
Run from project root: `PYTHONPATH=. python3 tests/…`

## Key conventions

- **Window icon**: `icons/clear.svg`. Test scripts may reference `icons/clear_test.jpg` or `icons/clear1.jpg`.
- **Recent files**: capped at 10, persisted via QSettings.
- **Config `config.json`**: must contain at least `{"plugins_dir": "plugins"}`.
- **`docs/spec/`**: Актуальные спецификации сервисов (ConfigService и др.); `docs/spec/plugins/` — только спеки плагинов; `docs/spec/ver1.0/` — архив устаревших (до рефакторинга).
- All imports use the repo-root package layout (e.g. `from core.editor_app import EditorApp`).
- Язык переговоров и отчётов по умолчанию — русский.
- Комментарии в коде писать на английском.

## Session status

Состояние сессии сохраняется в `docs/session_status.md`. Чтобы быстро восстановить контекст в новой сессии — скажите **"восстанови статус"** или **"что делали"**.

Короткая команда для просмотра:
```bash
./scripts/status.sh          # показать статус
./scripts/status.sh edit     # открыть в редакторе
```

## Git workflow

Пользователь часто забывает коммитить. Напоминать делать коммит когда:
- накопилось 3+ изменённых файла
- перед шагом, который может сломать работающий код
- после любого завершённого этапа рефакторинга
