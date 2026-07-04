# Changelog

## v2.0 — MVS Architecture (2026-07-02)

- **MVS restructuring:** split flat `core/` into `core/models/`, `core/views/`, `core/services/`
- **Removed** `ver1.0/` legacy code, stale docs, executed plan files
- **Added** standalone model tests for `Document`, `FileTabModel`, `FileTabSrv`
- **Updated** all imports project-wide, dropped old `core/tab_panel` references
- **Removed** old `test_file_edit.py`, `test_tab_panel.py`, `test_msg_panel.py`

> Диаграммы: [`docs/UML/class_diagram.mmd`](UML/class_diagram.mmd) (v2.0) · [`docs/UML/architecture_overview.md`](UML/architecture_overview.md) (для новичков)

### v2.0-rc — pre-MVS refactorings

- **Plugin system refactored:** actions/index_actions, nested menus with kind/content, toolbar reuse
- **EditorApp:** menu creation moved from main.py to EditorApp
- **HTMLProcessing** plugin added (content list generation, HTML validation)
- **iClear** plugin added (toolbar widget support)
- **Plugins:** TextProcessing extended with HTML operations and toolbar submenu
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
git checkout v2.0   # current architecture
git log v1.0..v2.0  # all changes between versions
```
