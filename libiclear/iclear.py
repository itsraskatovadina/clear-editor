#! /usr/bin/python3

import xml.etree.ElementTree as ET
import os, os.path

class ANode(object):
	
	def __init__(self, nid):
		""" nid, lvl, parent, children = []  
		nid - identifier, string, required
		parent - parent, there is a parent missing (None) - the root element;
		children - descendants, the list with ANode objects, may be empty  
		lvl - level in the tree """
		self.nid = str(nid)
		self.parent = None
		self.children = list()
		self.lvl = 0 # when creating a node, its level = 0
		
	def __repr__(self):
		return self.nid
		
	def info(self):
		return "".join([self.nid, "; par: ", str(self.parent), "; lvl: ", str(self.lvl), "; subs: ", str(self.children)])
 
	def set_parent(self, node):
		if isinstance(node, __class__):
			# exclude cyclic connections
			if ((self.parent != node)and(self != node)and(node not in self.children)):
				self.parent = node
				node.add_child(self)
				return node
		else: 
			#self.parent = None
			print("invalid argument type node in set_parent")
		
	def add_child(self, node):
		if isinstance(node, __class__):
			# exclude cyclic connections
			if ((self.parent != node)and(self != node)and(node not in self.children)):
				self.children.append(node)
				node.parent = self
				node.lvl = self.lvl + 1
				return node
		else: print("invalid argument type node in add_child")
		
	def add_children(self, subnodes):
		if isinstance(subnodes, list):
			for child in subnodes: self.add_child(child)
		else: print("invalid argument type node in add_children")
		
	@staticmethod
	def create(nid, parent=None, children=None):   
		node = ANode(nid)
		if parent: node.set_parent(parent)
		if children: node.add_children(children)
		return node
		
	def is_root(self):
		if (self.lvl == 0): return True
		return False
		
	def size(self):
		return len(self.children)
		
	def get_child(self, nid):
		""" get a direct subordinate node by nid """
		for child in self.children:
			if child.nid == nid: return child
		return None
		
	def find_child(self, nid):
		""" get a node (search through the entire subordinate tree) by nid """
		if (self.nid == nid): return self
		for child in self.children:
			res = child.find_child(nid)
			if res: return res
		return None
		
	def render(self):
		""" traversing the tree downwards with element printing """
		print("\t"*self.lvl, repr(self))
		for child in self.children: child.render()
		
	def render_info(self):
		""" traversing the tree downwards with extended element printing """
		print("".join(["\t"*self.lvl, self.info()]))
		for child in self.children: child.render_info()
		
	def travers(self, func, count = 0):
		""" traversing the tree downwards with a function call on the elements, returns the number of calls  """
		func(self)
		count = count + 1
		for child in self.children: 
			count = child.travers(func, count)
		return count 
		
	def travers_list_accum(self, func, results = []):
		""" traversing the tree downwards with a function call on the elements, the results are saved in a list  """
		results.append(func(self))
		for child in self.children:
			child.travers_list_accum(func, results)
		return results 

class Iclear(object):
	
	#modname = __name__
	#shift_str_class = len("<class '") + len(modname) + 1
	
	#hostname = "iclear"
	#hostpath = "/home/dina/www/"
	topdir = "ref"
	pagedir = "pages"
	phpincdir = "phpinc"
	pageext = ".php"
	mapname = "map.xml"
	
	levels_list = ['host', 'site', 'top', 'man', 'cat', 'page'] # список уровней
	
	levels_index = {}		# пронумерованный словарь уровней
	numerator = 0
	for el in levels_list:
		levels_index[el] = numerator
		numerator += 1
	
	def is_level(level):
		"""  проверяет присутствие lvl в списке уровней  """
		num_level = Iclear.levels_index.get(level)
		if num_level == None: return False
		else: return True
		
	def num_level(level):
		"""  возвращает номер уровеня lvl, level он есть в списке уровней  """
		num_level = Iclear.levels_index.get(level) 
		if num_level == None:
			print("неверный аргумент Iclear.num_level ", level)
			return False
		return num_level
		
	def next_level(level):	
		""" навигация уровням, возвращает следующий уровень для lvl,
			для top - man, для man - cat, для cat - page, для page - None """
		num_level =  Iclear.num_level(level)	# возможен Critical Error, если num_level == None (не найден)
		if (num_level > len(Iclear.levels_list)-2): return None
		else: return Iclear.levels_list[num_level+1]
		
	def prev_level(level):	
		""" навигация уровням, возвращает предидущий уровень уровень для lvl,
			для top - None, для man - top, для cat - man, для page - cat """
		num_level =  Iclear.num_level(level)	# возможен Critical Error, если num_level == None (не найден)
		if (num_level < 1): return None
		else: return Iclear.levels_list[num_level-1]	
		
	def call_func_by_levels(func):
		""" обход всех уровней levels_list,  результаты возвращаются списком"""
		results = []
		for el in Iclear.levels_list:
			result = func(el)
			results.append(result)
		return results
	
class INode(ANode):
	""" nid=, lvl, name, fname, path, parent, children = [] (subnodes)
		nid, lvl, name, path  - required, string and not empty
		in map.xml  
		nid = data-id, identifier
		name = data-name, menu name
		path = data-path, 
		runame = data-runame, 
		fname = data-fname, full name  
	 """

	def __init__(self, nid, level, name="", fname="", runame="", path="", parent= None):
		super(__class__, self).__init__(nid)
		self.nid = str(nid)
		self.level = level
		self.name = name
		self.fname = fname	
		self.runame = runame 
		self.path = path
		if parent: self.set_parent(parent)
		'''  mutable object as a default function argument '''
		#if isinstance(children, list)and(len(children) == 0): self.children = list()
		
	def info(self):
		if isinstance(self.parent, INode): info = self.parent.info() + "-"
		else: info = ""
		return info + self.nid + "(" + self.level[0:1] + ")"
		
	def finfo(self):
		if isinstance(self.parent, INode): info = self.parent.info() + "-"
		else: info = ""
		return info + self.nid + "(" + self.level[0:1] + ") " + self.name + ", " + self.path + ", " + self.fname + ", "+ self.runame
			
	'''
	def get_child(self, nid):
		""" получить подчиненный узел по nid  (get_child_node)"""
		for node in self.subnodes:
			if node.nid == nid: return node
	'''
class IHost(ANode):
	
	def __init__(self, nid, hostpath, sitepath = ""):
		super(__class__, self).__init__(nid)
		self.nid = str(nid)
		self.level = "host"
		self.hostpath = hostpath
		self.sitepath = sitepath
		#self.hostdir = self.hostpath + self.path  == full_path()
		self.topdir = Iclear.topdir
		self.pagedir = Iclear.pagedir
		self.phpincdir = Iclear.phpincdir
		self.pageext = Iclear.pageext
		self.mapname = Iclear.mapname
		
	def finfo(self):
		if isinstance(self.parent, INode): info = self.parent.info() + "-"
		else: info = ""
		return info + self.nid + "(" + self.level[0:1] + ") " + self.hostpath + ", " + self.sitepath
		
	def full_path(self): 	# путь к root сайта
		full_path = os.path.join(self.hostpath, self.sitepath)
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			return False
		
	def fill(self, fill_sites = True, fill_mans = True):
		""" заполняем узлы уровня site из map.xml хоста """
		
		full_mapname = os.path.join(self.full_path(), self.mapname)
		if not(Tools.check_exists_file(full_mapname)): return
			
		tree = ET.parse(full_mapname)
		maproot = tree.getroot()
		uls = maproot.findall("ul")
		for ul in uls:
			lis = ul.findall("li")
			for li in lis:
				site = self.add_child(ISite(nid = li.get("data-id"), name = li.get("data-name"), 
					fname = li.get("data-fname"), path = li.get("data-path")))
				if fill_sites: site.fill_sites()
				if fill_mans: site.fill_mans()
				
	def refill(self, fill_sites = True, fill_mans = True):
		self.children = []
		self.fill(fill_sites = fill_sites, fill_mans = fill_mans)

class ISite(INode):
	""" 	"""
	def __init__(self, nid, name="", fname="", path="", parent= None, description=""):
		"""  заполняем  """
		if name=="": name=nid
		if path=="": path=nid
		super(__class__, self).__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, level = "site")
		self.description = description
		
	def host(self): return self.parent
	
	def full_path(self): 	# путь к root сайта
		full_path = os.path.join(self.host().full_path(), self.path)
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			raise FileNotFoundError('The file ' + full_path + ' is not present.') 
			
	#filling is divided into two parts
	def fill(self, strfilter = None):
		self.fill_sites(strfilter)
		self.fill_mans(strfilter)
			
	def fill_sites(self):
		""" заполняем поле description и 
			узлы уровня top и man из map.xml сайта """
			
		full_mapname = os.path.join(self.full_path(), self.host().mapname)
		if not(Tools.check_exists_file(full_mapname)): return
		tree = ET.parse(os.path.join(full_mapname))
		
		maproot = tree.getroot()
		nodedescr = maproot.find("descr")
		if nodedescr != None:
			self.description = nodedescr.text
		
		uls = maproot.findall("ul")
		for ul in uls:
			top = ITop(nid = ul.get("data-id"), name = ul.get("data-name"), fname = ul.get("data-fname"),
				path = ul.get("data-path"), parent = self) 
			self.add_child(top)
			lis = ul.findall("li")
			for li in lis:
				logo = li.get("logo") if 'logo' in li.attrib else False
				man = IMan(nid = li.get("data-id"), name = li.get("data-name"), fname = li.get("data-fname"),
				 path = li.get("data-path"), parent = top, logo = logo)
				top.add_child(man)
				
	def fill_mans(self):
		for top in self.children:
			for man in top.children: man.fill()		
			
class ITop(INode):
	def __init__(self, nid, name="", fname="", path="", parent= None):
		super(__class__, self).__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, level = "top")
			
			
class IMan(INode):
	def __init__(self, nid, name="", fname="", path="", parent= None, logo = False):
		super(__class__, self).__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, level = "man")
		self.logo = logo
		
	def top(self): return self.parent
	def site(self): return self.parent.parent
	def host(self): return self.parent.parent.parent
	
	def short_path(self): 	# короткий путь к manual без /home/dina/www/iclear
		return os.path.join(self.site().path, self.host().topdir, self.top().path, self.path)
		
	def full_path(self): 	# полный путь к manual
		full_path = os.path.join(self.host().full_path(), self.short_path())
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			raise FileNotFoundError('The file ' + full_path + ' is not present.') 
			
	def fill(self):
		""" заполняем узлы на уровне cat и page из map.xml мануала """
		full_mapname = os.path.join(self.full_path(), self.host().mapname)
		tree = ET.parse(full_mapname)
		maproot = tree.getroot()
		uls = maproot.findall("ul")
		for ul in uls:
			cat = ICat(nid = ul.get("data-id"), name = ul.get("data-name"), path = ul.get("data-path"), parent = self)
			self.add_child(cat)
			lis = ul.findall("li")
			for li in lis:
				#runame = li.get("data-runame") if 'data-runame' in li.attrib else li.get("data-fname")
				if 'data-runame' in li.attrib:
					runame1 = li.get("data-runame")
					fname1 = li.get("data-name") + " (" + runame1 + ")"
				else:
					runame1 = li.get("data-fname")
					fname1 = li.get("data-fname")
				page = IPage(nid = li.get("data-id"), name = li.get("data-name"), fname = fname1, runame = runame1,
				path = li.get("data-path"), parent = cat)
				cat.add_child(page)
			
class ICat(INode):
	def __init__(self, nid, name="", fname="", runame="", path="", parent= None):
		super(__class__, self).__init__(nid = nid, name = name, fname = fname, runame = runame, path = path, parent= parent, level = "cat")
		
	def man(self): return self.parent
	def site(self): return self.man().site()
	def host(self): return self.man().host()
	
	def short_path(self): 	# короткий путь к page без /home/dina/www/iclear
		return os.path.join(self.site().path, self.host().topdir, self.man().parent.path,
			self.man().path, self.host().pagedir, self.path)

	def full_path(self): 	# путь к page /home/dina/www/iclear/conspect/ref/web/html/pages/intro/links
			return os.path.join(self.host().full_path(), self.short_path())
			
class IPage(INode):
	def __init__(self, nid, name="", fname="", runame="", path="", parent= None):
		super(__class__, self).__init__(nid = nid, name = name, fname = fname, runame = runame, path = path, parent= parent, level = "page")
		
	def man(self): return self.parent.parent
	def site(self): return self.man().site()
	def host(self): return self.man().host()
	
	def short_path(self): 	# короткий путь к page без /home/dina/www/iclear
		return os.path.join(self.site().path, self.host().topdir, self.man().parent.path,
			self.man().path, self.host().pagedir, self.parent.path, self.path + ".php")

	def full_path(self): 	# путь к page /home/dina/www/iclear/conspect/ref/web/html/pages/intro/links
			return os.path.join(self.host().full_path(), self.short_path())
			
class NodesNav(Iclear):
	
	def __init__(self, host = None, nodedict = None):
		
		self.site = self.top = self.man = self.cat = self.page = None
		self.host = host
		if nodedict: self.set_dict(nodedict)
		#if nodestr:	self.set_from_nodestr(nodestr)
												
	def set_dict(self, nodedict):
		
		self.site = self.top = self.man = self.cat = self.page = None
		if self.host is None:
			return
		
		sitestr = str(nodedict.get('site')).strip()
		if sitestr not in ('', None):
			finded_child_node = self.host.get_child(sitestr)
			if finded_child_node != None:
				self.site = finded_child_node
				topstr = str(nodedict.get('top')).strip()
				if topstr not in ('', None):
					finded_child_node = self.site.get_child(topstr)
					if finded_child_node != None:
						self.top = finded_child_node
						manstr = str(nodedict.get('man')).strip()
						if manstr not in ('', None):
							finded_child_node = self.top.get_child(manstr)
							if finded_child_node != None:
								self.man = finded_child_node
								catstr = str(nodedict.get('cat')).strip()
								if catstr not in ('', None):
									finded_child_node = self.man.get_child(catstr)
									if finded_child_node != None:
										self.cat = finded_child_node
										pagestr = str(nodedict.get('page')).strip()
										if pagestr not in ('', None):
											finded_child_node = self.cat.get_child(pagestr)
											if finded_child_node != None:
												self.page = finded_child_node
												
	def get_dict(self):
		nodedict = {'site': self.str_node('site'),
					'top': self.str_node('top'),
					'man': self.str_node('man'),
					"cat": self.str_node('cat'),
					"page": self.str_node('page')}
		return nodedict
		
	def __repr__(self):
		""" возвращает текстовое представление объекта """
		navrepr = "".join(["(h)=", str(self.host), ", (s)=", str(self.site), ", (t)=", str(self.top),
			", (m)=", str(self.man), ", (c)=", str(self.cat), ", (p)=", str(self.page)])
		return navrepr
		
	def repr_node(self, level, mark = ""):
		""" возвращает текстовое представление атрибута (одного из host, top, man, cat, page) 
			если это пробел, возвращается '' или атрибут mark   """
		mark = str(mark) 
		#num_level = Iclear.num_level(level)	# возможен Critical Error, если num_lvl == None (не найден)
		attr = getattr(self, level)
		return mark if attr is None else attr
		
	def __str__(self):
		""" возвращает текстовое представление объекта """
		return "".join([
			"(h)=", self.str_node('host'),
			", (s)=", self.str_node('site'),
			", (t)=", self.str_node('top'), 
			", (m)=", self.str_node('man'),  
			", (c)=", self.str_node('cat'),     
			", (p)=", self.str_node('page')])
		
	def str_node(self, level, mark = ""):
		""" возвращает текстовое представление атрибута (одного из host, top, man, cat, page) 
			если это пробел, возвращается '' или атрибут mark   """
		attr = getattr(self, level)
		return str(mark) if attr is None else str(attr.nid)
		
	def get_node(self, level):
		return getattr(self, level)
		
	def set_node(self, level, node):
		""" установка атрибута, если пустое значение - НЕТ(очищаем следующие атрибуты) """
		#num_lvl = Iclear.num_level(level)	# возможен Critical Error, если num_lvl == None (не найден)
		setattr(self, level, node)

		
	def isempty_node(self, level):
		"""  проверка заполненности, если атрибут пуст - возвращает False, иначе True """
		if getattr(self, level) == None: return True
		return False

	def get_url(self):
		""" генерация  ссылки типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """
		
		url = ''.join(["http://", self.host.sitepath,"/", self.site.path, "/", self.host.topdir, "/"])
		if self.top:
			url = url +''.join([self.top.path, "/"])
			if self.man:
				url = url +''.join([self.man.path, "/"])
				if self.cat:
					url = url +''.join([self.host.pagedir, "/", self.cat.path, "/"])
					if self.page:
						url = url +''.join([self.page.path, self.host.pageext])  
		return url
		
	def set_from_url(self, url):
		""" генерация NodesNav по ссылке типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """ 
		
		url_parts = url.split(sep="/")
		
		# ['http:', '', 'iclear', 'conspect', 'ref', 'soft', 'python', 'pages', 'datatypes', 'list.php#join']
		hostnid = url_parts[2]
		if hostnid != self.host.nid:
			return
		sitenid = url_parts[3]
		topnid = url_parts[5]
		mannid = url_parts[6]
		catnid = ""
		pagenid = ""
		if len(url_parts) > 8:
			catnid = url_parts[8]
			pagenid = url_parts[9].split(sep=".")[0]
			
		nodestr = NodesString(site = sitenid, top = topnid, man = mannid, cat = catnid, page = pagenid)
		self.set_from_nodestr(nodestr = nodestr)
		
	def set_from_page_path(self, page_path):
		
		self.site = self.top = self.man = self.cat = self.page = None
		
		if page_path.find(self.host.full_path()) == -1:
			return False
		parts = page_path[len(self.host.full_path())+1:].split(sep="/")
		if len(parts) != 7:
			return False
		
		nodedict = {'site': parts[0], 'top': parts[2], 'man': parts[3],
					"cat": parts[5], "page": parts[6].split(sep=".")[0]}
		self.set_dict(nodedict)
		if self.page:
			return True

		return False
		
class Service():
	
	def regen_map(node):
		""" функция написана для исправления варианта map.xml, добавляет атрибут data-runame, если его нет,
			может работать на уровне site и на уровне man"""

		mapname = os.path.join(node.full_path(), "map.xml")

		maptext = "<map>\n"
		tree = ET.parse(mapname)
		maproot = tree.getroot()
		uls = maproot.findall("ul")
		for ul in uls:
			fname = ul.get("data-fname") if 'data-fname' in ul.attrib else ul.get("data-name")
			runame = ul.get("data-runame") if 'data-runame' in ul.attrib else ul.get("data-fname")
			maptext += ''.join(['<ul',
					' data-name="', ul.get("data-name"), '"',
					' data-fname="', fname, '"',
					' data-id="', ul.get("data-id"), '"',
					' data-path="', ul.get("data-path"), '"',
					' data-runame="', runame, '"',
					'>\n'])
			lis = ul.findall("li")
			for li in lis:
				fname = li.get("data-fname") if 'data-fname' in li.attrib else li.get("data-name")
				runame = li.get("data-runame") if 'data-runame' in li.attrib else li.get("data-fname")
				maptext += ''.join([ '    <li',
					' data-name="', li.get("data-name"), '"',
					' data-fname="', fname, '"',
					' data-id="', li.get("data-id"), '"',
					' data-path="', li.get("data-path"), '"',
					' data-runame="', runame, '"',
					'></li>\n'])
			maptext += '</ul>\n'
		maptext += '</map>'
		
		print(mapname, "\n", maptext) 
		#Tools.write_file(mapname, maptext)
	
	def gen_asidephp(man, msg = True):
		pass
		
	def gen_headerphp(man, msg = True):
		pass

	def gen_partheadphp(man, msg = True):
		pass
		
	def gen_indexphp(man, msg = True):
		pass
		
	def gen_index_phpinc(node, msg = True):
		Service.gen_indexphp(node, msg = msg)
		Service.gen_asidephp(node, msg = msg)
		Service.gen_headerphp(node, msg = msg)
		Service.gen_partheadphp(node, msg = msg)
		
	def gen_root_indexphp(site):
		pass
		
	def gen_plug_pagephp(page, msg = True):
		pass
		
	def check_map(man):
		pass
		
	def diff_map_by_dir(man):
		pass
		
	def gen_view(node):
		pass
		
class Tools():
 
	@staticmethod
	def check_exists_file(fname):
		if not(os.path.exists(fname)): 
			print(''.join(["No such file or dir ", fname]))
			return False
		else:
			return True
			
if __name__ == "__main__":
	pass
