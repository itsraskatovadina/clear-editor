# Сводка рефакторинга v1.0 → v3.0

## Контекст

Рефакторинг основного приложения ClearEditor, начатый после v1.0 (плоская монолитная структура)
и завершённый к v3.0 (MVS + DI + декомпозиция сервисов).

## Этапы рефакторинга

### Этап 0: TabPanel + FileEditor → FileTabView + FileTabSrv + FileTabModel + EditorWidget

Самый первый и самый крупный шаг — расщепление монолита `TabPanel` (наследник QTabWidget, ~250 строк)
на MVS-триаду:

| Было | Стало |
|------|-------|
| `TabPanel` (QTabWidget + всё) | `FileTabView` (UI) + `FileTabSrv` (логика) + `FileTabModel` (данные) |
| `FileEditor` (QWidget + Document) | `EditorWidget` (view) + `Document` (model) |
| логика вкладок и редактора в одном классе | FileTabSrv управляет вкладками, EditorWidget — только отображение |

**Ключевые изменения:**
- FileTabModel — чистый Python, тестируемый
- FileTabSrv — QObject с сигналами editor_state_changed, message, line_changed
- EditorWidget — тонкая обёртка над HTMLEditor

### Этап 1: MessageSrv (MsgPanel → MessageSrv + MsgPanelView + MessageModel)

**Проблема:** MsgPanel смешивал UI (QTabWidget) с логикой маршрутизации и ErrorHandler.

**Решение:**
- `MessageModel` (dataclass) — чистая модель сообщения
- `MessageSrv` (QObject) — логика: post_message/post_error, форматирование HTML, beep
- `MsgPanelView` (QTabWidget) — только три QTextEdit (Err/Msg/View)
- `ErrorHandler` — переехал в message_srv.py

**Сигналы:** file_tab_srv.message → msg_srv.post_message → display_error/display_message → msg_panel.append_*

### Этап 2: PluginManager → Registry + Loader + UI

**Проблема:** PluginManager (232 строки) смешивал хранение, загрузку и генерацию UI.

**Решение:**
- `PluginRegistry` (model, pure Python) — хранение available/active/active_ui
- `PluginLoader` (service, QObject) — discover, load, deactivate с сигналами
- `PluginUI` (view, QObject) — build_menu/toolbar/dock/status
- `PluginManager` — фасад, сохраняет обратную совместимость

**Дополнительно:**
- Новый формат декларации UI: actions (dict) + menu_items/toolbar_items (ref by id)
- Поиск меню по тексту (find_menu_by_text) — решает дублирование подменю
- `PluginWidget` принимает registry вместо списка

### Этап 3: EditorApp — вынос Config/Session/Zoom

**Проблема:** EditorApp (~160 строк своих + делегирование) удерживал 3 ответственности.

**Решение:**
- `ConfigService` — config.json + QSettings (geometry, font, recent_files, open_files)
- `ThemeService` (бывший ZoomService) — zoom_in/zoom_out/set_font_size
- EditorApp делегирует ConfigService в load_config/restore_settings/closeEvent

**Валидация:**
- `_validate_plugins_dir()` — проверка наличия и типа plugins_dir
- `_validate_ui_defaults()` — проверка geometry/pos и geometry/size, удаление повреждённых ключей
- Ошибки ui_defaults → msg_panel (warning), ошибки plugins_dir → ConfigError

### Этап 4: HTMLEditor → TagCompletionsModel

- Из HTMLEditor вынесен список тегов/атрибутов в `TagCompletionsModel`
- Модель чистая, без Qt
- HTMLEditor получает модель через композицию

### Этап 5: iclear — переход на FileTabSrv API

- `editor.tab_panel` → `editor.file_tab_srv`
- `tab_panel.tab_added` → `file_tab_srv.editor_state_changed`
- `tab_panel.currentChanged` → `file_tab_srv.editor_state_changed`
- `tab_panel.add_tab(path)` → `file_tab_srv.add_tab(path)` (через колбэк)
- `tab_panel.widget(index).path` → `file_tab_srv.current_document().file_path`

### Этап 6: main.py — реструктуризация

- Добавлены секционные комментарии (# --- Config ---, # --- Plugin system --- и т.д.)
- DI-сборка: registry/loader/ui создаются перед PluginManager
- Активные плагины загружаются после discover
- ErrorHandler/excepthook устанавливаются после load_config

## Структура проекта (целевая, v3.0)

```
clear_editor/
├── main.py                     # bootstrap + DI
├── core/
│   ├── editor_app.py           # QMainWindow-оркестратор
│   ├── models/
│   │   ├── document.py
│   │   ├── file_tab_models.py
│   │   ├── message_model.py
│   │   └── html_editor_model.py
│   ├── views/
│   │   ├── file_tab_view.py
│   │   ├── editor_widget.py
│   │   ├── html_editor_widget.py
│   │   └── msg_panel_view.py
│   └── services/
│       ├── file_tab_srv.py
│       ├── message_srv.py
│       ├── config_service.py
│       └── theme_service.py
├── plugins_service/
│   ├── plugin_base.py
│   ├── plugin_manager.py       # facade
│   ├── models/
│   │   └── plugin_registry.py
│   ├── services/
│   │   └── plugin_loader.py
│   └── views/
│       ├── plugin_ui.py
│       └── plugin_widget.py
├── plugins/                    # wordcount, textprocessing, iclear, htmlprocessing
├── tests/                      # model/service tests
├── docs/
│   ├── refactoring/            # итоговые документы
│   ├── UML/                    # диаграммы
│   ├── spec/                   # спецификации
│   └── ...
└── icons/
```

## Итог

| Метрика | v1.0 | v2.0 | v3.0 |
|---------|------|------|------|
| core/ файлов | 8 (плоская) | 12 (3 пакета) | 15 (3 пакета) |
| Моделей (pure Python) | 0 | 2 | 5 |
| Сервисов (QObject) | 0 | 1 | 5 |
| Тестов (assert) | 0 | 2 файла | 7 файлов |
| Спецификаций | 0 | 0 | 4+ |
