#! /usr/bin/env python3

from pathlib import Path
from typing import Optional, List
import datetime


class Document:
    """Один открытый документ — данные + ссылка на QTextDocument."""

    def __init__(self, file_path: Optional[Path] = None, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self.last_file_mtime = datetime.datetime.now()
        self._qdoc = None

    def bind(self, qdoc):
        self._qdoc = qdoc

    @property
    def title(self) -> str:
        return self.file_path.name if self.file_path else "untitled"

    @property
    def full_title(self) -> str:
        return str(self.file_path) if self.file_path else "untitled"

    @property
    def modified(self) -> bool:
        return self._qdoc.isModified() if self._qdoc else False

    @modified.setter
    def modified(self, flag: bool):
        if self._qdoc:
            self._qdoc.setModified(flag)

    @property
    def content(self) -> str:
        return self._qdoc.toPlainText() if self._qdoc else ""

    def load(self):
        text = self.file_path.read_text(encoding=self.encoding)
        self.last_file_mtime = datetime.datetime.now()
        return text

    def save(self):
        self.file_path.write_text(self.content, encoding=self.encoding)
        self.last_file_mtime = datetime.datetime.now()
        self.modified = False

    def save_as(self, path: Path):
        self.file_path = path
        self.save()

    def is_externally_modified(self) -> bool:
        if self.file_path is None or not self.file_path.exists():
            return False
        stat = self.file_path.stat()
        file_mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        return self.last_file_mtime < file_mtime


class FileTabModel:
    """Состояние всех открытых документов."""

    def __init__(self):
        self._documents: List[Document] = []
        self._current_index: int = -1

    def current(self) -> Optional[Document]:
        if 0 <= self._current_index < len(self._documents):
            return self._documents[self._current_index]
        return None

    def at(self, index: int) -> Optional[Document]:
        if 0 <= index < len(self._documents):
            return self._documents[index]
        return None

    def add(self, path: Optional[Path] = None) -> Document:
        doc = Document(file_path=path)
        self._documents.append(doc)
        return doc

    def remove(self, index: int) -> bool:
        if 0 <= index < len(self._documents):
            self._documents.pop(index)
            if self._current_index >= len(self._documents):
                self._current_index = len(self._documents) - 1
            return True
        return False

    def set_current(self, index: int):
        if 0 <= index < len(self._documents):
            self._current_index = index

    @property
    def count(self) -> int:
        return len(self._documents)

    @property
    def current_index(self) -> int:
        return self._current_index

    def index_of(self, path: Path) -> int:
        for i, d in enumerate(self._documents):
            if d.file_path == path:
                return i
        return -1

    def index_of_doc(self, doc: Document) -> int:
        try:
            return self._documents.index(doc)
        except ValueError:
            return -1

    def all_docs(self) -> List[Document]:
        return list(self._documents)

    def move_doc(self, from_idx: int, to_idx: int):
        doc = self._documents.pop(from_idx)
        self._documents.insert(to_idx, doc)
