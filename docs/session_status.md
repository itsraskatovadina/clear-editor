# Session Status

**Дата:** 2026-07-06
**Этап:** Master plan — **приостановлен**. Доработка main / EditorApp / сервисов.

## Общий прогресс

| Этап | Статус |
|------|--------|
| MsgPanel → MessageSrv + MsgPanelView + MessageModel | ✅ закоммичено |
| HTMLEditor → TagCompletionsModel | ✅ закоммичено |
| PluginManager → Registry + Loader + UI | ✅ закоммичено |
| EditorApp → ConfigService + ZoomService | ✅ закоммичено |
| iclear → FileTabSrv API | ⏸️ отложено |
| Доработка main / EditorApp / сервисов | 🔄 текущая задача |

## Текущая задача

Доработать main.py, EditorApp и сервисы Config/Zoom по списку из docs/plan_plugins.txt → раздел 5:

1. ~~**ZoomService → ThemeService** — переименован ✅, API расширен, DI в main~~
2. **load_config** разбить на `load_config` (только config.json) + `restore_settings` (QSettings — геометрия, шрифт, recent)
3. **main.py** — блок redirect uncaught errors перенести сразу перед `set_tab_panel()`
4. **main.py** — добавить комментарии `# --- ... ---` для визуальной структуры
5. **main.py** — блок загрузки активных плагинов поместить перед `def open_plugin_settings()`
6. **main.py** — `registry/loader/ui` → `plugin_registry/plugin_loader/plugin_ui`
7. **EditorApp** — `create_status_bar()` вынести из `__init__`

## Текущее состояние (working tree)

Рабочий каталог чистый. Все изменения закоммичены.

## Документы

| Файл | Описание |
|------|----------|
| `docs/master_plan.txt` | Общий план рефакторинга (Rec 1-8) — приостановлен |
| `docs/plan_plug_manager.txt` | План рефакторинга PluginManager (выполнен) |
| `docs/plan_editor_app.txt` | План рефакторинга EditorApp |
| `docs/plan_plugins.txt` | Сводный план по плагинам — приостановлен |
| `docs/todo.txt` | Хотелки и текущие задачи |
