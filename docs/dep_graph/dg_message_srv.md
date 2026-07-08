```mermaid
graph TD
    subgraph Qt
        QObject[QObject]
        QTabWidget[QTabWidget]
    end

    subgraph core_models ["core/models"]
        Message[Message]
    end

    subgraph core_services ["core/services"]
        MessageSrv[MessageSrv]
        ErrorHandler[ErrorHandler]
    end

    subgraph core_views ["core/views"]
        MsgPanelView[MsgPanelView]
    end

    subgraph core ["core"]
        EditorApp[EditorApp]
        FileTabSrv[FileTabSrv]
    end

    MessageSrv -->|extends| QObject
    ErrorHandler -->|wraps stderr| sys.stderr
    MsgPanelView -->|extends| QTabWidget

    MessageSrv -->|creates / formats| Message
    MessageSrv -.->|display_error →| MsgPanelView
    MessageSrv -.->|display_message →| MsgPanelView

    EditorApp -->|composes| MessageSrv
    EditorApp -->|composes| MsgPanelView
    EditorApp -->|connects| FileTabSrv
    FileTabSrv -.->|message →| MessageSrv
    FileTabSrv -.->|editor_state_changed →| EditorApp
```

**Пояснение:**
- `extends` — наследование от Qt
- `creates / formats` — MessageSrv создаёт Message, форматирует в HTML
- `display_error/display_message →` — сигналы, connected к MsgPanelView
- `composes` — EditorApp создаёт и владеет (`self.msg_srv`, `self.msg_panel`)
- `message →` — FileTabSrv.message сигнал → MessageSrv.post_message
