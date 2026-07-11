## Goal
- Update `docs/spec/config_service_spec.txt` to reflect current code, add validation for `plugins_dir` and `ui_defaults`, and write tests for ConfigService.

## Progress
### Done
- Analysed discrepancies between `state_spec.txt` and current code (ConfigService extracted, PluginManager signature changed, spec missing ConfigError and validation).
- Proposed spec name: `docs/spec/config_service_spec.txt`.
- Documented validation conditions for `plugins_dir` (exists, valid path) and `ui_defaults` (dict with geometry/pos and geometry/size as 2‑int lists).
- Outlined test scenarios: missing/broken config.json, validation of plugins_dir/ui_defaults, settings.ini defaults, open/recent files persistence.
- Wrote initial report to `report.txt`.
- Created `docs/spec/config_service_spec.txt` with full spec + test plan.
- Added `validate()`, `_validate_plugins_dir()`, `_validate_ui_defaults()` to `core/services/config_service.py`.
- Created `tests/services/test_config_service.py` with 11 passing tests.

### In Progress
- (none)

### Blocked
- (none)

## Key Decisions
1. **Validation approach**: variant A (msg_panel message + continue without plugins) preferred over variant B (ConfigError → app exit). Reason: user sees the error but app still starts.
2. **Spec location**: `docs/spec/config_service_spec.txt` (NOT in plugins/ — that folder is only for plugin-related specs).
3. **Test isolation**: use `tempfile.TemporaryDirectory` for config.json; no QApplication needed.
4. **Missing ui_defaults**: not an error — validate() returns no errors if the key is absent entirely.

## Next Steps
(ask user)
