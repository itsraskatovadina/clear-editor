#! /usr/bin/env python3

import datetime
import os
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextEdit

from core.models.file_tab_models import FileTabModel
from core.views.editor_widget import EditorWidget


class FileTabSrv(QObject):
    message = pyqtSignal(str, str, str)
    editor_state_changed = pyqtSignal(str, str, str, str)
    editor_line_changed = pyqtSignal(int)

    def __init__(self, view, editor_class=QTextEdit, parent=None):
        super().__init__(parent)
        self._view = view
        self._editor_class = editor_class
        self._model = FileTabModel()
        self._programmatic_change = False
        self._focus_check_disabled = False

        self._view.close_requested.connect(self._on_close_requested)
        self._view.current_changed.connect(self._on_current_changed)
        self._view.tab_moved.connect(self._on_tab_moved)

    def _create_widget(self, document):
        ew = EditorWidget(parent=self._view, editor_class=self._editor_class)
        ew.modification_changed.connect(lambda: self._on_modification_changed(document))
        ew.cursor_position_changed.connect(self.editor_line_changed)
        return ew

    # --- tab management ---

    def new_tab(self):
        self.add_tab(None)

    def activate_tab(self, path):
        i = self._model.index_of(path)
        if i >= 0:
            doc = self._model.at(i)
            self._programmatic_change = True
            self._view.setCurrentIndex(i)
            self._programmatic_change = False
            self._model.set_current(i)
            fname = str(path)
            self.message.emit(
                f"file {fname} already open", "FileTabSrv", "info"
            )
            mod_label = "*" if doc.modified else ""
            self.editor_state_changed.emit(
                path.name, fname, mod_label, "Reopened"
            )
            return True
        return False

    def add_tab(self, path=None):
        if path:
            if self.activate_tab(path):
                return True
            if not self._check_path_exists(path):
                return False

        doc = self._model.add(path)
        ew = self._create_widget(doc)
        doc.bind(ew.document())

        if path is not None:
            if not self._load_file(doc, ew):
                return False
            operation = "Opened"
        else:
            operation = "New"

        self._programmatic_change = True
        index = self._view.add_editor_tab(ew, doc.title, doc.full_title)
        self._view.setCurrentIndex(index)
        self._programmatic_change = False
        self._model.set_current(index)

        self.editor_state_changed.emit(doc.title, doc.full_title, "", operation)
        return True

    def _load_file(self, doc, ew):
        try:
            ew.set_text(doc.load())
            return True
        except Exception as err:
            self.message.emit(str(err), "FileTabSrv", "error")
            return False

    def _check_path_exists(self, path):
        if not path.exists():
            self.message.emit(
                "There is no such file or directory", "FileTabSrv", "warning"
            )
            return False
        return True

    # --- close ---

    def close_tab(self, index, close_last_tab=False):
        if not close_last_tab and self._model.count <= 1:
            return False
        ew = self._view.editor_at(index)
        doc = self._model.at(index)
        if doc.modified:
            text_question = f'"{doc.title}" has unsaved changes. Do you want to save before closing?'
            if doc.file_path and doc.is_externally_modified():
                text_question += ' <span style="color:red">Attention! The file on the disk is newer than in the editor.</span>'
            reply = QMessageBox.question(
                self._view,
                "Unsaved Changes",
                text_question,
                QMessageBox.Save | QMessageBox.Ignore | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Save:
                if not self._save_tab(index):
                    return False
        self._remove_tab(index)
        return True

    def _remove_tab(self, index):
        self._model.remove(index)
        self._view.remove_editor_tab(index)

    def close_all_tab(self):
        for i in reversed(range(self._model.count)):
            self._view.setCurrentIndex(i)
            if not self.close_tab(i, close_last_tab=True):
                return False
        return True

    def closeEvent(self, event):
        if self.close_all_tab():
            event.accept()
        else:
            event.ignore()

    # --- save / save-as / reload ---

    def current_tab_process(self, action: str):
        index = self._view.currentIndex()
        if index == -1:
            return None
        if action == "save":
            self._save_tab(index)
        elif action == "save_as":
            self._save_as_tab(index)
        elif action == "close":
            self.close_tab(index)
        elif action == "reload":
            self._reload_tab(index)
        elif action == "property":
            self.view_property_tab(index)

    def view_property_tab(self, index):
        doc = self._model.at(index)
        if doc.file_path:
            if not self._check_path_exists(doc.file_path):
                return
            QMessageBox.information(
                self._view,
                "Property",
                str(doc.file_path),
                buttons=QMessageBox.Close,
                defaultButton=QMessageBox.Close,
            )
        else:
            QMessageBox.information(
                self._view,
                "Property",
                "untitled",
                buttons=QMessageBox.Close,
                defaultButton=QMessageBox.Close,
            )

    def _save_tab(self, index):
        doc = self._model.at(index)
        if doc.file_path is None:
            return self._save_as_tab(index)
        if not self._check_path_exists(doc.file_path):
            return False
        try:
            doc.save()
            self._view.set_tab(index, doc.title, doc.full_title)
            self.editor_state_changed.emit(doc.title, doc.full_title, "", "Saved")
            return True
        except Exception as err:
            self.message.emit(str(err), "FileTabSrv", "error")
            return False

    def _save_as_tab(self, index):
        file_path = QFileDialog.getSaveFileName(self._view, "Save As", os.getcwd())[0]
        if not file_path:
            return False
        path = Path(file_path)
        doc = self._model.at(index)
        try:
            doc.save_as(path)
            self._view.set_tab(index, doc.title, doc.full_title)
            self.editor_state_changed.emit(doc.title, doc.full_title, "", "Saved as")
            return True
        except Exception as err:
            self.message.emit(str(err), "FileTabSrv", "error")
            return False

    def _reload_tab(self, index):
        doc = self._model.at(index)
        if doc.file_path is None:
            return False
        if not self._check_path_exists(doc.file_path):
            return False
        ew = self._view.editor_at(index)
        cursor = ew.text_cursor()
        position = cursor.position()
        if self._load_file(doc, ew):
            max_pos = len(doc.content)
            position = min(position, max_pos)
            cursor.setPosition(position)
            ew.set_text_cursor(cursor)
            self._view.set_tab(index, doc.title, doc.full_title)
            self.editor_state_changed.emit(doc.title, doc.full_title, "", "Reload")
            return True
        return False

    # --- open file ---

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self._view, "Open File", "", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return
        self.add_tab(Path(file_path))

    # --- session ---

    def get_open_files(self):
        return [
            str(d.file_path) for d in self._model.all_docs() if d.file_path
        ]

    def set_files(self, file_list):
        opened = 0
        for path_str in file_list:
            path = Path(path_str)
            if path.exists():
                if self.add_tab(path):
                    opened += 1
        return opened

    # --- signals relay ---

    def _on_close_requested(self, index):
        self.close_tab(index)

    def _on_tab_moved(self, from_idx, to_idx):
        if from_idx == to_idx:
            return
        self._model.move_doc(from_idx, to_idx)
        self._model.set_current(self._view.currentIndex())

    def _on_current_changed(self, index):
        if self._programmatic_change:
            return
        ew = self._view.editor_at(index) if index >= 0 else None
        if ew:
            ew.set_focus()
            self._model.set_current(index)
            doc = self._model.at(index)
            if doc:
                mod_label = "*" if doc.modified else ""
                self.editor_state_changed.emit(
                    doc.title, doc.full_title, mod_label, "tab_changed"
                )

    def _on_modification_changed(self, doc):
        index = self._model.index_of_doc(doc)
        if index < 0:
            return
        mod_label = "*" if doc.modified else ""
        self._view.set_tab(index, doc.title + mod_label, doc.full_title)
        self.editor_state_changed.emit(
            doc.title, doc.full_title, mod_label, "modification_changed"
        )

    # --- public API for EditorApp ---

    def current_editor(self):
        widget = self.current_widget()
        return widget.editor if widget else None

    def current_widget(self):
        index = self._view.currentIndex()
        if index == -1:
            return None
        return self._view.editor_at(index)

    def current_document(self):
        return self._model.current()

    def tab_count(self):
        return self._model.count

    def widget_at(self, index):
        if 0 <= index < self._model.count:
            return self._view.editor_at(index)
        return None

    def with_editor(self, index, callback):
        ew = self._view.editor_at(index)
        if ew:
            return callback(ew.editor)
        return None

    # --- external modification check ---

    def on_app_focus_changed(self, old, now):
        index = self._view.currentIndex()
        if index == -1:
            return
        if self._focus_check_disabled:
            return
        doc = self._model.at(index)
        if doc and doc.file_path:
            if now and isinstance(now, self._editor_class):
                self._focus_check_disabled = True
                self._check_external_modified(index)
                self._focus_check_disabled = False

    def _check_external_modified(self, index):
        doc = self._model.at(index)
        if doc.file_path is None:
            return
        if not self._check_path_exists(doc.file_path):
            return
        if doc.is_externally_modified():
            msg_box = QMessageBox(self._view)
            msg_box.setWindowTitle("External modification")
            msg_box.setText(
                "The file on the disk is newer than in the editor. Select the required action:"
            )
            reload_btn = msg_box.addButton("Reload", QMessageBox.ActionRole)
            msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Ignore)
            msg_box.exec_()
            clicked = msg_box.clickedButton()
            if clicked == msg_box.button(QMessageBox.Save):
                self._save_tab(index)
            elif clicked == msg_box.button(QMessageBox.Ignore):
                doc.last_file_mtime = datetime.datetime.now()
            elif clicked == reload_btn:
                self._reload_tab(index)
