```mermaid
graph TD
    subgraph Qt
        QTabWidget[QTabWidget]
        QWidget[QWidget]
        QTextEdit[QTextEdit]
        QObject[QObject]
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

    FileTabView -->|extends| QTabWidget
    EditorWidget -->|extends| QWidget
    EditorWidget -->|contains| QTextEdit

    FileTabModel -->|composes *| Document

    FileTabSrv -->|extends| QObject
    FileTabSrv -->|composes| FileTabModel
    FileTabSrv -->|composes *| EditorWidget
    FileTabSrv ..->|uses| FileTabView
```

**Пояснение стрелок:**
- `extends` — наследование от Qt-класса
- `composes` — композиция (создаёт и владеет объектом)
- `composes *` — композиция со списком (1 ко многим)
- `uses` — получает ссылку через параметр конструктора
