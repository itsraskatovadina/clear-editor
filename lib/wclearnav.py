#! /usr/bin/python3

from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QInputDialog, QMessageBox,
	QPushButton, QTextEdit, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QFrame, QStyle)
from PyQt5.QtCore import QCoreApplication, QSettings, QSize, QPoint, Qt
from PyQt5.QtGui import QFont, QIcon
from pathlib import Path

class WinNode(QWidget):   
	def __init__(self, parent, lvl):
		QWidget.__init__(self, parent)
		self.parent = parent
		
		self.txt	= QLabel(lvl)
		self.lst	= QComboBox()
		self.fill_list()
		
		self.lst.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
		self.lst.setMinimumContentsLength(8)  # 10
		hbox = QHBoxLayout()
		hbox.addWidget(self.txt)
		hbox.addWidget(self.lst)
		self.setLayout(hbox)
		
		self.lst.currentIndexChanged["int"].connect(self.on_changed_list)
			
	def fill_list(self):
		""" заполняем или перезаполняем список выбора """
		self.lst.clear()

		lvl = self.txt.text()
		prev_lvl = iclib.NodeLevels.prev_lvl(lvl)
		#prev_lvl_node = getattr(self.parent.nodefilter, prev_lvl)
		prev_lvl_node = self.parent.nodnav.get_node(prev_lvl)
		#print(lvl, prev_lvl_node)
		""" если nodefilter.node на предидущем уровне заполнен
		 (для top предидущий уровень site и он всегда заполнен)  
			тогда формируем список для выбора + пустое значение """
		if prev_lvl_node:
			self.lst.addItem("")
			self.lst.setCurrentIndex(0)
			for subnode in prev_lvl_node.subnodes:
				self.lst.addItem(subnode.nid)
			""" если nodefilter.node на соответствующем уровне заполнен   
			тогда устанавливаем его значение в списке"""
			if self.parent.nodnav.get_node(lvl):
				self.lst.setCurrentText(str(self.parent.nodnav.get_node(lvl)))
		
	def on_changed_list(self, index):
		"""  при изменении текущего индекса списка
			1 - изменяем self.parent.nodefilter.set_node(lvl) 
			2 - изменяем список выбора на следующем уровне (если он есть)"""
		lvl = self.txt.text()
		prev_lvl = iclib.NodeLevels.prev_lvl(lvl)
		next_lvl = iclib.NodeLevels.next_lvl(lvl)
		
		node = None
		if index > 0:
			nodenid = self.lst.itemText(index)
			prev_lvl_node = self.parent.nodnav.get_node(prev_lvl)
			node = prev_lvl_node.get_child_node(nodenid)
			
		self.parent.set_nodnav(lvl, node)	 
		
		if next_lvl:
			win_next_lvl = getattr(self.parent, "w" + next_lvl)
			win_next_lvl.fill_list()

class LinkInputDialog(QInputDialog):
	
	def __init__(self, parent=None):
		QInputDialog.__init__(self, parent)
		self.resize(QSize(500, 270))
		self.setInputMode(0)

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
		self.wsite = WinNode(parent = self, lvl = "site")
		hboxLay.addWidget(self.wsite)
		self.wtop = WinNode(parent = self, lvl = "top")
		hboxLay.addWidget(self.wtop)
		self.wman = WinNode(parent = self, lvl = "man")
		hboxLay.addWidget(self.wman)
		self.wcat = WinNode(parent = self, lvl = "cat")
		hboxLay.addWidget(self.wcat)
		self.wpage = WinNode(parent = self, lvl = "page")
		hboxLay.addWidget(self.wpage)		
		
		#self.btnRefill = QPushButton("↺")
		#self.btnRefill.clicked.connect(self.refill)
		#hboxLay.addWidget(self.btnRefill)
		
		self.btnFillFromLink = QPushButton("...")
		self.btnFillFromLink.setToolTip("HTTP адрес страницы")
		self.btnFillFromLink.clicked.connect(self.fill_from_link)
		hboxLay.addWidget(self.btnFillFromLink)
		
		self.btnOpen = QPushButton(parent=self)  
		self.btnOpen.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.btnOpen.clicked.connect(self.open_page)
		hboxLay.addWidget(self.btnOpen)
		
		hboxLay.addStretch()
		
		mainBox = QVBoxLayout()
		mainBox.addWidget(self.txt_nodnav)
		#mainBox.addLayout(hboxLay)
		mainBox.addStretch()
		
		self.setLayout(hboxLay)

		#self.setFrameStyle(QFrame.Box)
		
	def render_txt_nodnav(self):
		self.txt_nodnav.setText(str(self.nodnav))
		
	def set_nodnav(self, lvl, node):
		self.nodnav.set_node(lvl, node)
		self.render_txt_nodnav()

	def open_page(self):	
		path = self.nodnav.page.full_path()
		self.parent.tab_panel.add_tab(Path(path))
		#print(path)
		
	def refill(self):	
		""" перезаполняем nodefilter (когда меняется map) """
		""" сохраняем nodefilter в виде словаря """
		dict_filter = self.nodefilter.get_dict_filter()
		#print(dict_filter)
		""" перезаполняем site """
		site = iclib.Site(nid = "conspect", name="IT Сonspect")
		""" пытаемся восстановить nodefilter"""
		self.nodefilter = site.gen_node_filter_from_dict(dict_filter)
		#self.nodefilter = site.gen_node_filter_from_dict(dict_filter={'top': "web", 'man': "html", "cat": "intro", "page": ""})
		
		self.render_txt_nodnav()
		self.wtop.lst.blockSignals(True)
		self.wtop.fill_list()
		self.wtop.lst.blockSignals(False)
		# остальные должны перезаполнится автоматически
		
	def fill_from_link(self):
		""" перезаполняем nodefilter с адресной строки страницы """
		
		inputDialog = QInputDialog(self)
		inputDialog.resize(QSize(700, 270))
		inputDialog.setWindowTitle("url")
		inputDialog.setLabelText("Введите адрес страницы")
		inputDialog.setTextValue(self.nodnav.gen_link())
		inputDialog.setInputMode(0)
		ok = inputDialog.exec_()
		pagelink = inputDialog.textValue()
		"""
		pagelink, ok = inputDialog.getText(self, "url",
		"Введите url адрес страницы", text=self.nodefilter.gen_link())"""
		
		if ok:
			self.nodnav.gen_from_link(pagelink)
				
			self.render_txt_nodnav()
			
			self.wtop.lst.blockSignals(True)
			self.wman.lst.blockSignals(True)
			self.wcat.lst.blockSignals(True)
			self.wpage.lst.blockSignals(True)
			
			self.wtop.fill_list()
			self.wman.fill_list()
			self.wcat.fill_list()
			self.wpage.fill_list()
			
			self.wtop.lst.blockSignals(False)
			self.wman.lst.blockSignals(False)
			self.wcat.lst.blockSignals(False)
			self.wpage.lst.blockSignals(False)
	
class WMain(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		host = iclib.Host("iclear")	
		nodnav = iclib.NodesNav(host = host)
		self.win = WinNodesNav(nodnav)
			
		mainBox = QVBoxLayout()
		mainBox.addWidget(self.win)
		self.setLayout(mainBox)	
		
if __name__ == "__main__":
	
	import sys
	import iclear as iclib
	
	app = QApplication(sys.argv)
		
	window = WMain()	
	window.setWindowTitle("WinFilter")
	window.setWindowIcon(QIcon('../icons/filtr.ico'))							 
	window.resize(400, 100)
	window.setFont(QFont('SansSerif', 14))
	window.show()										 
	sys.exit(app.exec_()) 		

else:
	import lib.iclear as iclib
	
