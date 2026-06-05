#! /usr/bin/python3

# extensions/word_search.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QFileDialog,
    QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from .base_extension import BaseExtension

class WordSearchExtension(BaseExtension):
    """Расширение для поиска слов в тексте"""
    
    word_found = pyqtSignal(str, int)  # слово, позиция
    
    def __init__(self, text_edit=None):
        super().__init__(text_edit)
        self.word_list = []
        self.current_words = []
        self.words_file_path = ""
        
    def get_name(self):
        return "Поиск слов"
    
    def setup_ui(self, layout):
        # Группа настроек
        settings_group = QGroupBox("Настройки")
        settings_layout = QFormLayout()
        
        # Поле для пути к файлу со словами
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Выберите файл со словами...")
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        
        settings_layout.addRow("Файл со словами:", file_layout)
        
        # Кнопка загрузки слов
        self.load_btn = QPushButton("Загрузить слова")
        self.load_btn.clicked.connect(self.load_words)
        settings_layout.addRow("", self.load_btn)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Группа поиска
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout()
        
        # Поле ввода для поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите слово для поиска...")
        self.search_input.returnPressed.connect(self.search_word)
        
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_word)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.search_input)
        input_layout.addWidget(search_btn)
        search_layout.addLayout(input_layout)
        
        # Список найденных слов
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.jump_to_word)
        search_layout.addWidget(QLabel("Найденные слова:"))
        search_layout.addWidget(self.results_list)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Информационная метка
        self.info_label = QLabel("Готов к работе")
        self.info_label.setStyleSheet("color: gray;")
        layout.addWidget(self.info_label)
        
        layout.addStretch()
    
    def browse_file(self):
        """Выбор файла со словами"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Выберите файл со словами",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.words_file_path = file_path
            self.load_words()
    
    def load_words(self):
        """Загрузка слов из файла"""
        file_path = self.file_path_edit.text()
        if not file_path:
            self.info_label.setText("Ошибка: не выбран файл")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.word_list = [line.strip().lower() for line in f if line.strip()]
            
            self.info_label.setText(f"Загружено {len(self.word_list)} слов")
            self.update_search()
            
        except Exception as e:
            self.info_label.setText(f"Ошибка загрузки: {str(e)}")
    
    def search_word(self):
        """Поиск текущего слова в тексте"""
        search_text = self.search_input.text().strip().lower()
        if not search_text or not self.parent_widget:
            return
            
        text = self.parent_widget.toPlainText().lower()
        positions = []
        
        # Поиск всех вхождений
        start = 0
        while True:
            pos = text.find(search_text, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        # Отображение результатов
        self.results_list.clear()
        for pos in positions:
            self.results_list.addItem(f"'{search_text}' на позиции {pos}")
        
        self.info_label.setText(f"Найдено {len(positions)} вхождений")
    
    def update_search(self):
        """Обновление поиска при изменении текста"""
        if self.search_input.text():
            self.search_word()
    
    def jump_to_word(self, item):
        """Переход к позиции слова"""
        if self.parent_widget:
            # Извлечение позиции из текста
            text = item.text()
            pos = int(text.split("позиции ")[1])
            
            # Установка курсора
            cursor = self.parent_widget.textCursor()
            cursor.setPosition(pos)
            self.parent_widget.setTextCursor(cursor)
            self.parent_widget.setFocus()
    
    def apply_settings(self):
        """Применение сохраненных настроек"""
        if 'words_file' in self.settings:
            self.file_path_edit.setText(self.settings['words_file'])
            self.words_file_path = self.settings['words_file']
            self.load_words()
    
    def save_settings(self):
        """Сохранение настроек"""
        self.settings['words_file'] = self.file_path_edit.text()
        return self.settings
