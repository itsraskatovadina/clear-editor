# FileTabSrv — таблица вызовов методов

| Метод | Вызывает / создаёт | Откуда вызывается |
|---|---|---|
| **`__init__`** | `FileTabModel()`, <br>подключает сигналы `_view.close_requested → _on_close_requested`, <br>`_view.current_changed → _on_current_changed`, <br>`_view.tab_moved → _on_tab_moved` | `EditorApp.__init__`, <br>тесты (`test_file_tab_srv.py`, `test_editor_app.py`) |
| **`_create_widget(document)`** | создаёт `EditorWidget(parent=_view, editor_class=...)`, <br>подключает `ew.modification_changed → _on_modification_changed(document)`, <br>`ew.cursor_position_changed → editor_line_changed` | `add_tab` |
| **`new_tab()`** | `add_tab(None)` | `EditorApp` — меню File>New, `set_tab_panel` (когда нет файлов сессии); <br>тесты |
| **`activate_tab(path)`** | `_model.index_of(path)`, `_model.at(i)`, <br>`_view.setCurrentIndex(i)`, `_model.set_current(i)`, <br>`message.emit(...)`, `editor_state_changed.emit(...)` | `add_tab` |
| **`add_tab(path)`** | `activate_tab(path)`, `_check_path_exists(path)`, <br>`_model.add(path)`, `_create_widget(doc)`, `doc.bind(ew.document())`, <br>`_load_file(doc, ew)`, `_view.add_editor_tab(ew, title, tooltip)`, <br>`_view.setCurrentIndex(index)`, `_model.set_current(index)`, <br>`editor_state_changed.emit(...)` | `new_tab`, `open_file`, `set_files`, <br>`EditorApp.action_open_recent_file`; <br>тесты |
| **`_load_file(doc, ew)`** | `doc.load()`, `ew.set_text(...)`, <br>`message.emit(...)` при ошибке | `add_tab`, `_reload_tab` |
| **`_check_path_exists(path)`** | `path.exists()`, `message.emit(...)` | `add_tab`, `_save_tab`, `_reload_tab`, <br>`view_property_tab`, `_check_external_modified` |
| **`close_tab(index, close_last_tab)`** | `_view.editor_at(index)`, `_model.at(index)`, <br>`doc.is_externally_modified()`, `QMessageBox.question(...)`, <br>`_save_tab(index)`, `_remove_tab(index)` | `_on_close_requested`, `close_all_tab`, <br>`current_tab_process("close")`; <br>тесты |
| **`_remove_tab(index)`** | `_model.remove(index)`, `_view.remove_editor_tab(index)` | `close_tab` |
| **`close_all_tab()`** | `_model.count`, `_view.setCurrentIndex(i)`, `close_tab(i, True)` | `closeEvent` |
| **`closeEvent(event)`** | `close_all_tab()`, `event.accept()` / `event.ignore()` | `EditorApp.closeEvent` |
| **`current_tab_process(action)`** | `current_widget()`, `_view.currentIndex()`, <br>→ `_save_tab` / `_save_as_tab` / `close_tab` / `_reload_tab` / `view_property_tab` | `EditorApp` — меню File (Save/Save As/Close/Reload/Property) через lambda; <br>тесты |
| **`view_property_tab(index)`** | `_model.at(index)`, `_check_path_exists(doc.file_path)`, <br>`QMessageBox.information(...)` | `current_tab_process("property")` |
| **`_save_tab(index)`** | `_model.at(index)`, `_check_path_exists(doc.file_path)`, <br>`_save_as_tab(index)` (если нет пути), <br>`doc.save()`, `_view.set_tab(index, title, full_title)`, <br>`editor_state_changed.emit(...)`, `message.emit(...)` при ошибке | `current_tab_process("save")`, `close_tab`, <br>`_check_external_modified` |
| **`_save_as_tab(index)`** | `QFileDialog.getSaveFileName(...)`, `Path(file_path)`, <br>`_model.at(index)`, `doc.save_as(path)`, <br>`_view.set_tab(index, title, full_title)`, <br>`editor_state_changed.emit(...)`, `message.emit(...)` при ошибке | `current_tab_process("save_as")`, `_save_tab` |
| **`_reload_tab(index)`** | `_model.at(index)`, `_check_path_exists(doc.file_path)`, <br>`_view.editor_at(index)`, `ew.text_cursor()`, <br>`_load_file(doc, ew)`, `ew.set_text_cursor(cursor)`, <br>`_view.set_tab(index, title, full_title)`, <br>`editor_state_changed.emit(...)` | `current_tab_process("reload")`, <br>`_check_external_modified` |
| **`open_file()`** | `QFileDialog.getOpenFileName(...)`, `Path(file_path)`, `add_tab(Path(...))` | `EditorApp` — меню File>Open; <br>тесты |
| **`get_open_files()`** | `_model.all_docs()` | `EditorApp.closeEvent` |
| **`set_files(file_list)`** | `Path(path_str)`, `path.exists()`, `add_tab(path)` | `EditorApp.set_tab_panel` |
| **`_on_close_requested(index)`** | `close_tab(index)` | сигнал `_view.close_requested` (нажатие крестика на вкладке) |
| **`_on_tab_moved(from, to)`** | `_model.move_doc(from, to)`, <br>`_model.set_current(_view.currentIndex())` | сигнал `_view.tab_moved` (перетаскивание вкладки) |
| **`_on_current_changed(index)`** | `_view.editor_at(index)`, `ew.set_focus()`, <br>`_model.set_current(index)`, `_model.at(index)`, <br>`editor_state_changed.emit(...)` | сигнал `_view.current_changed` (переключение вкладки) |
| **`_on_modification_changed(doc)`** | `_model.index_of_doc(doc)`, `_view.set_tab(...)`, <br>`editor_state_changed.emit(...)` | сигнал `ew.modification_changed` (изменение текста) |
| **`current_editor()`** | `current_widget()`, `widget.editor` | `EditorApp.current_editor`, <br>плагины: `wordcount`, `htmlprocessing`, `textprocessing` |
| **`current_widget()`** | `_view.currentIndex()`, `_view.editor_at(index)` | `current_tab_process`, `current_editor` |
| **`current_document()`** | `_model.current()` | `EditorApp.current_file_name`, <br>плагины: `wordcount`, `iclear`; <br>тесты |
| **`tab_count()`** | `_model.count` | `EditorApp.set_tab_panel`, <br>плагин `wordcount`; <br>тесты |
| **`widget_at(index)`** | `_model.count`, `_view.editor_at(index)` | плагин `wordcount` |
| **`on_app_focus_changed(old, now)`** | `_view.currentIndex()`, `_model.at(index)`, <br>`isinstance(now, _editor_class)`, `_check_external_modified(index)` | `EditorApp.on_app_focus_changed` |
| **`_check_external_modified(index)`** | `_model.at(index)`, `_check_path_exists(doc.file_path)`, <br>`doc.is_externally_modified()`, `QMessageBox(...)`, <br>→ `_save_tab` / `_reload_tab` / `doc.last_file_mtime = now` | `on_app_focus_changed` |
