```mermaid
graph TD
    subgraph Qt
        QMainWindow[QMainWindow]
        QObject[QObject]
        QTabWidget[QTabWidget]
        QWidget[QWidget]
        QTextEdit[QTextEdit]
    end

    subgraph core_models ["core/models"]
        Document[Document]
        FileTabModel[FileTabModel]
    end

    subgraph core_views ["core/views"]
        FileTabView[FileTabView]
        EditorWidget[EditorWidget]
    end

    subgraph core_services ["core/services"]
        FileTabSrv[FileTabSrv]
    end

    EditorApp[EditorApp] -->|extends| QMainWindow
    FileTabSrv -->|extends| QObject
    FileTabView -->|extends| QTabWidget
    EditorWidget -->|extends| QWidget

    FileTabModel -->|composes *| Document

    EditorApp -->|composes| FileTabView
    EditorApp -->|composes| FileTabSrv

    FileTabSrv -->|composes| FileTabModel
    FileTabSrv -->|composes *| EditorWidget
    FileTabSrv ..->|uses _view| FileTabView

    EditorApp -.->|delegates to| FileTabSrv
    EditorApp -.->|connects signals ←| FileTabSrv
```

**Пояснение стрелок:**
- `extends` — наследование от Qt
- `composes` — создаёт и владеет
- `composes *` — список (1 ко многим)
- `uses` — получает через параметр
- `delegates` — делегирует вызовы (меню, фокус)
- `connects signals` — сигнал-слот
