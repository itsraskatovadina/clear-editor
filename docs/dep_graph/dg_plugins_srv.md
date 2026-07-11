```mermaid
graph TD
    subgraph Qt
        QObject[QObject]
        QDialog[QDialog]
        QMainWindow[QMainWindow]
    end

    subgraph plugins_service_models ["plugins_service/models"]
        PluginRegistry[PluginRegistry]
    end

    subgraph plugins_service_services ["plugins_service/services"]
        PluginLoader[PluginLoader]
    end

    subgraph plugins_service_views ["plugins_service/views"]
        PluginUI[PluginUI]
    end

    subgraph plugins_service ["plugins_service"]
        PluginManager[PluginManager]
        PluginWidget[PluginWidget]
        PluginBase[PluginBase]
    end

    subgraph core_app ["core"]
        EditorApp[EditorApp]
    end

    PluginManager -->|extends| QObject
    PluginLoader -->|extends| QObject
    PluginUI -->|extends| QObject
    PluginWidget -->|extends| QDialog
    EditorApp -->|extends| QMainWindow
    PluginBase -->|extends| QObject

    PluginManager -->|uses| PluginRegistry
    PluginManager -->|uses| PluginLoader
    PluginManager -->|uses| PluginUI
    PluginManager ..->|parent = EditorApp| EditorApp

    PluginLoader -->|registers into| PluginRegistry
    PluginUI -->|reads/writes| PluginRegistry
    PluginWidget -->|reads| PluginRegistry

    PluginLoader -->|instantiates| PluginBase
    PluginUI -->|builds UI for| PluginBase

    EditorApp -->|holds ref to| PluginManager
```

**Пояснение:**
- `extends` — наследование от Qt
- `uses` — получает через конструктор и вызывает методы
- `registers into / reads/writes` — взаимодействует с реестром
- `instantiates` — PluginLoader.load() создаёт экземпляр PluginBase
- `builds UI for` — PluginUI строит UI по конфигурации PluginBase
- `parent` — PluginManager.parent() == EditorApp (QObject parent)
- `holds ref to` — `editor_app.plugin_manager = plugin_manager`
