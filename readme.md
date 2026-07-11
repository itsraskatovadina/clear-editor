# ClearEditor

Многостраничный текстовый редактор с поддержкой вкладок, подсветкой синтаксиса HTML, системой плагинов и отслеживанием внешних изменений файлов.

---

## О проекте

**ClearEditor** — учебный проект, демонстрирующий эволюцию архитектуры ПО от монолита (v1.0) к MVS + DI (v3.0).

Разработан на **Python** + **PyQt5**.

---

## Возможности

- Вкладки — открывайте, редактируйте и сохраняйте несколько файлов
- Система плагинов — wordcount, textprocessing, iclear, htmltools
- Сохранение сессии — восстановление open/recent файлов, геометрии окна
- Панель сообщений — перехват stderr + handled-ошибки (Err/Msg/View)
- Подсветка синтаксиса HTML и автодополнение тегов
- Отслеживание внешних изменений

---

## Быстрый старт

```bash
pip install PyQt5
python3 main.py
```

Требуется `config.json` в рабочей директории:

```json
{"plugins_dir": "plugins"}
```

---

## Архитектура (MVS)

**Model-View-Service** — упрощённый аналог MVC:

- **Model** (`core/models/`) — данные, без Qt, тестируются без GUI
- **View** (`core/views/`) — Qt виджеты, только отображение
- **Service** (`core/services/`) — QObject, бизнес-логика, соединяет Model и View через сигналы

```
main.py → EditorApp (QMainWindow-оркестратор)
           ├── FileTabView + FileTabSrv + FileTabModel
           ├── MsgPanelView + MessageSrv
           ├── ConfigService / ThemeService
           └── PluginManager → Registry + Loader + UI
```

Диаграммы: [class_diagram_v3.mmd](docs/UML/class_diagram_v3.mmd) ·
[architecture_overview.md](docs/UML/architecture_overview.md)

---

## Структура проекта

| Директория | Содержание |
|------------|-----------|
| `core/models/` | Модели данных (Document, FileTabModel, MessageModel, TagCompletionsModel) |
| `core/views/` | Qt-виджеты (FileTabView, EditorWidget, MsgPanelView, HTMLEditor) |
| `core/services/` | Сервисы (FileTabSrv, MessageSrv, ConfigService, ThemeService) |
| `plugins/` | Плагины (wordcount, textprocessing, iclear, htmltools) |
| `plugins_service/` | Система плагинов (Registry, Loader, UI) |
| `tests/` | Модульные и интеграционные тесты |
| `docs/` | Документация, спецификации, планы рефакторинга |

---

## Плагины

Включить/отключить: **Настройки → Плагины**.

- **wordcount** — счётчик слов в статус-баре
- **textprocessing** — меню "Текст": удалить пустые строки, capitalize first
- **iclear** — навигатор по файловой структуре PHP-сайта
- **htmltools** — валидация HTML, генерация оглавления

---

## Тестирование

```bash
python3 tests/models/test_document.py
python3 tests/models/test_file_tab_model.py
python3 tests/models/test_message_model.py
python3 tests/services/test_config_service.py
python3 tests/services/test_message_srv.py
```

Модельные тесты — auto-assert (без Qt), сервисные — визуальные (требуют QApplication).

---

## Версии

| Версия | Описание |
|--------|----------|
| v1.0 | Монолитная архитектура |
| v2.0 | MVS-разделение core/ на models/views/services/ |
| v3.0 | Декомпозиция сервисов, DI, новые спецификации |

История: [CHANGELOG](docs/refactoring/CHANGELOG.md) ·
Сводка рефакторинга: [refactoring_summary](docs/refactoring/refactoring_summary.md)
