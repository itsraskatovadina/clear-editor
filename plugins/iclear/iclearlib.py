#! /usr/bin/python3

import xml.etree.ElementTree as ET
import os, os.path


class ANode(object):
    def __init__(self, nid):
        """nid, lvl, parent, children = []
        nid - identifier, string, required
        parent - parent, there is a parent missing (None) - the root element;
        children - descendants, the list with ANode objects, may be empty
        lvl - level in the tree"""
        self.nid = str(nid)
        self.parent = None
        self.children = list()
        self.lvl = 0  # when creating a node, its level = 0

    def __repr__(self):
        return self.nid

    def info(self):
        return "".join(
            [
                self.nid,
                "; par: ",
                str(self.parent),
                "; lvl: ",
                str(self.lvl),
                "; subs: ",
                str(self.children),
            ]
        )

    def set_parent(self, node):
        if isinstance(node, __class__):
            # exclude cyclic connections
            if (self.parent != node) and (self != node) and (node not in self.children):
                self.parent = node
                node.add_child(self)
                return node
        else:
            node_type = type(node)
            Tools.output(
                f"Invalid argument type node in ANode.set_parent(), {node_type}",
                outtype="error",
            )

    def add_child(self, node):
        if isinstance(node, __class__):
            # exclude cyclic connections
            if (self.parent != node) and (self != node) and (node not in self.children):
                self.children.append(node)
                node.parent = self
                node.lvl = self.lvl + 1
                return node
        else:
            node_type = type(node)
            Tools.output(
                f"Invalid argument type node in ANode.add_child(), {node_type}",
                outtype="error",
            )

    def add_children(self, subnodes):
        if isinstance(subnodes, list):
            for child in subnodes:
                self.add_child(child)
        else:
            Tools.output(
                f"Invalid argument type node in ANode.add_children()", outtype="error"
            )

    @staticmethod
    def create(nid, parent=None, children=None):
        node = ANode(nid)
        if parent:
            node.set_parent(parent)
        if children:
            node.add_children(children)
        return node

    def is_root(self):
        if self.lvl == 0:
            return True
        return False

    def size(self):
        return len(self.children)

    def get_child(self, nid):
        """get a direct subordinate node by nid"""
        for child in self.children:
            if child.nid == nid:
                return child
        return None

    def find_child(self, nid):
        """get a node (search through the entire subordinate tree) by nid"""
        if self.nid == nid:
            return self
        for child in self.children:
            res = child.find_child(nid)
            if res:
                return res
        return None

    def render(self):
        """traversing the tree downwards with element printing"""
        print("\t" * self.lvl, repr(self))
        for child in self.children:
            child.render()

    def render_info(self):
        """traversing the tree downwards with extended element printing"""
        print("".join(["\t" * self.lvl, self.info()]))
        for child in self.children:
            child.render_info()

    def travers(self, func, count=0):
        """traversing the tree downwards with a function call on the elements,
        returns the number of calls"""
        func(self)
        count = count + 1
        for child in self.children:
            count = child.travers(func, count)
        return count

    def travers_list_accum(self, func, results=[]):
        """traversing the tree downwards with a function call on the elements,
        the results are saved in a list
        mutable  default  argument  results"""
        results.append(func(self))
        for child in self.children:
            child.travers_list_accum(func, results)
        return results


class Iclear(object):
    topdir = "ref"
    pagedir = "pages"
    phpincdir = "phpinc"
    pageext = ".php"
    mapname = "map.xml"
    # list of levels
    levels_list = ["host", "site", "top", "man", "cat", "page"]
    # dictionary of level numbers
    levels_index = {}
    numerator = 0
    for el in levels_list:
        levels_index[el] = numerator
        numerator += 1

    def is_level(level):
        """checks the presence of level in the list of levels"""
        num_level = Iclear.levels_index.get(level)
        if num_level == None:
            return False
        else:
            return True

    def num_level(level):
        """returns the level number if it is in the list"""
        num_level = Iclear.levels_index.get(level)
        if num_level == None:
            Tools.output(
                f"Invalid argument type node in ANode.num_level()", outtype="error"
            )
            return False
        return num_level

    def next_level(level):
        """level navigation, returns the next level for level,
        for top - man, for man - cat, for cat - page, for page - None"""
        num_level = Iclear.num_level(
            level
        )  #  Critical Error, if num_level == None (not finded)
        if num_level > len(Iclear.levels_list) - 2:
            return None
        else:
            return Iclear.levels_list[num_level + 1]

    def prev_level(level):
        """level navigation, returns the previous level level for level,
        for top - None, for man - top, for cat - man, for page - cat"""
        num_level = Iclear.num_level(level)
        if num_level < 1:
            return None
        else:
            return Iclear.levels_list[num_level - 1]

    def call_func_by_levels(func):
        """traversing all levels of levels_list, results are returned as a list"""
        results = []
        for el in Iclear.levels_list:
            result = func(el)
            results.append(result)
        return results


class INode(ANode):
    """nid =, lvl, name, fname, path, parent, children = [] (subnodes)
    nid, lvl, name, path  - required, string and not empty
    in map.xml
    nid = data-id, identifier
    name = data-name, menu name
    path = data-path,
    runame = data-runame,
    fname = data-fname, full name
    """

    def __init__(self, nid, level, name="", fname="", runame="", path="", parent=None):
        super(__class__, self).__init__(nid)
        self.nid = str(nid)
        self.level = level
        self.name = name
        self.fname = fname
        self.runame = runame
        self.path = path
        if parent:
            self.set_parent(parent)
        """  mutable object as a default function argument """
        # if isinstance(children, list)and(len(children) == 0): self.children = list()

    def info(self):
        if isinstance(self.parent, INode):
            info = self.parent.info() + "-"
        else:
            info = ""
        return info + self.nid + "(" + self.level[0:1] + ")"

    def finfo(self):
        if isinstance(self.parent, INode):
            info = self.parent.info() + "-"
        else:
            info = ""
        return (
            info
            + self.nid
            + "("
            + self.level[0:1]
            + ") "
            + self.name
            + ", "
            + self.path
            + ", "
            + self.fname
            + ", "
            + self.runame
        )


class IHost(ANode):
    def __init__(self, nid, hostpath, sitepath=""):
        super(__class__, self).__init__(nid)
        self.nid = str(nid)
        self.level = "host"
        self.hostpath = hostpath
        self.sitepath = sitepath
        # self.hostdir = self.hostpath + self.path  == full_path()
        self.topdir = Iclear.topdir
        self.pagedir = Iclear.pagedir
        self.phpincdir = Iclear.phpincdir
        self.pageext = Iclear.pageext
        self.mapname = Iclear.mapname

    def finfo(self):
        if isinstance(self.parent, INode):
            info = self.parent.info() + "-"
        else:
            info = ""
        return (
            info
            + self.nid
            + "("
            + self.level[0:1]
            + ") "
            + self.hostpath
            + ", "
            + self.sitepath
        )

    def full_path(self):
        full_path = os.path.join(self.hostpath, self.sitepath)
        if Tools.check_exists_file(full_path):
            return full_path
        else:
            return False

    def fill(self, fill_sites=True, fill_mans=True):
        """filling in the site level nodes from map.xml the host"""
        full_path = self.full_path()
        if not full_path:
            return False
        full_mapname = os.path.join(full_path, self.mapname)
        if not (Tools.check_exists_file(full_mapname)):
            return False
        try:
            tree = ET.parse(full_mapname)
            maproot = tree.getroot()
        except ET.ParseError as e:
            Tools.output(
                f"Parsing error: {e} in IHost.fill; host.nid={self.nid}",
                outtype="error",
            )
            return False

        uls = maproot.findall("ul")
        for ul in uls:
            lis = ul.findall("li")
            for li in lis:
                site = self.add_child(
                    ISite(
                        nid=li.get("data-id"),
                        name=li.get("data-name"),
                        fname=li.get("data-fname"),
                        path=li.get("data-path"),
                    )
                )
                if fill_sites:
                    site.fill_sites()
                if fill_mans:
                    site.fill_mans()
        if self.size() == 0:
            Tools.output(f"No detected sites in IHost.fill", outtype="info")
        return True

    def refill(self, fill_sites=True, fill_mans=True):
        self.children = []
        return self.fill(fill_sites=fill_sites, fill_mans=fill_mans)


class ISite(INode):
    """ """

    def __init__(self, nid, name="", fname="", path="", parent=None, description=""):
        """filling"""
        if name == "":
            name = nid
        if path == "":
            path = nid
        super(__class__, self).__init__(
            nid=nid, name=name, fname=fname, path=path, parent=parent, level="site"
        )
        self.description = description

    def host(self):
        return self.parent

    def full_path(self):
        full_path = os.path.join(self.host().full_path(), self.path)
        if Tools.check_exists_file(full_path):
            return full_path
        else:
            return False

    # filling is divided into two parts
    def fill(self, strfilter=None):
        self.fill_sites(strfilter)
        self.fill_mans(strfilter)

    def fill_sites(self):
        """filling in the description and the top and man level nodes from map.xml the site"""

        full_mapname = os.path.join(self.full_path(), self.host().mapname)
        if not (Tools.check_exists_file(full_mapname)):
            return False
        try:
            tree = ET.parse(full_mapname)
            maproot = tree.getroot()
        except ET.ParseError as e:
            Tools.output(
                f"Parsing error: {e} in ISite.fill_sites(); site.nid={self.nid}",
                outtype="error",
            )
            return False

        nodedescr = maproot.find("descr")
        if nodedescr != None:
            self.description = nodedescr.text

        uls = maproot.findall("ul")
        for ul in uls:
            top = ITop(
                nid=ul.get("data-id"),
                name=ul.get("data-name"),
                fname=ul.get("data-fname"),
                path=ul.get("data-path"),
                parent=self,
            )
            self.add_child(top)
            lis = ul.findall("li")
            for li in lis:
                logo = li.get("logo") if "logo" in li.attrib else False
                man = IMan(
                    nid=li.get("data-id"),
                    name=li.get("data-name"),
                    fname=li.get("data-fname"),
                    path=li.get("data-path"),
                    parent=top,
                    logo=logo,
                )
                top.add_child(man)
            if top.size() == 0:
                Tools.output(
                    f"No detected mans in ISite.fill_sites {top.nid}", outtype="info"
                )
        if self.size() == 0:
            Tools.output(
                f"No detected tops in ISite.fill_sites {self.nid}", outtype="info"
            )
        return True

    def fill_mans(self):
        for top in self.children:
            for man in top.children:
                man.fill()

        return True


class ITop(INode):
    def __init__(self, nid, name="", fname="", path="", parent=None):
        super(__class__, self).__init__(
            nid=nid, name=name, fname=fname, path=path, parent=parent, level="top"
        )


class IMan(INode):
    def __init__(self, nid, name="", fname="", path="", parent=None, logo=False):
        super(__class__, self).__init__(
            nid=nid, name=name, fname=fname, path=path, parent=parent, level="man"
        )
        self.logo = logo

    def top(self):
        return self.parent

    def site(self):
        return self.parent.parent

    def host(self):
        return self.parent.parent.parent

    def short_path(self):
        return os.path.join(
            self.site().path, self.host().topdir, self.top().path, self.path
        )

    def full_path(self):
        full_path = os.path.join(self.host().full_path(), self.short_path())
        if Tools.check_exists_file(full_path):
            return full_path
        else:
            return False

    def fill(self):
        """we fill in the nodes at the cat and page levels from map.xml the manual"""
        full_mapname = os.path.join(self.full_path(), self.host().mapname)
        if not (Tools.check_exists_file(full_mapname)):
            return False
        try:
            tree = ET.parse(full_mapname)
            maproot = tree.getroot()
        except ET.ParseError as e:
            Tools.output(
                f"Parsing error: {e} in IMan.fill(); man.nid={self.nid}",
                outtype="error",
            )
            return False

        uls = maproot.findall("ul")
        for ul in uls:
            cat = ICat(
                nid=ul.get("data-id"),
                name=ul.get("data-name"),
                path=ul.get("data-path"),
                parent=self,
            )
            self.add_child(cat)
            lis = ul.findall("li")
            for li in lis:
                # runame = li.get("data-runame") if 'data-runame' in li.attrib else li.get("data-fname")
                if "data-runame" in li.attrib:
                    runame1 = li.get("data-runame")
                    fname1 = li.get("data-name") + " (" + runame1 + ")"
                else:
                    runame1 = li.get("data-fname")
                    fname1 = li.get("data-fname")
                page = IPage(
                    nid=li.get("data-id"),
                    name=li.get("data-name"),
                    fname=fname1,
                    runame=runame1,
                    path=li.get("data-path"),
                    parent=cat,
                )
                cat.add_child(page)
            if cat.size() == 0:
                Tools.output(
                    f"No detected pages in IMan.fill {cat.nid}", outtype="info"
                )
        if self.size() == 0:
            Tools.output(f"No detected cats in IMan.fill {self.nid}", outtype="info")
        return True


class ICat(INode):
    def __init__(self, nid, name="", fname="", runame="", path="", parent=None):
        super(__class__, self).__init__(
            nid=nid,
            name=name,
            fname=fname,
            runame=runame,
            path=path,
            parent=parent,
            level="cat",
        )

    def man(self):
        return self.parent

    def site(self):
        return self.man().site()

    def host(self):
        return self.man().host()

    def short_path(self):
        return os.path.join(
            self.site().path,
            self.host().topdir,
            self.man().parent.path,
            self.man().path,
            self.host().pagedir,
            self.path,
        )

    def full_path(self):
        return os.path.join(self.host().full_path(), self.short_path())


class IPage(INode):
    def __init__(self, nid, name="", fname="", runame="", path="", parent=None):
        super(__class__, self).__init__(
            nid=nid,
            name=name,
            fname=fname,
            runame=runame,
            path=path,
            parent=parent,
            level="page",
        )

    def man(self):
        return self.parent.parent

    def site(self):
        return self.man().site()

    def host(self):
        return self.man().host()

    def short_path(self):
        return os.path.join(
            self.site().path,
            self.host().topdir,
            self.man().parent.path,
            self.man().path,
            self.host().pagedir,
            self.parent.path,
            self.path + ".php",
        )

    def full_path(self):
        return os.path.join(self.host().full_path(), self.short_path())


class NodesNav(Iclear):
    def __init__(self, host=None, nodedict=None):

        self.site = self.top = self.man = self.cat = self.page = None
        self.host = host
        if nodedict:
            self.set_dict(nodedict)

    def set_dict(self, nodedict):

        self.site = self.top = self.man = self.cat = self.page = None
        if self.host is None:
            return

        sitestr = str(nodedict.get("site")).strip()
        if sitestr not in ("", None):
            finded_child_node = self.host.get_child(sitestr)
            if finded_child_node != None:
                self.site = finded_child_node
                topstr = str(nodedict.get("top")).strip()
                if topstr not in ("", None):
                    finded_child_node = self.site.get_child(topstr)
                    if finded_child_node != None:
                        self.top = finded_child_node
                        manstr = str(nodedict.get("man")).strip()
                        if manstr not in ("", None):
                            finded_child_node = self.top.get_child(manstr)
                            if finded_child_node != None:
                                self.man = finded_child_node
                                catstr = str(nodedict.get("cat")).strip()
                                if catstr not in ("", None):
                                    finded_child_node = self.man.get_child(catstr)
                                    if finded_child_node != None:
                                        self.cat = finded_child_node
                                        pagestr = str(nodedict.get("page")).strip()
                                        if pagestr not in ("", None):
                                            finded_child_node = self.cat.get_child(
                                                pagestr
                                            )
                                            if finded_child_node != None:
                                                self.page = finded_child_node

    def get_dict(self):
        nodedict = {
            "site": self.str_node("site"),
            "top": self.str_node("top"),
            "man": self.str_node("man"),
            "cat": self.str_node("cat"),
            "page": self.str_node("page"),
        }
        return nodedict

    def __repr__(self):
        navrepr = "".join(
            [
                "(h)=",
                str(self.host),
                ", (s)=",
                str(self.site),
                ", (t)=",
                str(self.top),
                ", (m)=",
                str(self.man),
                ", (c)=",
                str(self.cat),
                ", (p)=",
                str(self.page),
            ]
        )
        return navrepr

    def repr_node(self, level, mark=""):
        mark = str(mark)
        attr = getattr(self, level)
        return mark if attr is None else str(attr)

    def __str__(self):
        return "".join(
            [
                "(h)=",
                self.str_node("host"),
                ", (s)=",
                self.str_node("site"),
                ", (t)=",
                self.str_node("top"),
                ", (m)=",
                self.str_node("man"),
                ", (c)=",
                self.str_node("cat"),
                ", (p)=",
                self.str_node("page"),
            ]
        )

    def str_node(self, level, mark=""):
        attr = getattr(self, level)
        return str(mark) if attr is None else str(attr.nid)

    def get_node(self, level):
        return getattr(self, level)

    def set_node(self, level, node):
        setattr(self, level, node)

    def isempty_node(self, level):
        if getattr(self, level) == None:
            return True
        return False

    def collect_selected_pages(self):
        """Collect pages based on current navigation state.
        Returns list of IPage, or None if no level is selected."""
        if self.page:
            return [self.page]
        elif self.cat:
            return self._collect_subtree(self.cat)
        elif self.man:
            return self._collect_subtree(self.man)
        elif self.top:
            return self._collect_subtree(self.top)
        return None

    def _collect_subtree(self, node):
        pages = []
        node.travers(lambda n: pages.append(n) if isinstance(n, IPage) else None)
        return pages

    def get_url(self):
        """generating a link like http://iclear/conspect/ref/soft/development/
        or http://iclear/conspect/ref/soft/development/pages/tools/git.php"""

        url = "".join(["http://", self.host.sitepath, "/"])

        if self.site:
            url = url + "".join([self.site.path, "/", self.host.topdir, "/"])
            if self.top:
                url = url + "".join([self.top.path, "/"])
                if self.man:
                    url = url + "".join([self.man.path, "/"])
                    if self.cat:
                        url = url + "".join(
                            [self.host.pagedir, "/", self.cat.path, "/"]
                        )
                        if self.page:
                            url = url + "".join([self.page.path, self.host.pageext])
        return url

    def set_from_url(self, url):
        """generating NodesNav from link like http://iclear/conspect/ref/soft/development/
        or http://iclear/conspect/ref/soft/development/pages/tools/git.php"""

        url_parts = url.split(sep="/")
        # ['http:', '', 'iclear', 'conspect', 'ref', 'soft', 'python', 'pages', 'datatypes', 'list.php#join']
        if len(url_parts) < 3:
            return
        hostnid = url_parts[2]
        if hostnid != self.host.nid:
            return

        sitenid = topnid = mannid = catnid = pagenid = ""
        if len(url_parts) > 3:
            sitenid = url_parts[3]
        if len(url_parts) > 5:
            topnid = url_parts[5]
        if len(url_parts) > 6:
            mannid = url_parts[6]
        if len(url_parts) > 8:
            catnid = url_parts[8]
        if len(url_parts) > 9:
            pagenid = url_parts[9].split(sep=".")[0]

        nodedict = {
            "site": sitenid,
            "top": topnid,
            "man": mannid,
            "cat": catnid,
            "page": pagenid,
        }
        self.set_dict(nodedict=nodedict)

    def set_from_page_path(self, page_path):

        self.site = self.top = self.man = self.cat = self.page = None

        if page_path.find(self.host.full_path()) == -1:
            return False
        parts = page_path[len(self.host.full_path()) + 1 :].split(sep="/")
        if len(parts) != 7:
            return False

        nodedict = {
            "site": parts[0],
            "top": parts[2],
            "man": parts[3],
            "cat": parts[5],
            "page": parts[6].split(sep=".")[0],
        }
        self.set_dict(nodedict)
        if self.page:
            return True

        return False


class Service:
    def gen_asidephp(man):

        asidename = os.path.join(man.full_path(), man.host().phpincdir, "aside.php")
        man_short_path = os.path.join(man.short_path(), "index.php")

        asidetext = f'<!DOCTYPE html>\n\
<div><ul>\n\t\
<li><span id="spanmin" onclick="resizemain()" title="menu collapse">Min</span></li>\n\
<li><a href="/{man_short_path}" id="map">Map</a></li>\n\
</ul>\n\t\
<ul id = "hiddenmenu">\n'

        for cat in man.children:
            asidetext = (
                asidetext
                + f'\t<li id = "menu_{cat.nid}"><details><summary>{cat.name}</summary><ul>\n'
            )
            for page in cat.children:
                asidetext = (
                    asidetext
                    + f'\t\t<li><a href="/{page.short_path()}" id= "item_{page.nid}" target="_self" title="{page.runame}">{page.name}</a></li>\n'
                )
            asidetext += "\t</ul></details></li>\n"
        asidetext += "</ul></div>"

        # print(asidename, "\n", asidetext)
        Tools.write_file(asidename, asidetext)

    def gen_headerphp(man):
        headertext = (
            '<div class="wrapper">\n\
	<div class="box1"><a href="../../../../../index.php" target="_self">Home</a></div>\n\
	<div class="box2"><h1><a href="/'
            + man.short_path()
            + '/index.php">'
            + man.fname
            + "</a></h1></div>\n\
</div>"
        )
        headername = os.path.join(man.full_path(), man.host().phpincdir, "header.php")
        # print(headername, "\n", headertext)
        Tools.write_file(headername, headertext)

    def gen_partheadphp(man):
        partheadtext = (
            "<title>"
            + man.name
            + '</title>\n\
<meta charset="utf-8">\n\
<meta name="robots" content="noindex">\n\
<link rel="stylesheet" type="text/css" href="../../../../../../app/styles/index.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../../app/styles/page.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../app/styles/index.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../app/styles/page.css">\n\
<script src="../../../../../../app/scripts/script.js"></script>'
        )
        partheadname = os.path.join(
            man.full_path(), man.host().phpincdir, "parthead.php"
        )
        # print(partheadname, "\n", partheadtext)
        Tools.write_file(partheadname, partheadtext)

    def gen_indexphp(man, msg=True):
        indextext = '<!DOCTYPE html>\n\
<html lang="ru">\n\
<head>\n\
	<title>'
        indextext += man.nid
        indextext += '</title>\n\
	<meta charset="utf-8">\n\
	<meta name="robots" content="noindex"/>\n\
	<link rel="stylesheet" type="text/css" href="../../../../app/styles/index.css" />\n\
	<link rel="stylesheet" type="text/css" href="../../../app/styles/index.css" />\n\
	<link rel="stylesheet" type="text/css" href="app/styles/index.css" />\n\
	<script type="text/javascript" src="../../../../app/scripts/script.js"></script>\n\
</head>\n\
<body onload="start()">\n\
	<div class="header">\n\
'
        indextext += (
            '		<div class="wrapper3">\n\
			<div class="box1"><a href="../../../index.php" target="_self">Home</a></div>\n\
			<div class="box2"><h1><a href="index.php">'
            + man.fname
            + '</a></h1></div>\n\
			<div class="box3">'
        )
        indextext += (
            '<img src="app/logo.jpg" width="40" height="40" alt="logo">'
            if man.logo
            else ""
        )
        indextext += "</div>\n\
		</div>\n\
"
        indextext += '	</div>\n\
	<div class="main">\n\
		<div class="aside"><?php include "phpinc/aside.php"; ?></div>\n\
		<div class="article">\n\
	<div class = "map etr">\n\
<ul>\n\
'
        for cat in man.children:
            indextext += "".join(
                ["\t<li><details open><summary>", cat.name, "</summary><ol>\n"]
            )
            for i in range(len(cat.children)):
                page = cat.children[i]
                # print(page.name)
                indextext += "".join(
                    [
                        '\t\t<li><a href="/',
                        page.short_path(),
                        '" target="_self" title="',
                        str(i + 1),
                        ". ",
                        page.runame,
                        '">',
                        page.name,
                        "</a></li>\n",
                    ]
                )
            indextext += "\t</ol></details></li>\n"
        indextext += "</ul>\n\
	</div></div></div>\n\
    </body>\n\
</html>\n\
"
        indexname = os.path.join(man.full_path(), "index.php")
        # print(indexname, "\n", indextext)
        Tools.write_file(indexname, indextext)

    def gen_index_phpinc(node):
        Service.gen_indexphp(node)
        Service.gen_asidephp(node)
        Service.gen_headerphp(node)
        Service.gen_partheadphp(node)

    def gen_root_indexphp(site):
        indextext = '<!DOCTYPE html>\n\
<html lang="ru">\n\
<head>\n\
	<title>'
        indextext += site.nid
        indextext += (
            '</title>\n\
	<meta charset="utf-8">\n\
	<meta name="robots" content="noindex"/>\n\
	<link rel="stylesheet" type="text/css" href="../app/styles/root.css" />\n\
	<link rel="stylesheet" type="text/css" href="app/styles/root.css" />\n\
</head>\n\
<body>\n\
	<div class="header"><div class="wrapper3">\n\
		<div class="logo"><a href="../index.php" target="_self"><img src="app/img/icons/logo.png" width="40" height="40" alt="logo"></a></div>\n\
		<div><h1><a href="index.php">'
            + site.fname
            + '</a></h1></div>\n\
	</div></div>\n\
	<div class="main">\n'
        )

        indextext += (
            '<div class="root">\n\
		<p>'
            + site.description
            + '</p>\n\
		<div class = "map"><ul>\n\
'
        )
        pagecount = 0
        for top in site.children:
            indextext += "".join(
                ["\t\t\t<li><details open><summary>", top.fname, "</summary><ol>\n"]
            )
            for man in top.children:
                extendstr = "  ("
                for cat in man.children:
                    extendstr += cat.nid + ", "
                extendstr += ")"
                extendstr = ""
                indextext += "".join(
                    [
                        '\t\t\t\t<li><a href="/',
                        man.short_path(),
                        '" target="_self">',
                        man.name,
                        "</a>",
                        extendstr,
                        "</li>\n",
                    ]
                )

                for cat in man.children:
                    for page in cat.children:
                        pagecount += 1

            indextext += "\t\t\t</ol></details></li>\n"
        indextext += "\n\
	</ul>\n\
	</div></div></div>\n\
    </body>\n\
</html>"

        indexname = os.path.join(site.full_path(), "index.php")
        # print(indexname, "\n", indextext)
        Tools.write_file(indexname, indextext)

    def gen_plug_pagephp(page):

        comments_delimiters = '\n\
<!-- ***************************************************************************************  -->\n\
<!-- =======================================================================================  -->\n\
<!--    + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +     -->\n\
<!--  - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - -  - - - - - - - - - - - -->\n\
<!--  <h3 id="header">Header <a class="selflink" href="#header"></a> </h3>  -->\n'

        pagename = page.full_path()
        if os.path.exists(pagename):
            Tools.output(f"{pagename} already exists", outtype="error")
            return False

        pagetext = f'<!DOCTYPE html>\n\
<html lang="ru">\n\
<head>\n\
	<?php include "../../phpinc/parthead.php"; ?>\n\
</head>\n\
<body onload="start()">\n\
	<div class="header"><?php include "../../phpinc/header.php"; ?></div>\n\
	<div class="main"><div class="aside"><?php include "../../phpinc/aside.php"; ?></div>\n\
	<div class="article">\n\
	<!--  {page.path}  --> \n\
	<span id="top"></span>\n\
	<div class="goup"><a href="#top" title="Вернуться к началу страницы">^</a></div>\n\
	<!--  header -->\n\
	<h2><a href="{page.path}.php">{page.fname}</a></h2>\n\
		\n	<div class="links_list"><details><summary>Ссылки</summary><ul>\n\
		<li><a href="https://en.wikipedia.org/wiki/Test" target="_blank">wiki Test</a></li>\n\
	</ul></details></div>\n{comments_delimiters}\n\
</div></div>\n\
</body>\n\
</html>'

        # print(pagename, "\n", pagetext)
        Tools.write_file(pagename, pagetext)

    def check_map(man):
        """checking the site map map
        all categories and pages should be unique by id and path,
        there should be no empty directories (manual) and categories(cat)"""

        error_found = False
        catsetpath = set()
        catsetnid = set()
        if len(man.children) == 0:
            error_found = True
            message = "Пустой man - " + man.info()
            Tools.output(message, outtype="err")

        for cat in man.children:
            if cat.path not in catsetpath:
                catsetpath.add(cat.path)
            else:
                error_found = True
                message = "Not a unique cat.path - " + cat.info()
                Tools.output(message, outtype="err")

            if cat.nid not in catsetnid:
                catsetnid.add(cat.nid)
            else:
                error_found = True
                message = "Not a unique cat.nid - " + cat.info()
                Tools.output(message, outtype="err")

            pagesetpath = set()
            pagesetnid = set()

            if len(cat.children) == 0:
                error_found = True
                message = "Empty cat - " + cat.info()
                Tools.output(message, outtype="err")

            for page in cat.children:
                if page.path not in pagesetpath:
                    pagesetpath.add(page.path)
                else:
                    error_found = True
                    message = "Not a unique page.path - " + page.info()
                    Tools.output(message, outtype="err")

                if page.nid not in pagesetnid:
                    pagesetnid.add(page.nid)
                else:
                    error_found = True
                    message = "Not a unique page.nid - " + page.info()
                    Tools.output(message, outtype="err")

        return error_found

    def diff_map_by_dir(man):
        """сравнение карты справочника map с каталогами и файлами в /pages
        1
        *всем страницами (page) из карты должны соответствовать файлы
        всем каталогам (cat) из карты должны соответствовать папки
        2
        всем файлам и каталогам на диске должны соответствовать cat и page в карте -
        не должно быть лишних файлов и каталогов на диске (не указанных в карте)
        (внутри каталогов (категорий, cat) не должно быть других каталогов
        *в папке справочника (manual) должны быть только папки каталогов из карты)"""

        if Service.check_map(man):
            return

        errtempdirname = "errtemp"

        error_found = False
        catsdir_full_path = os.path.join(man.full_path(), man.site().pagedir)
        catsdir_content = next(os.walk(catsdir_full_path))
        # в папке справочника (manual) должны быть только папки каталогов из карты)
        if len(catsdir_content[2]) > 0:
            error_found = True
            message = (
                "В папке "
                + man.info()
                + " присутствуют файлы "
                + str(catsdir_content[2])
            )
            Tools.output(message, outtype="err")

        catlistpath = list(map(lambda node: node.path, man.children))
        for catdir in catsdir_content[1]:
            if catdir not in catlistpath:
                error_found = True
                if catdir == errtempdirname:
                    Tools.output("Присутствует " + errtempdirname)
                else:
                    message = (
                        "В папке "
                        + catsdir_full_path
                        + " не указанный каталог "
                        + catdir
                    )
                    Tools.output(message, outtype="err")

        error_file_found = []
        for cat in man.children:
            # всем каталогам (cat) из карты должны соответствовать папки
            if not (os.path.exists(cat.full_path())):
                error_found = True
                message = "Не существует директории " + cat.info()
                Tools.output(message, outtype="err")

            # всем страницами (page) из карты должны соответствовать файлы
            for page in cat.children:
                if not (os.path.exists(page.full_path())):
                    error_found = True
                    message = "Не существует файла " + page.info()
                    Tools.output(message, outtype="err")

            pagesdir_full_path = cat.full_path()
            pagesdir_content = next(os.walk(pagesdir_full_path))
            # (внутри каталогов (категорий, cat) не должно быть других каталогов
            if len(pagesdir_content[1]) > 0:
                error_found = True
                message = (
                    "В папке "
                    + cat.full_path()
                    + " не указанный каталог "
                    + str(pagesdir_content[1])
                )
                Tools.output(message, outtype="err")

            # всем файлам  на диске должны соответствовать page в карте
            pagelistpath = list(map(lambda node: node.path + ".php", cat.children))
            for page in pagesdir_content[2]:
                if page not in pagelistpath:
                    error_found = True
                    error_file_found.append((pagesdir_full_path, page))
                    message = (
                        "В папке " + cat.full_path() + " не указанный файл " + page
                    )
                    Tools.output(message, outtype="err")

        # переносим лишние файлы в папку ошибок
        if len(error_file_found) > 0:
            message = (
                "Файлы не указанные в карте, будут перенесены в папку pages/errtemp"
            )
            Tools.output(message)
            import shutil

            errtempdir = os.path.join(catsdir_full_path, errtempdirname)
            if not (os.path.exists(errtempdir)):
                os.mkdir(errtempdir)

            for f in error_file_found:
                page = f[1]
                source = os.path.join(f[0], page)
                target = os.path.join(errtempdir, page)
                # print(source, target)
                shutil.move(source, target)

        if not error_found:
            Tools.output(
                "Карта справочника '"
                + man.fname
                + "' соответствует файловой структуре."
            )


class Tools:
    stdout = None
    outhandler = None

    @staticmethod
    def set_output(stdout, outhandler):
        Tools.stdout = stdout
        Tools.outhandler = outhandler

    @staticmethod
    def output(outtext, outtype="", stdout=None, outhandler=None):
        """outtext - output text, outtype = debug/info/warning/error,
        stdout is the output flag in sys.stdout, outhandler is the external handler"""

        if stdout is not None:
            thisstdout = stdout
        elif Tools.stdout is not None:
            thisstdout = Tools.stdout
        else:
            thisstdout = True

        thisouthandler = Tools.outhandler if (outhandler is None) else outhandler

        if thisstdout:
            if outtype == "error":
                print("\033[31m" + outtext + "\033[39m")
            else:
                print(outtext)
        if thisouthandler:
            thisouthandler(outtext, outtype)

    @staticmethod
    def check_exists_file(fname):
        if not (os.path.exists(fname)):
            Tools.output(f"No such file or dir {fname}", outtype="error")
            return False
        else:
            return True

    @staticmethod
    def write_file(fname, ftext):
        try:
            with open(fname, "w") as f:
                f.write(ftext)
                Tools.output(f"{fname} writed", outtype="info")
                return True
        except IOError:
            Tools.output(f"File writing error {fname}", outtype="error")
            return False


if __name__ == "__main__":
    pass
