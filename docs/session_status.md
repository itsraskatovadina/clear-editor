# Session Status

**Дата:** 2026-07-05
**Этап:** EditorApp — вынос Config/Zoom сервисов — **сделано, не закоммичено**

## Общий прогресс

| Этап | Статус |
|------|--------|
| MsgPanel → MessageSrv + MsgPanelView + MessageModel | ✅ закоммичено |
| HTMLEditor → TagCompletionsModel | ✅ закоммичено |
| PluginManager → Registry + Loader + UI | ✅ закоммичено |
| EditorApp → ConfigService + ZoomService | ✅ сделано, **не закоммичено** |
| iclear → FileTabSrv API | ⏸️ отложено |

## Что сделано за последние сессии

### PluginManager (шаги 1-7) — закоммичено
- `plugins_service/models/plugin_registry.py` — чистая модель
- `plugins_service/services/plugin_loader.py` — загрузчик, сигналы
- `plugins_service/views/plugin_ui.py` — генерация UI (формат Вариант B)
- `plugins_service/plugin_manager.py` — фасад
- `plugins_service/plugin_widget.py` — принимает registry
- `main.py` — DI-сборка

### MessageSrv — закоммичено
- `core/services/message_srv.py` — beep на error/warning, цвет warning `#cc8400`
- `core/models/message_model.py` — dataclass Message

### HTMLEditor → TagCompletionsModel — закоммичено
- `core/models/html_editor_model.py` — TagCompletionsModel (pure Python)
- `core/views/html_editor_widget.py` — использует модель
- `tests/models/test_html_editor_model.py` — 6 тестов

### EditorApp — ConfigService + ZoomService — **НЕ закоммичено**
- `core/services/config_service.py` — загрузка config.json, QSettings, геометрия/шрифт/recent/open
- `core/services/zoom_service.py` — zoom_in/zoom_out для target QWidget
- `core/editor_app.py` — делегирует ConfigService и ZoomService

### Инфраструктура — закоммичено
- `plan_plug_manager.txt` → `docs/plan_plug_manager.txt`
- `plan_editor_app.txt` → `docs/plan_editor_app.txt`

## Текущее состояние (working tree)

```
 M core/editor_app.py              ← изменён, делегирует ConfigService/ZoomService
?? core/services/config_service.py ← новый, не добавлен в git
?? core/services/zoom_service.py   ← новый, не добавлен в git
```

## Известные проблемы

1. **`editor_app.py:set_tab_panel` — дублирование (некритично)**
   - новая версия (стр. 94) и старая (стр. 162) обе сработают одинаково
   - старая читает QSettings напрямую — работает, т.к. ConfigService оборачивает тот же QSettings
   - новый код ConfigService-restore_open_files() — мёртвый, переопределён старым
   - **Не баг рантайма**, а незавершённый рефакторинг: удалить старый вариант

## Документы

| Файл | Описание |
|------|----------|
| `docs/master_plan.txt` | Общий план рефакторинга (Rec 1-8) |
| `docs/plan_plug_manager.txt` | План рефакторинга PluginManager |
| `docs/plan_editor_app.txt` | План рефакторинга EditorApp + предложение по iclear |
| `docs/todo.txt` | Хотелки по плагинам (wrap, шаблоны, rename HTMLProcessing) |

## Планы на следующий раз

1. Закоммитить EditorApp (удалить старый `set_tab_panel` сначала)
2. Рефакторинг iclear plugin на FileTabSrv API
3. Межплагинная связь: iclear → htmlprocessing.validate_html
