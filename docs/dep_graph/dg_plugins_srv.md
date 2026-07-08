```mermaid
graph TD
    PluginManager[PluginManager] -->|extends| QObject
    PluginLoader[PluginLoader] -->|extends| QObject
    PluginUI[PluginUI] -->|extends| QObject
    PluginWidget[PluginWidget] -->|extends| QDialog
    EditorApp[EditorApp] -->|extends| QMainWindow

    PluginManager -->|uses| PluginRegistry
    PluginManager -->|uses| PluginLoader
    PluginManager -->|uses| PluginUI
    PluginManager ..->|injected via parent| EditorApp

    PluginLoader -->|registers into| PluginRegistry
    PluginUI -->|reads/writes via| PluginRegistry
    PluginWidget -->|reads| PluginRegistry

    EditorApp -->|holds reference| PluginManager
```

**Пояснение:**
- `extends` — наследование от Qt
- `uses` — получает через конструктор и вызывает методы
- `injected via parent` — PluginManager.parent() == EditorApp
- `registers into / reads` — читает/пишет данные регистрации
- `holds reference` — `editor_app.plugin_manager = plugin_manager`
