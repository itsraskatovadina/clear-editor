```mermaid
graph TD
    subgraph core_services ["core/services"]
        ConfigService[ConfigService]
        ConfigError[ConfigError]
    end

    subgraph core ["core"]
        EditorApp[EditorApp]
    end

    subgraph Qt
        QSettings[QSettings]
    end

    subgraph external ["config files"]
        config_json["config.json"]
        settings_ini["settings.ini"]
    end

    ConfigService -->|reads| config_json
    ConfigService -->|reads/writes via| QSettings
    QSettings -->|backed by| settings_ini

    EditorApp ..->|injected / creates| ConfigService
    EditorApp -->|delegates load/save to| ConfigService
```

**Пояснение:**
- `ConfigService` — plain class, не Qt
- `ConfigError` — исключение (наследует `Exception`)
- `injected / creates` — EditorApp получает ConfigService через конструктор либо создаёт сам
- `delegates` — EditorApp вызывает `load_config()`, `restore_settings()`, `closeEvent()` → ConfigService
