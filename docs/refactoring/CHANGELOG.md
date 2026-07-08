# Changelog

## v3.0 — MVS Maturity + DI (2026-07-08)

- **MessageSrv extraction:** `MsgPanel` monolith → `MessageModel` + `MessageSrv` + `MsgPanelView` + `ErrorHandler`
- **PluginManager decomposition:** monolith → `PluginRegistry` (model) + `PluginLoader` (service) + `PluginUI` (view) + facade
- **EditorApp slimmed:** extracted `ConfigService`, `ThemeService` (ex-ZoomService)
- **HTMLEditor:** extracted `TagCompletionsModel` for autocompletion data
- **main.py restructured:** DI assembly, section headers, renamed plugin vars
- **iclear plugin:** migrated from `tab_panel` API to `file_tab_srv.editor_state_changed`
- **Specifications:** `ConfigService`, `MessageSrv`, `iclear`, `HTMLProcessing` — dedicated spec files
- **Tests:** 11 ConfigService tests, MessageSrv tests, PluginLoader tests, PluginRegistry tests
- **Session status** tracking added (`docs/session_status.md`, `scripts/status.sh`)
- **AGENTS.md:** added project conventions, test commands, session workflow

> Диаграммы: [`docs/UML/class_diagram_v3.mmd`](UML/class_diagram_v3.mmd) (v3.0) · [`docs/UML/class_diagram_v2.mmd`](UML/class_diagram_v2.mmd) (v2.0) · [`docs/UML/architecture_overview.md`](UML/architecture_overview.md)

---

## v2.0 — MVS Architecture (2026-07-02)

- **MVS restructuring:** split flat `core/` into `core/models/`, `core/views/`, `core/services/`
- **Removed** `ver1.0/` legacy code, stale docs, executed plan files
- **Added** standalone model tests for `Document`, `FileTabModel`, `FileTabSrv`
- **Updated** all imports project-wide, dropped old `core/tab_panel` references
- **Removed** old `test_file_edit.py`, `test_tab_panel.py`, `test_msg_panel.py`

> Диаграммы: [`docs/UML/class_diagram_v2.mmd`](UML/class_diagram_v2.mmd) (v2.0) · [`docs/UML/architecture_overview.md`](UML/architecture_overview.md)

### v2.0-rc — pre-MVS refactorings

- **Plugin system refactored:** actions/index_actions, nested menus with kind/content, toolbar reuse
- **EditorApp:** menu creation moved from main.py to EditorApp
- **HTMLProcessing** plugin added
- **iClear** plugin added
- **Plugins:** TextProcessing extended with HTML operations
- **Specifications:** restructured into `en/` and `ru/` locales
- **Added:** `pyproject.toml`, `AGENTS.md`, `requirements.txt`

---

## v1.0 — Monolithic (2026-06 — 2026-07)

- Initial implementation — flat `core/` structure
- Monolithic `QMainWindow` with all logic in one place
- Basic tabbed editor with HTML highlighting
- Plugin system without service layer
- Early test scripts for manual visual inspection

> Диаграммы: [`docs/UML/class_diagram_v1.mmd`](UML/class_diagram_v1.mmd) (v1.0)

---

## How to explore history

```bash
git checkout v1.0   # old architecture (pre-MVS)
git checkout v2.0   # MVS architecture
git checkout v3.0   # MVS + DI + decomposed services
git log v1.0..v2.0  # all changes between versions
git log v2.0..v3.0  # all changes v2.0 → v3.0
```
