#! /usr/bin/python3

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QDialog,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QLabel,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QInputDialog,
    QFileDialog,
    QDialogButtonBox,
    QMenu,
    QAction,
    QFrame,
    QStyle,
)
from PyQt5.QtCore import QCoreApplication, QSettings, QSize, QPoint, Qt, QDir, QUrl
from PyQt5.QtGui import QFont, QIcon, QDesktopServices
from pathlib import Path
import os
import iclearlib as iclib


class WinNode(QWidget):
    def __init__(self, parent, level):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.txt = QLabel(level)
        self.lst = QComboBox()
        self.fill_list()

        self.lst.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.lst.setMinimumContentsLength(8)
        hbox = QHBoxLayout()
        hbox.addWidget(self.txt)
        hbox.addWidget(self.lst)
        self.setLayout(hbox)

        self.lst.currentIndexChanged["int"].connect(self.on_changed_list)

    def fill_list(self):
        """filling in or re-filling the selection list"""
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
        """when changing the current index of the list
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
    """widget for displaying and selecting an instance of the NodeNav class
    composition - one invisible host field and related fields(site, top, man, cat, page)"""

    def __init__(self, nodnav, parent=None):
        QWidget.__init__(self, parent)

        self.parent = parent
        self.nodnav = nodnav

        hboxLay = QHBoxLayout()
        hboxLay.setContentsMargins(0, 0, 0, 0)
        self.wsite = WinNode(parent=self, level="site")
        hboxLay.addWidget(self.wsite)
        self.wtop = WinNode(parent=self, level="top")
        hboxLay.addWidget(self.wtop)
        self.wman = WinNode(parent=self, level="man")
        hboxLay.addWidget(self.wman)
        self.wcat = WinNode(parent=self, level="cat")
        hboxLay.addWidget(self.wcat)
        self.wpage = WinNode(parent=self, level="page")
        hboxLay.addWidget(self.wpage)

        self.setLayout(hboxLay)

    def render_txt_nodnav(self):
        self.txt_nodnav.setText(str(self.nodnav))

    def set_nodnav(self, level, node):
        self.nodnav.set_node(level, node)

    def refill(self):
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
    def __init__(self, nodnav=None, open_file_cb=None, editor=None, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self._open_file_cb = open_file_cb
        self._editor = editor
        if nodnav is None:
            nodnav = self._build_nodnav_from_settings()
        self.winnodnav = WinNodesNav(nodnav=nodnav, parent=self)

        hboxLay = QHBoxLayout()
        hboxLay.setContentsMargins(0, 0, 0, 0)

        self.btnSettings = QPushButton("\u2699", parent=self)
        self.btnSettings.setFixedWidth(28)
        self.btnSettings.setToolTip("Settings")
        self.btnSettings.clicked.connect(self._open_settings)
        hboxLay.addWidget(self.btnSettings)

        hboxLay.addWidget(self.winnodnav)

        self.btnURL = QPushButton(parent=self)
        self.btnURL.setIcon(QIcon("icons/icon-hyperlink.jpg"))
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
        menu = QMenu("menu")

        xdgOpenAction = QAction("xdg_open", self)
        xdgOpenAction.triggered.connect(self.xdg_open)
        menu.addAction(xdgOpenAction)

        refilAction = QAction("refill host", self)
        refilAction.triggered.connect(self.refill_host)
        menu.addAction(refilAction)

        genIndexAction = QAction("gen_index_and_phpinc", self)
        genIndexAction.triggered.connect(self.gen_index_phpinc)
        menu.addAction(genIndexAction)

        genPlugAction = QAction("gen_plug_pagephp", self)
        genPlugAction.triggered.connect(self.gen_plug_pagephp)
        menu.addAction(genPlugAction)

        contListAction = QAction("gen_content_list", self)
        contListAction.triggered.connect(self.gen_content_list)
        menu.addAction(contListAction)

        checkMapAction = QAction("check_map", self)
        checkMapAction.triggered.connect(self.check_map)
        menu.addAction(checkMapAction)

        self._validate_action = None
        menu.aboutToShow.connect(self._update_validate_action)

        self.btnMenu.setMenu(menu)
        hboxLay.addWidget(self.btnMenu)

        hboxLay.addStretch()

        self.setLayout(hboxLay)

    @staticmethod
    def _build_nodnav_from_settings():
        settings = QSettings("settings.ini", QSettings.IniFormat)
        hostpath = settings.value("iclear/hostpath", "")
        sitepath = settings.value("iclear/sitepath", "")
        if hostpath:
            host = iclib.IHost("iclear", hostpath, sitepath=sitepath)
            host.fill(fill_sites=True, fill_mans=True)
            return iclib.NodesNav(host=host)
        return iclib.NodesNav(host=iclib.IHost("", ""))

    def _open_settings(self):
        settings = QSettings("settings.ini", QSettings.IniFormat)
        hostpath = settings.value("iclear/hostpath", "")
        sitepath = settings.value("iclear/sitepath", "")
        dlg = IclearSettingDialog(self, hostpath, sitepath)
        if dlg.exec() == IclearSettingDialog.Accepted:
            hostpath, sitepath = dlg.get_values()
            settings.setValue("iclear/hostpath", hostpath)
            settings.setValue("iclear/sitepath", sitepath)
            self.winnodnav.nodnav = self._build_nodnav_from_settings()
            self.winnodnav.refill()

    def fill_from_url(self):
        """re-filling nodnav from the address bar of the page"""
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
            if iclib.Tools.check_exists_file(page_path) and self._open_file_cb:
                self._open_file_cb(Path(page_path))
                return True
        return False

    def _collect_pages(self, node):
        pages = []
        node.travers(lambda n: pages.append(n) if isinstance(n, iclib.IPage) else None)
        return pages

    def _validate_all_pages(self):
        if not self._editor or not self._editor.plugin_manager:
            return

        hp = self._editor.plugin_manager.get_active("htmlprocessing")
        if not hp:
            self._editor.msg_srv.post_message(
                "Activate HTMLProcessing plugin first", "iclear", "warning"
            )
            return

        nav = self.winnodnav.nodnav
        pages = []

        if nav.page:
            pages = [nav.page]
        elif nav.cat:
            pages = self._collect_pages(nav.cat)
        elif nav.man:
            pages = self._collect_pages(nav.man)
        elif nav.top:
            pages = self._collect_pages(nav.top)
        else:
            self._editor.msg_srv.post_message(
                "No files selected, nothing to validate", "iclear", "warning"
            )
            return

        if not pages:
            self._editor.msg_srv.post_message(
                "No pages in current section", "iclear", "info"
            )
            return

        status_bar = self._editor.statusBar
        total = len(pages)
        errors_count = 0
        for page in pages:
            full_path = page.full_path()
            if not iclib.Tools.check_exists_file(full_path):
                continue
            status_bar.showMessage(f"Validating: {page.short_path()}", 0)
            QApplication.processEvents()
            errors = hp.validate_html(file_path=full_path)
            if errors:
                errors_count += 1
                for line, msg in errors:
                    self._editor.msg_srv.post_message(
                        f"{page.full_path()} (line {line}): {msg}",
                        "iclear", "warning",
                    )

        status_bar.clearMessage()

        if errors_count == 0:
            self._editor.msg_srv.post_message(
                f"All {total} files OK", "iclear", "info"
            )
        else:
            self._editor.msg_srv.post_message(
                f"Validated {total}, {errors_count} with errors",
                "iclear", "warning",
            )

    def _update_validate_action(self):
        hp = None
        if self._editor and self._editor.plugin_manager:
            hp = self._editor.plugin_manager.get_active("htmlprocessing")

        if hp and self._validate_action is None:
            self._validate_action = QAction("validate html", self)
            self._validate_action.triggered.connect(self._validate_all_pages)
            self.btnMenu.menu().addAction(self._validate_action)
        elif not hp and self._validate_action is not None:
            self.btnMenu.menu().removeAction(self._validate_action)
            self._validate_action = None

    def refill_host(self):
        nodedict = self.winnodnav.nodnav.get_dict()
        self.winnodnav.nodnav.host.refill(fill_sites=True, fill_mans=True)
        self.winnodnav.nodnav.set_dict(nodedict)
        self.winnodnav.refill()

    def xdg_open(self, page_path):
        if self.winnodnav.nodnav.page:
            full_path = self.winnodnav.nodnav.page.full_path()
            QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))
        elif self.winnodnav.nodnav.cat:
            full_path = self.winnodnav.nodnav.cat.full_path()
            QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))
        elif self.winnodnav.nodnav.man:
            full_path = self.winnodnav.nodnav.man.full_path()
            QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))
        elif self.winnodnav.nodnav.site:
            full_path = self.winnodnav.nodnav.site.full_path()
            QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))

    def fill_from_page_path(self, page_path):
        self.winnodnav.nodnav.set_from_page_path(page_path)
        self.winnodnav.refill()

    def gen_plug_pagephp(self):
        if self.winnodnav.nodnav.page:
            iclib.Service.gen_plug_pagephp(self.winnodnav.nodnav.page)

    def gen_index_phpinc(self):
        if self.winnodnav.nodnav.man:
            iclib.Service.gen_index_phpinc(self.winnodnav.nodnav.man)
        elif self.winnodnav.nodnav.site:
            iclib.Service.gen_root_indexphp(self.winnodnav.nodnav.site)

    def check_map(self):
        if self.winnodnav.nodnav.man:
            iclib.Service.diff_map_by_dir(self.winnodnav.nodnav.man)

    def gen_view(self):
        pass

    def gen_content_list(self):
        pass


class IclearSettingDialog(QDialog):
    def __init__(self, parent=None, hostpath="", sitepath=""):
        super(IclearSettingDialog, self).__init__(parent)

        self.setWindowTitle("Iclear settings")
        self.setModal(True)

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

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        mainlayout = QVBoxLayout(self)
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
        hostdir = QFileDialog.getExistingDirectory(
            parent=self, caption="Select host path"
        )
        if hostdir == "":
            return
        self.hostpath_value.setText(hostdir)

    def on_open_site(self):
        hostpath = self.hostpath_value.text()
        sitedir = QFileDialog.getExistingDirectory(
            parent=self, caption="Select site path", directory=hostpath
        )
        if sitedir == "":
            return
        self.sitepath_value.setText(sitedir[len(hostpath) + 1 :])

    def get_values(self):
        return (self.hostpath_value.text(), self.sitepath_value.text())
