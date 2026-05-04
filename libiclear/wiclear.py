#! /usr/bin/python3

from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QDialog, QMessageBox,
	QPushButton, QTextEdit, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout,
	QInputDialog, QDialogButtonBox, QMenu, QAction, QFrame, QStyle)
from PyQt5.QtCore import QCoreApplication, QSettings, QSize, QPoint, Qt
from PyQt5.QtGui import QFont, QIcon
from pathlib import Path
import os

class WinNode(QWidget):   
	def __init__(self, parent, level):
		QWidget.__init__(self, parent)
		self.parent = parent
		
		self.txt	= QLabel(level)
		self.lst	= QComboBox()
		self.fill_list()
		
		self.lst.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
		self.lst.setMinimumContentsLength(8)  
		hbox = QHBoxLayout()
		hbox.addWidget(self.txt)
		hbox.addWidget(self.lst)
		self.setLayout(hbox)
		
		self.lst.currentIndexChanged["int"].connect(self.on_changed_list)
			
	def fill_list(self):
		""" заполняем или перезаполняем список выбора """
		self.lst.clear()

		level = self.txt.text()
		prev_level = iclib.Iclear.prev_level(level)
		#prev_level_node = getattr(self.parent.nodefilter, prev_level)
		prev_level_node = self.parent.nodnav.get_node(prev_level)
		#print(level, prev_level_node)
		""" если nodefilter.node на предидущем уровне заполнен
		 (для site (top) предидущий уровень host (site) и он всегда заполнен ???)  
			тогда формируем список для выбора + пустое значение """
		if prev_level_node:
			self.lst.addItem("")
			self.lst.setCurrentIndex(0)
			for child in prev_level_node.children:
				self.lst.addItem(child.nid)
			""" если nodefilter.node на соответствующем уровне заполнен   
			тогда устанавливаем его значение в списке"""
			if self.parent.nodnav.get_node(level):
				self.lst.setCurrentText(str(self.parent.nodnav.get_node(level)))
		
	def on_changed_list(self, index):
		"""  при изменении текущего индекса списка
			1 - изменяем self.parent.nodefilter.set_node(level) 
			2 - изменяем список выбора на следующем уровне (если он есть)"""
		level = self.txt.text()
		prev_level = iclib.Iclear.prev_level(level)
		next_level = iclib.Iclear.next_level(level)
		
		node = None
		if index > 0:
			nodenid = self.lst.itemText(index)
			prev_level_node = self.parent.nodnav.get_node(prev_level)
			node = prev_level_node.get_child(nodenid)
			
		self.parent.set_nodnav(level, node)	 
		
		if next_level:
			win_next_level = getattr(self.parent, "w" + next_level)
			win_next_level.fill_list()

class IclearInputDialog(QDialog):
	
	def __init__(self, parent=None, hostpath = '', sitepath = ''):
		super(IclearInputDialog, self).__init__(parent)
		
		self.setWindowTitle("Iclear settings")
		self.setModal(True)
		#self.resize(QSize(500, 270))
		self.label1 = QLabel("apache sites dir")
		self.line_edit1 = QLineEdit(hostpath)
		self.label2 = QLabel("additional path")
		self.line_edit2 = QLineEdit(sitepath)
		self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		layout = QVBoxLayout(self)

		layout.addWidget(self.label1)
		layout.addWidget(self.line_edit1)

		layout.addWidget(self.label2)
		layout.addWidget(self.line_edit2)

		layout.addWidget(self.button_box)
		
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)
		
	def get_values(self):
		"""Возвращает кортеж из двух строковых значений"""
		return (self.line_edit1.text(), self.line_edit2.text())

class WinNodesNav(QFrame):
	"""  виджет для отображения и выбора экземпляра класса NodeNav 
		состав - одно невидимое поле host и видимые поля(site, top, man, cat, page),
		 каждое из которых подчинено предидущему
		доп функция - перезаполнение по кнопке ↺ и ввод по ссылке кнопка ... """
	
	def __init__(self, nodnav, parent=None):
		QFrame.__init__(self, parent)
		
		self.parent = parent
		self.nodnav = nodnav

		self.setFrameStyle(QFrame.Box | QFrame.Plain)
		self.setObjectName('navself')
		self.setStyleSheet("QFrame#navself {border: 1px solid #C0C0C0;}")
		 
		self.txt_nodnav	= QLabel(str(self.nodnav))
		#self.txt_nodnav.setFrameStyle(QFrame.NoFrame)
		
		hboxLay = QHBoxLayout()
		hboxLay.setContentsMargins(0,0,0,0)
		self.wsite = WinNode(parent = self, level = "site")
		hboxLay.addWidget(self.wsite)
		self.wtop = WinNode(parent = self, level = "top")
		hboxLay.addWidget(self.wtop)
		self.wman = WinNode(parent = self, level = "man")
		hboxLay.addWidget(self.wman)
		self.wcat = WinNode(parent = self, level = "cat")
		hboxLay.addWidget(self.wcat)
		self.wpage = WinNode(parent = self, level = "page")
		hboxLay.addWidget(self.wpage)		
		
		self.btnURL = QPushButton(parent=self)
		self.btnURL.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.btnURL.setFixedWidth(32)
		self.btnURL.setToolTip("URL")
		self.btnURL.clicked.connect(self.fill_from_url)
		hboxLay.addWidget(self.btnURL)
		
		self.btnMenu = QPushButton("...")
		self.btnMenu.setStyleSheet("QPushButton::menu-indicator { image: url(noimg) }")
		self.btnMenu.setFixedWidth(36)
		menu = QMenu('menu')
		
		xdgOpenAction = QAction('xdg_open', self)
		xdgOpenAction.triggered.connect(self.xdg_open)
		menu.addAction(xdgOpenAction)
		
		refilAction = QAction('refilling', self)
		refilAction.triggered.connect(self.refill)
		menu.addAction(refilAction)
		
		genIndexAction = QAction('gen_index_and_phpinc', self)
		#genIndexAction.triggered.connect(self.refill)
		menu.addAction(genIndexAction)
		
		genPlugAction = QAction('gen_plug_pagephp', self)
		#genPlugAction.triggered.connect(self.refill)
		menu.addAction(genPlugAction)
		
		checkMapAction = QAction('check_map', self)
		#checkMapAction.triggered.connect(self.refill)
		menu.addAction(checkMapAction)
		
		genViewAction = QAction('gen_view', self)
		#genViewAction.triggered.connect(self.refill)
		menu.addAction(genViewAction)

		
		self.btnMenu.setMenu(menu)
		hboxLay.addWidget(self.btnMenu)

		'''
		self.btnOpen = QPushButton(parent=self)  
		self.btnOpen.setToolTip("Open")
		self.btnOpen.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.btnOpen.clicked.connect(self.open_page)
		hboxLay.addWidget(self.btnOpen)
		'''
		hboxLay.addStretch()
		self.setLayout(hboxLay)

		#self.setFrameStyle(QFrame.Box)
		
	def render_txt_nodnav(self):
		self.txt_nodnav.setText(str(self.nodnav))
		
	def set_nodnav(self, level, node):
		self.nodnav.set_node(level, node)
		self.render_txt_nodnav()

	def open_page(self):	
		path = self.nodnav.page.full_path()
		self.parent.tab_panel.add_tab(Path(path))
		#print(path)
		
	def refill(self):
		#self.render_txt_nodnav()
		self.wsite.lst.blockSignals(True)
		self.wtop.lst.blockSignals(True)
		self.wman.lst.blockSignals(True)
		self.wcat.lst.blockSignals(True)
		self.wpage.lst.blockSignals(True)
		
		self.wsite.fill_list()
		self.wtop.fill_list()
		self.wman.fill_list()
		self.wcat.fill_list()
		self.wpage.fill_list()
		
		self.wsite.lst.blockSignals(False)
		self.wtop.lst.blockSignals(False)
		self.wman.lst.blockSignals(False)
		self.wcat.lst.blockSignals(False)
		self.wpage.lst.blockSignals(False)
		
	def fill_from_map(self):
		""" перезаполняем nodnav (когда меняется map) """
		""" сохраняем nodnav в виде словаря """
		nodedict = self.nodnav.get_dict()
		self.nodnav.host.refill(fill_sites = True, fill_mans = True)
		self.nodnav.set_dict(nodedict)
		self.refill()
		
	def fill_from_url(self):
		""" перезаполняем nodefilter с адресной строки страницы """
		inputDialog = QInputDialog(self)
		inputDialog.resize(QSize(700, 270))
		inputDialog.setWindowTitle("url")
		inputDialog.setLabelText("Введите адрес страницы")
		inputDialog.setTextValue(self.nodnav.get_url())
		inputDialog.setInputMode(0)
		ok = inputDialog.exec_()
		pagelink = inputDialog.textValue()
		"""
		pagelink, ok = inputDialog.getText(self, "url",
		"Введите url адрес страницы", text=self.nodefilter.gen_link())"""
		
		if ok:
			self.nodnav.set_from_url(pagelink)
			self.refill()
			
	def xdg_open(self, page_path):
		if 	self.nodnav.page: 
			full_path = self.nodnav.page.full_path()
			os.system("xdg-open "+full_path)
		elif self.nodnav.cat: 
			full_path = self.nodnav.cat.full_path()
			os.system("xdg-open "+full_path)
		elif self.nodnav.man: 
			full_path = self.nodnav.man.full_path()
			os.system("xdg-open "+full_path)
		else: 
			full_path = self.nodnav.site.full_path()
			os.system("xdg-open "+full_path)
			
	def fill_from_page_path(self, page_path):
		self.nodnav.set_from_page_path(page_path)
		self.refill()
		
	
class WMain(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		host = iclib.IHost("iclear", "/home/user/www/", sitepath = "iclear")
		host.fill(fill_sites = True, fill_mans = True)
		nodnav = iclib.NodesNav(host = host, nodestr = nodestr)
 
		self.win = WinNodesNav(nodnav, parent=self)
			
		mainBox = QVBoxLayout()
		mainBox.addWidget(self.win)
		self.setLayout(mainBox)	
		
if __name__ == "__main__":
	
	import sys
	import iclear as iclib
	
	app = QApplication(sys.argv)
		
	window = WMain()							 
	window.resize(400, 100)
	window.setFont(QFont('SansSerif', 14))
	window.show()										 
	sys.exit(app.exec_()) 		

else:
	import libiclear.iclear as iclib
	
