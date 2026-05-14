#! /usr/bin/python3

from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QDialog, QMessageBox,
	QPushButton, QTextEdit, QLabel, QLineEdit, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
	QInputDialog, QFileDialog, QDialogButtonBox, QMenu, QAction, QFrame, QStyle)
from PyQt5.QtCore import QCoreApplication, QSettings, QSize, QPoint, Qt, QDir
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
		""" filling in or re-filling the selection list """
		self.lst.clear()

		level = self.txt.text()
		prev_level = iclib.Iclear.prev_level(level)
		prev_level_node = self.parent.nodnav.get_node(prev_level)
		""" if nodnav.node is full at the previous level
		 (there is a pre-existing host level for the site and it is always full)  
			then we form a selection list + an empty value. """
		if prev_level_node:
			self.lst.addItem("")
			self.lst.setCurrentIndex(0)
			for child in prev_level_node.children:
				self.lst.addItem(child.nid)
			""" if nodnav.node is filled at the appropriate level   
			then we set its value in the list.  """
			level_node = self.parent.nodnav.get_node(level)
			if level_node:
				self.lst.setCurrentText(str(level_node))
		
	def on_changed_list(self, index):
		"""  when changing the current index of the list
			1 - change self.parent.nodnav.set_node(level) 
			2 - change the selection list at the next level (if any)"""
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

class WinNodesNav(QWidget):
	"""  widget for displaying and selecting an instance of the NodeNav class 
		composition - one invisible host field and related fields(site, top, man, cat, page) """
	
	def __init__(self, nodnav, parent=None):
		QWidget.__init__(self, parent)
		
		self.parent = parent
		self.nodnav = nodnav
		#self.txt_nodnav	= QLabel(str(self.nodnav))
		
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
		
		#hboxLay.addStretch()
		self.setLayout(hboxLay)
		
	def render_txt_nodnav(self):
		self.txt_nodnav.setText(str(self.nodnav))
		
	def set_nodnav(self, level, node):
		self.nodnav.set_node(level, node)
		#self.render_txt_nodnav()

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
		

class IclearWidget(QWidget):
	
	def __init__(self, nodnav, parent = None):
		QWidget.__init__(self, parent)
		
		self.parent = parent
		self.winnodnav = WinNodesNav(nodnav = nodnav, parent=self)
		
		hboxLay = QHBoxLayout()
		hboxLay.setContentsMargins(0,0,0,0)
		hboxLay.addWidget(self.winnodnav)

		self.btnURL = QPushButton(parent=self)
		self.btnURL.setIcon(QIcon('icons/icon-hyperlink.jpg'))
		self.btnURL.setFixedWidth(32)
		self.btnURL.setToolTip("URL")
		self.btnURL.clicked.connect(self.fill_from_url)
		hboxLay.addWidget(self.btnURL)

		self.btnOpen = QPushButton(parent=self)
		self.btnOpen.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.btnOpen.setFixedWidth(32)
		self.btnOpen.setToolTip("Open")
		self.btnOpen.clicked.connect(self.open_page)
		hboxLay.addWidget(self.btnOpen)
		
		self.btnMenu = QPushButton("...")
		self.btnMenu.setStyleSheet("QPushButton::menu-indicator { image: url(noimg) }")
		self.btnMenu.setFixedWidth(36)
		menu = QMenu('menu')
		
		xdgOpenAction = QAction('xdg_open', self)
		xdgOpenAction.triggered.connect(self.xdg_open)
		menu.addAction(xdgOpenAction)
		
		refilAction = QAction('refill host', self)
		refilAction.triggered.connect(self.refill_host)
		menu.addAction(refilAction)
		
		genIndexAction = QAction('gen_index_and_phpinc', self)
		genIndexAction.triggered.connect(self.gen_index_phpinc)
		menu.addAction(genIndexAction)
		
		genPlugAction = QAction('gen_plug_pagephp', self)
		genPlugAction.triggered.connect(self.gen_plug_pagephp)
		menu.addAction(genPlugAction)
		
		contListAction = QAction('gen_content_list', self)
		contListAction.triggered.connect(self.gen_content_list)
		menu.addAction(contListAction)
		
		checkMapAction = QAction('check_map', self)
		checkMapAction.triggered.connect(self.check_map)
		menu.addAction(checkMapAction)
		
		genViewAction = QAction('gen_view', self)
		genViewAction.triggered.connect(self.gen_view)
		menu.addAction(genViewAction)
		
		self.btnMenu.setMenu(menu)
		hboxLay.addWidget(self.btnMenu)

		self.setLayout(hboxLay)

	def fill_from_url(self):
		""" re-filling nodnav from the address bar of the page """
		inputDialog = QInputDialog(self)
		inputDialog.resize(QSize(700, 270))
		inputDialog.setWindowTitle("url")
		inputDialog.setLabelText("Enter the page url")

		inputDialog.setTextValue(self.winnodnav.nodnav.get_url())
		inputDialog.setInputMode(0)
		ok = inputDialog.exec_()
		pageurl = inputDialog.textValue()
		
		if ok:
			self.winnodnav.nodnav.set_from_url(pageurl)
			self.winnodnav.refill()
					
	def open_page(self):	
		if self.winnodnav.nodnav.page:
			page_path = self.winnodnav.nodnav.page.full_path()
			if iclib.Tools.check_exists_file(page_path):
				self.parent.tab_panel.add_tab(Path(page_path))
				return True
		return False
		
	def refill_host(self):
		"""refilling nodnav (when the map changes)  
		  saving nodnav as a dictionary"""
		nodedict = self.winnodnav.nodnav.get_dict()
		self.winnodnav.nodnav.host.refill(fill_sites = True, fill_mans = True)
		self.winnodnav.nodnav.set_dict(nodedict)
		self.winnodnav.refill()

	def xdg_open(self, page_path):
		if 	self.winnodnav.nodnav.page: 
			full_path = self.winnodnav.nodnav.page.full_path()
			os.system("xdg-open "+full_path)
		elif self.winnodnav.nodnav.cat: 
			full_path = self.winnodnav.nodnav.cat.full_path()
			os.system("xdg-open "+full_path)
		elif self.winnodnav.nodnav.man: 
			full_path = self.winnodnav.nodnav.man.full_path()
			os.system("xdg-open "+full_path)
		elif self.winnodnav.nodnav.site:  
			full_path = self.winnodnav.nodnav.site.full_path()
			os.system("xdg-open "+full_path)
			
	def fill_from_page_path(self, page_path):
		self.winnodnav.nodnav.set_from_page_path(page_path)
		self.winnodnav.refill()
		
	def gen_plug_pagephp(self):	
		if 	self.winnodnav.nodnav.page: 
			iclib.Service.gen_plug_pagephp(self.winnodnav.nodnav.page)
					
	def gen_index_phpinc(self):	
		if 	self.winnodnav.nodnav.man:
			iclib.Service.gen_index_phpinc(self.winnodnav.nodnav.man)
		elif self.winnodnav.nodnav.site:
			iclib.Service.gen_root_indexphp(self.winnodnav.nodnav.site)
		
	def check_map(self):	
		if 	self.winnodnav.nodnav.man:
			iclib.Service.diff_map_by_dir(self.winnodnav.nodnav.man)

	def gen_view(self):	
		pass

	def gen_content_list(self):	
		pass
		
class IclearSettingDialog(QDialog):
	
	def __init__(self, state, parent=None, hostpath = '', sitepath = ''):
		super(IclearSettingDialog, self).__init__(parent)
		
		self.setWindowTitle("Iclear settings")
		self.setModal(True)
		
		self.state = QCheckBox("Iclear support is enabled")
		self.state.setChecked(state)
		self.hostpath_label = QLabel("apache sites dir")
		self.hostpath_value = QLineEdit(hostpath)
		
		self.btnOpenHost = QPushButton(parent=self)
		self.btnOpenHost.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton)) 
		self.btnOpenHost.clicked.connect(self.on_open_host)
		
		self.sitepath_label = QLabel("additional path")
		self.sitepath_value = QLineEdit(sitepath)
		
		self.btnOpenSite = QPushButton(parent=self)
		self.btnOpenSite.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton)) 
		self.btnOpenSite.clicked.connect(self.on_open_site)
		
		self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		
		mainlayout = QVBoxLayout(self)
		mainlayout.addWidget(self.state)
		hbox_host = QHBoxLayout()
		hbox_host.addWidget(self.hostpath_label)
		hbox_host.addWidget(self.hostpath_value)
		hbox_host.addWidget(self.btnOpenHost)
		mainlayout.addLayout(hbox_host)
		hbox_site = QHBoxLayout()
		hbox_site.addWidget(self.sitepath_label)
		hbox_site.addWidget(self.sitepath_value)
		hbox_site.addWidget(self.btnOpenSite)
		mainlayout.addLayout(hbox_site)
		
		mainlayout.addWidget(self.button_box)
		
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)
		
	def on_open_host(self):
		hostdir = QFileDialog.getExistingDirectory(parent=self, caption="Select host path")
		if hostdir == '':
			return
		self.hostpath_value.setText(hostdir)
		
	def on_open_site(self):
		hostpath = self.hostpath_value.text()
		sitedir = QFileDialog.getExistingDirectory(parent=self, caption="Select site path", 
			directory=hostpath)
		if sitedir == '':
			return
		self.sitepath_value.setText(sitedir[len(hostpath)+1:])
		
	def get_values(self):
		return (self.state.isChecked(), self.hostpath_value.text(), self.sitepath_value.text())


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
	window.show()										 
	sys.exit(app.exec_()) 		

else:
	import libiclear.iclear as iclib
	
