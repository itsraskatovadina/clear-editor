#! /usr/bin/python3

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString, Tag
import os, os.path
import sys 
	
# 'site': "conspect", 'top': "web", 'man': "html", "cat": "intro", "page": "links"

class Iclear(object):
	
	modname = __name__
	shift_str_class = len("<class '") + len(modname) + 1
	
	hostname = "iclear"
	hostpath = "/home/dina/www/"
	topdir = "ref"
	pagedir = "pages"
	phpincdir = "phpinc"
	pageext = ".php"
	
"""  ------------------ class  -----------------------------------------------  """
class NodeLevels(object):
	""" class NodeLevels предоставляет навигацию по уровням levels_list
	""" 
	levels_list = ['host', 'site', 'top', 'man', 'cat', 'page'] # список уровней
	
	levels_index = {}		# пронумерованный словарь уровней
	numerator = 0
	for el in levels_list:
		levels_index[el] = numerator
		numerator += 1
	
	def islvl(lvl):
		"""  проверяет присутствие lvl в списке уровней  """
		num_lvl = NodeLevels.levels_index.get(lvl)
		if num_lvl == None: return False
		else: return True
		
	def numlvl(lvl):
		"""  возвращает номер уровеня lvl, если он есть в списке уровней  """
		num_lvl = NodeLevels.levels_index.get(lvl) 
		if num_lvl == None:
			print("неверный аргумент NodeLevels.numlvl ", lvl)
			return False
		return num_lvl
		
	def next_lvl(lvl):	
		""" навигация уровням, возвращает следующий уровень для lvl,
			для top - man, для man - cat, для cat - page, для page - None """
		num_lvl =  NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		if (num_lvl > len(NodeLevels.levels_list)-2): return None
		else: return NodeLevels.levels_list[num_lvl+1]
		
	def prev_lvl(lvl):	
		""" навигация уровням, возвращает предидущий уровень уровень для lvl,
			для top - None, для man - top, для cat - man, для page - cat """
		num_lvl =  NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		if (num_lvl < 1): return None
		else: return NodeLevels.levels_list[num_lvl-1]	
		
	def call_func_by_lvls(func):
		""" обход всех уровней levels_list,  результаты возвращаются списком"""
		results = []
		for el in NodeLevels.levels_list:
			result = func(el)
			results.append(result)
			
		return results
		 

"""  ------------------ class  -----------------------------------------------  """
class NodesString(object):
	""" объект nodestr = 'host': "conspect", 'top': "web", 'man': "html", "cat": "intro", "page": "links"
		где каждый элемент это lvl + (node.nid или "")(текст);
	""" 
		
	def __init__(self, host = "", site = "", top = "", man  = "", cat  = "", page = ""):
		""" объект nodestr = 'host': "conspect", 'top': "web", 'man': "html", "cat": "intro", "page": "links" 
		или 'host': "conspect", 'top': "web", 'man': "", "cat": "", "page": ""
		или 'host': "", 'top': "", 'man': "", "cat": "", "page": ""
		(после первого пропуска значения следующие значения - пробелы, не может быть узла без родителя кроме первого)
		где каждый элемент это lvl + (node.nid или "")(текст);
		!!!! не проверяется корректность подчиненности и корректность узла node.nid,
		то есть man может не соответствовать top и вообще не являтся одним из node.nid
		например 'top': "web", 'man': "spec", или 'top': "0err", 'man': "123" 
		
		если host не передан, по умолчанию заполняем из Iclear.hostname
		"""
 
		if host == "": host = Iclear.hostname 
		self.site = ""; self.top = ""; self.man = ""; self.cat = ""; self.page = ""
		
		self.host = str(host).strip()
		if self.host != "":
			self.site = str(site).strip()
			if self.site != "":
				self.top = str(top).strip()
				if self.top != "":
					self.man = str(man).strip()		
					if self.man != "":
						self.cat = str(cat).strip()
						if self.cat != "":
							self.page = str(page).strip()
							
							
							
	def set_node(self, lvl, nodenid):
		""" установка атрибута, если пробельное значение - очищаем следующие атрибуты """
		
		num_lvl = NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		
		if (nodenid == None): nodenid = '' 
		setattr(self, lvl, str(nodenid).strip())
		if (num_lvl > len(NodeLevels.levels_list)-2): return
		if (str(nodenid).strip()==""): 
			for i in range(num_lvl + 1, len(NodeLevels.levels_list)):
				setattr(self, NodeLevels.levels_list[i], '')
				#print(NodeLevels.levels_list[i])
		
			
	def get_dict(self):
		""" возвращает представление объекта NodesString в виде словаря
		nodestr_dict = {'host': "clear", 'top': "web", 'man': "html", "cat": "intro", "page": "links"}  """
		
		nodestr_dict = {}
		for el in NodeLevels.levels_list:
			nodestr_dict[el] = getattr(self, el)
			
		return nodestr_dict
		
	def set_dict(self, nodestr_dict):
		""" заполнение  объекта NodesString из словаря
		nodestr_dict = {'site': "clear",'top': "web", 'man': "html", "cat": "intro", "page": "links"}  """
		#print('            !!!!!!!!!!PLUG!!!!!!!!!   ' )
		
		self.site = ""; self.top = ""; self.man = ""; self.cat = ""; self.page = ""
		if nodestr_dict.get('site') not in ('', None):
			self.set_node('site', nodestr_dict.get('site'))
			if nodestr_dict.get('top') not in ('', None):
				self.set_node('top', nodestr_dict.get('top'))
				if nodestr_dict.get('man') not in ('', None):
					self.set_node('man', nodestr_dict.get('man'))
					if nodestr_dict.get('cat') not in ('', None):
						self.set_node('cat', nodestr_dict.get('cat'))
						if nodestr_dict.get('page') not in ('', None):
							self.set_node('page', nodestr_dict.get('page'))

		return self
		
	def repr_node(self, lvl, mark = ""):
		""" возвращает текстовое представление атрибута (одного из host, top, man, cat, page) 
			если это пробел, возвращается '' или атрибут mark   """
			
		mark = str(mark)
		num_lvl = NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		return mark if (getattr(self, lvl)=="") else getattr(self, lvl)
		  
	def __repr__(self):
		""" возвращает текстовое представление объекта """
		return "".join([
			"(h)=",	self.repr_node('host', mark ="''"),
			", (s)=", self.repr_node('site', mark ="''"),
			", (t)=", self.repr_node('top', mark ="''"), 
			", (m)=", self.repr_node('man', mark ="''"),  
			", (c)=", self.repr_node('cat', mark ="''"),     
			", (p)=", self.repr_node('page', mark ="''")])
					
	def isempty_node(self, lvl):
		"""  проверка заполненности, если атрибут пуст - возвращает False, иначе True """
		if getattr(self, lvl) == "": return True
		return False
					
	def isnodesstring(self):
		"""  проверка заполненности, если все атрибуты пустые - возвращает False, иначе True """
		for el in NodeLevels.levels_list:
			if self.isempty_node(el): return True
		return False
		
	def isnodesstring(obj):
		""" проверка проверка принадлежности к классу NodesString """
		base_class_name = str(obj.__class__)[Iclear.shift_str_class:-2]
		if base_class_name == 'NodesString': return True
		else: return False 
		
	def isvalid(obj):	
		""" проверка проверка принадлежности к классу NodesString """
		if (NodesString.isnodesstring(obj)) and (obj.isnodesstring()): return True
		else: return False

"""  ------------------ class  -----------------------------------------------  """
class NodesNav(Iclear):
	""" объект nodenav = 'host': node("conspect"), 'top': node("web"), 'man': node("html"),
		"cat": node("intro"), "page": "links"
		или 'host': "conspect", 'top': "web", 'man': "", "cat": "", "page": ""
		объект предназначен для навигации/фильтрации, объект-view - WinNodesNav
	"""
	def __init__(self, host = None, site = None, top = None, man  = None, cat  = None, page = None,
					nodestr = None):
		""" nodnav = NodesNav(host = host, nodestr = NodesString()) 
			если объект инициализируется не пустыми аттрибутами типа Node
			 или непустым аттрибутом NodesString 
			приоритет имеют аттрибуты типа Node """

		self.host = None; self.site = None; self.site = None; self.top = None;
		self.man = None; self.cat = None; self.page = None
		
		if Node.isvalid(host)and(host.lvl == 'host'):
			self.host = host
			if Node.isvalid(site)and(site.parent == self.host)and(site.lvl == 'site'):
				self.site = site
				if Node.isvalid(top)and(top.parent == self.site)and(top.lvl == 'top'):
					self.top = top
				if Node.isvalid(man)and(man.parent == self.top)and(man.lvl == 'man'):
					self.man = man
					if Node.isvalid(cat)and(cat.parent == self.man)and(cat.lvl == 'cat'):
						self.cat = cat
						if Node.isvalid(page)and(page.parent == self.cat)and(page.lvl == 'page'):
							self.page = page
							

		if NodesString.isvalid(nodestr):		
			if (self.site == None)and(not nodestr.isempty_node('site')):
				finded_child_node = self.host.get_child_node(nodestr.site)
				if finded_child_node != None:
					self.site = finded_child_node
					if (self.top == None)and(not nodestr.isempty_node('top')):
						finded_child_node = self.site.get_child_node(nodestr.top)
						if finded_child_node != None:
							self.top = finded_child_node
							if (self.man == None)and(not nodestr.isempty_node('man')):
								finded_child_node = self.top.get_child_node(nodestr.man)
								if finded_child_node != None:
									self.man = finded_child_node
									if (self.cat == None)and(not nodestr.isempty_node('cat')):
										finded_child_node = self.man.get_child_node(nodestr.cat)
										if finded_child_node != None:
											self.cat = finded_child_node
											if (self.page == None)and(not nodestr.isempty_node('page')):
												finded_child_node = self.cat.get_child_node(nodestr.page)
												if finded_child_node != None:
													self.page = finded_child_node
 
	def get_node(self, lvl):
		return getattr(self, lvl)
		
	def set_node(self, lvl, node):
		""" установка атрибута, если пробельное значение - очищаем следующие атрибуты """
		num_lvl = NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		setattr(self, lvl, node)
		
	def repr_node(self, lvl, mark = ""):
		""" возвращает текстовое представление атрибута (одного из host, top, man, cat, page) 
			если это пробел, возвращается '' или атрибут mark   """
			
		mark = str(mark)
		num_lvl = NodeLevels.numlvl(lvl)	# возможен Critical Error, если num_lvl == None (не найден)
		attr = getattr(self, lvl)
		return mark if (attr =="") else attr
		
	def isempty_node(self, lvl):
		"""  проверка заполненности, если атрибут пуст - возвращает False, иначе True """
		if getattr(self, lvl) == None: return True
		return False
		
	def __repr__(self):
		""" возвращает текстовое представление объекта """
		navrepr = "".join(["(h)=", str(self.host), ", (s)=", str(self.site), ", (t)=", str(self.top),
			", (m)=", str(self.man), ", (c)=", str(self.cat), ", (p)=", str(self.page)])
			
		return navrepr
					
	def gen_link(self):
		""" генерация  ссылки типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """
		
		link = ''.join(["http://", self.site.hostname,"/", self.site.path, "/", self.site.topdir, "/"])
		if self.top:
			link = link +''.join([self.top.path, "/"])
			if self.man:
				link = link +''.join([self.man.path, "/"])
				if self.cat:
					link = link +''.join([self.site.pagedir, "/", self.cat.path, "/"])
					if self.page:
						link = link +''.join([self.page.path, self.site.pageext])  
		
		return link
		
	def gen_from_link(self, link):
		""" генерация NodesNav по ссылке типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """ 
		
		listlink = link.split(sep="/")
		
		# ['http:', '', 'iclear', 'conspect', 'ref', 'soft', 'python', 'pages', 'datatypes', 'list.php#join']
		hostnid = listlink[2]
		host = Host(hostnid)
		
		sitenid = listlink[3]
		topnid = listlink[5]
		mannid = listlink[6]
		catnid = ""
		pagenid = ""

		if len(listlink) > 8:
			catnid = listlink[8]
			pagenid = listlink[9].split(sep=".")[0]
			
		nodestr = NodesString(host = hostnid, site = sitenid, top = topnid, man = mannid, cat = catnid, page = pagenid)
		self.__init__(host = host, nodestr = nodestr)
		
	def call_func_by_nodes(self, lvl, func, msg = False):
		""" обход всех уровней,  результаты возвращаются списком """
 
		results = []
		for site in self.host.subnodes:
			# фильтр site	
			if not(self.isempty_node("site")) and (self.site.nid!= site.nid): continue  
			if lvl == "site": 
				result = func(site); results.append(result)
			else:
				for top in site.subnodes:
					# фильтр top
					if not(self.isempty_node("top")) and (self.top.nid!= top.nid): continue  
					if lvl == "top": 
						result = func(top); results.append(result)
					else:
						for man in top.subnodes:
							# фильтр man
							if not(self.isempty_node("man")) and (self.man.nid!= man.nid): continue
							if lvl == "man":
								result = func(man); results.append(result)
							else:
								for cat in man.subnodes:
									# фильтр cat
									if not(self.isempty_node("cat")) and (self.cat.nid!= cat.nid): continue
									if lvl == "cat":
										result = func(cat); results.append(result)
									else:
										for page in cat.subnodes:
											# фильтр page
											if not(self.isempty_node("page")) and (self.page.nid!= page.nid): continue
											if lvl == "page": 
												result = func(page); results.append(result)
										
		if msg: print(" Called " + str(len(results)) + " nodes")
		return results
		
		
"""  ------------------ class  -----------------------------------------------  """
class NodeFilter(object):
	""" topid, manid, catid, pageid - строки; topnode, mannode, catnode, pagenode - объекты Node 
	"""
	levels_list = ['site', 'top', 'man', 'cat', 'page']
	levels_index = {}
	numerator = 0
	for el in levels_list:
		levels_index[el] = numerator
		numerator += 1
	
	def __init__(self, site = None, top = None, man  = None, cat  = None, page = None, dict_filter = None):
		self.site = site; self.top = top; self.man = man; self.cat = cat; self.page = page
		""" для заполнения из strfilter
		нужны аргументы, strfilter и site или в site переносить функцию
		site.get_nodefilter()
		if isinstance(strfilter, dict): 
			self.top = strfilter["top"]
			self.man = strfilter["man"]
			self.cat = strfilter["cat"]
			self.page = strfilter["page"]
		"""
		
	def __repr__(self):
		return "".join(["filter: ", "(t)=", str(self.top), ", (m)=", str(self.man),
					", (c)=", str(self.cat), ", (p)=", str(self.page)])
					
	def __bool__(self):
		"""  проверка истинности, если объект не определен возвращает False """
		if (self.top == None) and (self.man == None) and (self.cat == None) and (self.page == None): return False
		else: return True
		
	def repr_node(self, lvl):
		""" возвращает текстовое представление атрибута (одного из top, man, cat, page)
		 для экранного виджета по его названию, заданному в виде строки. 
		 Если атрибут не установлен - возвращаем пустую строку "", иначе - node.nid """
		 
		return str(getattr(self, lvl)) if getattr(self, lvl) else ""
		
	def get_node(self, lvl):	
		if lvl in NodeFilter.levels_list:	return getattr(self, lvl)
			
	def set_node(self, lvl, node):	
		if lvl in NodeFilter.levels_list:	setattr(self, lvl, node)
		
	def next_lvl(lvl):	
		""" навигация уровням, возвращает следующий уровень,
			для top - man, для man - cat, для cat - page, для page - None """
		num_lvl = NodeFilter.levels_index.get(lvl) 
		if (num_lvl > len(NodeFilter.levels_list)-2): return None
		else: return NodeFilter.levels_list[num_lvl+1]
		
	def prev_lvl(lvl):	
		""" навигация уровням, возвращает предидущий уровень,
			для top - None, для man - top, для cat - man, для page - cat """
		num_lvl = NodeFilter.levels_index.get(lvl) 
		if (num_lvl < 1): return None
		else: return NodeFilter.levels_list[num_lvl-1]		
		
	def get_dict_filter(self):
		""" возвращает представление объекта NodeFilter в виде словаря
		dict_filter = {'top': "web", 'man': "html", "cat": "intro", "page": "links"}  """
		
		dict_filter = {'top': None, 'man': None, "cat": None, "page": None}
		"""
		dict_filter["top"] = self.top.nid if self.top else None
		dict_filter["man"] = self.man.nid if self.man else None
		dict_filter["cat"] = self.cat.nid if self.cat else None
		dict_filter["page"] = self.page.nid if self.page else None
		"""
		if self.top:
			dict_filter["top"] = self.top.nid
			if self.man:
				dict_filter["man"] = self.man.nid
				if self.cat:
					dict_filter["cat"] = self.cat.nid
					if self.page:
						dict_filter["page"] = self.page.nid
		
		return dict_filter
		
			
	def gen_link(self):
		""" генерация  ссылки типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """
		
		link = ''.join(["http://", self.site.hostname,"/", self.site.path, "/", self.site.topdir, "/"])
		if self.top:
			link = link +''.join([self.top.path, "/"])
			if self.man:
				link = link +''.join([self.man.path, "/"])
				if self.cat:
					link = link +''.join([self.site.pagedir, "/", self.cat.path, "/"])
					if self.page:
						link = link +''.join([self.page.path, self.site.pageext])  
		
		return link
	
"""  ------------------ class NodeFilter -----------------------------------------------  """

class Node(object):
	""" nid=, lvl, name, fname, path, parent, subnodes = [] 
	 в карте map.xml  
	 nid = data-id, идентификатор
	 name = data-name, название меню
	 **** runame = data-runame, русское название меню, для атрибута title **** в процессе(не реализовано)
	 fname = data-fname, полное название  
	 path = data-path, каталог или файл	 
	 """
	
	def isnode(obj):	
		""" проверка проверка принадлежности к классу Node """
		base_class_name = str(obj.__class__.__bases__[0])[Iclear.shift_str_class:-2]
		if base_class_name == 'Node': return True
		else: return False 
		
	def isvalid(obj):	
		""" проверка проверка принадлежности к классу Node """
		if (Node.isnode(obj)) and (obj.nid!=''): return True
		else: return False 
		
	def __init__(self, nid, lvl, name="", fname="", runame="", path="", parent= None, subnodes=[]):
		self.nid = str(nid)
		self.lvl = lvl
		self.name = name
		self.fname = fname if fname!= None else ""	
		self.runame = runame if runame!= None else ""	
		self.path = path
		self.parent = parent
		self.subnodes = subnodes
		if isinstance(subnodes, list)and(len(subnodes) == 0): self.subnodes = list()
		''' nid, lvl, name, path  - обязательны, являются строками и не равны нулю  '''
		
	def __repr__(self):
		return self.nid
		
	def lv0(self):
		return str(self.__class__).lower()[Iclear.shift_str_class:-2]
		
	def info(self):
		if isinstance(self.parent, Node): info = self.parent.info() + "-"
		else: info = ""
		return info + self.nid + "(" + self.lvl[0:1] + ")"
			
	def get_child_node(self, nid):
		""" получить подчиненный узел по nid """
		for node in self.subnodes:
			if node.nid == nid: return node

		
"""  ------------------ class Node -----------------------------------------------  """

class Page(Node):
	def __init__(self, nid, name="", fname="", runame="", path="", parent= None):
		super().__init__(nid = nid, name = name, fname = fname, runame = runame, path = path, parent= parent, lvl = "page")
		
	def man(self): return self.parent.parent
	def site(self): return self.man().site()
	
	def short_path(self): 	# короткий путь к page без /home/dina/www/iclear
		return os.path.join(self.site().path, self.site().topdir, self.man().parent.path,
			self.man().path, self.site().pagedir, self.parent.path, self.path + ".php")

	def full_path(self): 	# путь к page /home/dina/www/iclear/conspect/ref/web/html/pages/intro/links
			return os.path.join(self.site().hostdir, self.short_path())
			
"""  ----------------------------------------------------------------------------  """		

class Cat(Node):
	def __init__(self, nid, name="", fname="", path="", parent= None, subnodes=[]):
		super().__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, lvl = "cat")
		
	def man(self): return self.parent
	def site(self): return self.man().site()
	
	def short_path(self): 	# короткий путь к page без /home/dina/www/iclear
		return os.path.join(self.site().path, self.site().topdir, self.man().parent.path,
			self.man().path, self.site().pagedir, self.path)

	def full_path(self): 	# путь к page /home/dina/www/iclear/conspect/ref/web/html/pages/intro/links
			return os.path.join(self.site().hostdir, self.short_path())
"""  ----------------------------------------------------------------------------  """		

class Man(Node):
	def __init__(self, nid, name="", fname="", path="", parent= None, subnodes=[], logo = False):
		super().__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, lvl = "man")
		self.logo = logo
		
	def site(self): return self.parent.parent
	
	def short_path(self): 	# короткий путь к manual без /home/dina/www/iclear
		return os.path.join(self.site().path, self.site().topdir, self.parent.path, self.path)
		
	def full_path(self): 	# полный путь к manual
		full_path = os.path.join(self.site().hostdir, self.short_path())
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			raise FileNotFoundError('The file ' + full_path + ' is not present.') 
			#return False
		
	def fill(self, strfilter = None):
		""" заполняем узлы на уровне cat и page из map.xml мануала """
		tree = ET.parse(os.path.join(self.full_path(), "map.xml"))
		maproot = tree.getroot()
		uls = maproot.findall("ul")
		for ul in uls:
			if (strfilter)and(strfilter["cat"]!= "")and(strfilter["cat"]!= ul.get("data-id")): continue  # фильтр cat
			cat = Cat(nid = ul.get("data-id"), name = ul.get("data-name"), path = ul.get("data-path"),
			 parent = self)
			self.subnodes.append(cat)
			lis = ul.findall("li")
			for li in lis:
				#runame = li.get("data-runame") if 'data-runame' in li.attrib else li.get("data-fname")
				if 'data-runame' in li.attrib:
					runame1 = li.get("data-runame")
					fname1 = li.get("data-name") + " (" + runame1 + ")"
				else:
					runame1 = li.get("data-fname")
					fname1 = li.get("data-fname")
				if (strfilter)and(strfilter["page"]!= "")and(strfilter["page"]!= li.get("data-id")): continue  # фильтр page
				page = Page(nid = li.get("data-id"), name = li.get("data-name"), fname = fname1, runame = runame1,
				path = li.get("data-path"), parent = cat)
				cat.subnodes.append(page)
"""  ----------------------------------------------------------------------------  """		
class Top(Node):
	def __init__(self, nid, name="", fname="", path="", parent= None, subnodes=[]):
		super().__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, lvl = "top")
"""  ----------------------------------------------------------------------------  """

class Site(Node):
	""" 	"""
	def __init__(self, nid, name="", fname="", path="", parent= None, subnodes=[], 
		description="", strfilter = None, fill = True):
		"""  заполняем  """
		if name=="": name=nid
		if path=="": path=nid
		super().__init__(nid = nid, name = name, fname = fname, path = path, parent= parent, lvl = "site")
		self.strfilter = strfilter
		self.description = description
		self.hostpath = "/home/dina/www/"
		self.hostname = "iclear"
		self.hostdir = self.hostpath + self.hostname
		self.topdir = "ref"
		self.pagedir = "pages"
		self.phpincdir = "phpinc"
		self.pageext = ".php"
	
		self.description = description
	
		if self.strfilter == "": self.strfilter = {'top': "", 'man': "", "cat": "", "page": ""}
		
		if fill: self.fill(self.strfilter)
		else: 
			if fill == "site": self.fill_site(self.strfilter)
				
	def full_path(self): 	# путь к root сайта
		full_path = os.path.join(self.hostdir, self.path)
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			raise FileNotFoundError('The file ' + full_path + ' is not present.') 
			#return False
		
	#заполнение разбито на две части
	def fill(self, strfilter = None):
		self.fill_site(strfilter)
		self.fill_man (strfilter)
		
	def fill_site(self, strfilter = None):
		""" заполняем поле description и 
			узлы уровня top и man из map.xml сайта """
		tree = ET.parse(os.path.join(self.full_path(), "map.xml"))
		maproot = tree.getroot()
		
		nodedescr = maproot.find("descr")
		if nodedescr != None:
			self.description = nodedescr.text
		
		uls = maproot.findall("ul")
		for ul in uls:
			if (strfilter)and(strfilter["top"]!= "")and(strfilter["top"]!= ul.get("data-id")): continue  # фильтр top
			top = Top(nid = ul.get("data-id"), name = ul.get("data-name"), fname = ul.get("data-fname"),
				path = ul.get("data-path"), parent = self) 
			self.subnodes.append(top)
			lis = ul.findall("li")
			for li in lis:
				if (strfilter)and(strfilter["man"]!= "")and(strfilter["man"]!= li.get("data-id")): continue  # фильтр man
				logo = li.get("logo") if 'logo' in li.attrib else False
				man = Man(nid = li.get("data-id"), name = li.get("data-name"), fname = li.get("data-fname"),
				 path = li.get("data-path"), parent = top, logo = logo)
				top.subnodes.append(man)
				
	def fill_man(self, strfilter = None):
		""" продолжаем заполнять узлы на уровне cat и page из map.xml мануалов 
				узлы уровня top и man уже заполнены """
		for top in self.subnodes:
			for man in top.subnodes: man.fill(strfilter)
						
	def call_func_by_nodes(self, lvl, func, strfilter = None, nodefilter = None, msg = False):

		#if (strfilter == None)and(isinstance(nodefilter, NodeFilter)): strfilter = nodefilter.get_strfilter()
			
		allnodescalled = 0;
		for top in self.subnodes:
			if (strfilter)and(strfilter["top"] not in ("", None))and(strfilter["top"]!= top.nid): continue  # фильтр top
			if lvl == "top": 
				func(top); allnodescalled += 1
			else:
				for man in top.subnodes:
					if (strfilter)and(strfilter["man"] not in ("", None))and(strfilter["man"]!= man.nid): continue  # фильтр man
					if lvl == "man":
						func(man); allnodescalled += 1
					else:
						for cat in man.subnodes:
							if (strfilter)and(strfilter["cat"] not in ("", None))and(strfilter["cat"]!= cat.nid): continue  # фильтр cat
							if lvl == "cat":
								func(cat); allnodescalled += 1
							else:
								for page in cat.subnodes:
									#if (strfilter)and(strfilter["page"]!= "")and(strfilter["page"]!= page.nid): continue  # фильтр page
									if (strfilter)and(strfilter["page"] not in ("", None))and(strfilter["page"]!= page.nid): continue  # фильтр page
									if lvl == "page": 
										func(page) ; allnodescalled += 1
										
		if msg: print(" Called " + str(allnodescalled) + " nodes")
		return allnodescalled
		
	def gen_node_filter_from_dict(self, dict_filter):
		""" возвращает объект NodeFilter по представлению в виде словаря
		dict_filter = {'top': "web", 'man': "html", "cat": "intro", "page": "links"} """
		
		nodefilter = NodeFilter(site=self)
		
		if dict_filter == None: return nodefilter
		
		if (dict_filter["top"] not in ("", None)):
			for top in self.subnodes:
				if (dict_filter["top"] == top.nid):
					nodefilter.top = top
					if (dict_filter["man"] not in ("", None)):
						for man in top.subnodes:
							if (dict_filter["man"] == man.nid):
								nodefilter.man = man
								if (dict_filter["cat"] not in ("", None)):
									for cat in man.subnodes:
										if (dict_filter["cat"] == cat.nid):
											nodefilter.cat = cat
											if (dict_filter["page"] not in ("", None)):
												for page in cat.subnodes:
													if (dict_filter["page"] == page.nid):
														nodefilter.page = page
											break
								break
					break
					
		return nodefilter
		
	def gen_node_filter_from_link(self, link):
		""" генерация nodefilter по ссылке типа http://iclear/conspect/ref/soft/development/
		или http://iclear/conspect/ref/soft/development/pages/tools/git.php  """ 
		
		nodefilter = NodeFilter(site=self)
		if link == None: return nodefilter
		
		listlink = link.split(sep="/")
		
		# ['http:', '', 'iclear', 'conspect', 'ref', 'soft', 'python', 'pages', 'datatypes', 'list.php#join']
		top = listlink[5]
		man = listlink[6]
		cat = ""
		page = ""

		if len(listlink) > 8:
			cat = listlink[8]
			page = listlink[9].split(sep=".")[0]
			
		nodefilter = self.gen_node_filter_from_dict(dict_filter = {'top': top, 'man': man, "cat": cat, "page": page})
		
		return nodefilter

"""  ----------------------- class Site ------------------------------------------------  """

class Host(Node):
	
	def __init__(self, nid = None, name="", path="", subnodes=[],
		strfilter = None, fill = True):
		""" если nid не передан, по умолчанию заполняем из Iclear.hostname """
		if nid == None: nid = Iclear.hostname 
		if name == "": name = nid
		if path == "": path = nid
		super().__init__(nid = nid, name = name, path = path, lvl = "host")
		self.hostpath = "/home/dina/www/"
		#self.hostname = "iclear"
		#self.hostdir = self.hostpath + self.hostname
		self.topdir = "ref"
		self.pagedir = "pages"
		self.phpincdir = "phpinc"
		self.pageext = ".php"
		
		self.fill()
		
	def full_path(self): 	# путь к root сайта
		full_path = os.path.join(self.hostpath, self.path)
		if Tools.check_exists_file(full_path):
			return full_path
		else:
			raise FileNotFoundError('The file ' + full_path + ' is not present.') 
			#return False
		
	def fill(self, strfilter = None):
		""" заполняем узлы уровня site из map.xml хоста """
		
		mapname = os.path.join(self.full_path(), "map.xml")
		if not(Tools.check_exists_file(mapname)): return
			
		tree = ET.parse(mapname)
		maproot = tree.getroot()
		uls = maproot.findall("ul")
		for ul in uls:
			lis = ul.findall("li")
			for li in lis:
				#name = li.get("data-id")
				#print(name)
				site = Site(nid = li.get("data-id"), name = li.get("data-name"),
					fname = li.get("data-fname"), path = li.get("data-path"), parent = self) 
				self.subnodes.append(site)
			
"""  ----------------------------------------------------------------------------  """

class Tools():
	""" stdout - флаг вывода в stdout, outhandler - внешний обработчик """
	
	output_stdout = True
	output_outhandler = None
	
	@staticmethod
	def set_output(stdout= True, outhandler = None):
		Tools.output_stdout = stdout
		Tools.output_outhandler = outhandler
	
	@staticmethod
	def output(outtext, outtype = "out", stdout= True, outhandler = None):
		""" outtext - текст вывода, outtype = out/err/sys, stdout - флаг вывода в stdout, outhandle - внешний обработчик """
		
		stdout = Tools.output_stdout
		outhandler = Tools.output_outhandler
		
		if stdout: 
			if outtype == "out": print(outtext)
			if outtype == "err": print('\033[31m' + outtext + '\033[39m')
		if outhandler: outhandler(outtext, outtype)
	
	@staticmethod
	def check_exists_file(fname):
		if not(os.path.exists(fname)): 
			Tools.output(''.join(["No such file or dir ", fname]), outtype = "err")
			return False
		else:
			return True
	
	@staticmethod
	def rename_file(fname1, fname2):
		if os.path.exists(fname1): os.path.rename(fname1, fname2)
	
	@staticmethod
	def getfileslist(fdir):
		""" список описаний файлов в директории, состоит из кортежей (путь, файл)"""
		listfilesinfo = []
		for root, dirs, files in os.walk(fdir):
			for filename in files: 
				listfilesinfo.append((root, filename)) # кортеж (путь, файл)
		return listfilesinfo
		
	def getdirslist(fdir):
		""" список описаний директорий в директории, состоит из кортежей (путь, файл)"""
		listdirsinfo = []
		for root, dirs, files in os.walk(fdir):	
			for dir_name in dirs:		
				listdirsinfo.append((root, dir_name)) # кортеж (путь, dirs)
		return listdirsinfo
	
	@staticmethod
	def write_file(fname, ftext):
		try:
			with open(fname, "w") as f:
				f.write(ftext)
				#print( fname + " writed")
				Tools.output(''.join([fname, " writed"]))
				
		except IOError:
			Tools.output(''.join([fname, " file writing error"]), outtype = "err")
			return -1
			
			
			
"""  -----------------------class Tools------------------------------------------------  """
"""  -----------------------class wProc------------------------------------------------  """
class wProc():
	
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
		
		#print(mapname, "\n", maptext) 
		Tools.write_file(mapname, maptext)
	
	''' --------------------------------------------------------'''
	def gen_asidephp(man, msg = True):
		""" генерация файла aside.php на основании node Man карты сайта map.xml"""
		asidetext =  '<div><ul>\n\t'
		asidetext += '<li><span id="spanmin" onclick="resizemain()" title="menu collapse">Min</span></li>'
		asidetext += '<li><a href="/' + os.path.join(man.short_path(), "index.php") + '" id="map">Map</a></li>\n'
		asidetext += '</ul>\n\t'
		asidetext += '<ul id = "hiddenmenu">\n'
		for cat in man.subnodes:
			asidetext += ''.join(['\t<li id = "menu_', cat.nid, '"><details><summary>', cat.name, '</summary><ul>\n'])
			for page in cat.subnodes:
				''' asidetext += ''.join(['\t\t<li><a href="/', page.short_path(), '" id= "item_', page.nid, 
						'" target="_self">', page.name, '</a></li>\n']) '''
				asidetext += ''.join(['\t\t<li><a href="/', page.short_path(), '" id= "item_', page.nid, 
						'" target="_self" title="', page.runame,'">', page.name, '</a></li>\n'])
			asidetext += '\t</ul></details></li>\n'
		asidetext += '</ul></div>'
		asidename = os.path.join(man.full_path(), man.site().phpincdir, "aside.php")
		#print(asidename, "\n", asidetext)
		Tools.write_file(asidename, asidetext)
	
	''' --------------------------------------------------------'''
	def gen_headerphp(man, msg = True):
		""" генерация файла header.php на основании node Man карты сайта map.xml"""
		headertext = '<div class="wrapper">\n\
	<div class="box1"><a href="../../../../../index.php" target="_self">Home</a></div>\n\
	<div class="box2"><h1><a href="/'+man.short_path()+'/index.php">'+man.fname+'</a></h1></div>\n\
</div>'
		headername = os.path.join(man.full_path(), man.site().phpincdir, "header.php")
		#print(headername, "\n", headertext)
		Tools.write_file(headername, headertext)

	''' --------------------------------------------------------'''
	def gen_partheadphp(man, msg = True):
		""" генерация файла parthead.php на основании node Man карты сайта map.xml"""
		partheadtext = '<title>'+ man.name+'</title>\n\
<meta charset="utf-8">\n\
<meta name="robots" content="noindex">\n\
<link rel="stylesheet" type="text/css" href="../../../../../../app/styles/index.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../../app/styles/page.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../app/styles/index.css">\n\
<link rel="stylesheet" type="text/css" href="../../../../../app/styles/page.css">\n\
<script src="../../../../../../app/scripts/script.js"></script>'
		partheadname = os.path.join(man.full_path(), man.site().phpincdir, "parthead.php")
		#print(partheadname, "\n", partheadtext)
		Tools.write_file(partheadname, partheadtext)

	''' --------------------------------------------------------'''
	def gen_indexphp(man, msg = True):
		""" генерация файла index.php на основании node Man карты сайта map.xml"""

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
		indextext += '		<div class="wrapper3">\n\
			<div class="box1"><a href="../../../index.php" target="_self">Home</a></div>\n\
			<div class="box2"><h1><a href="index.php">'+man.fname+'</a></h1></div>\n\
			<div class="box3">'
		indextext += '<img src="app/logo.jpg" width="40" height="40" alt="logo">' if man.logo else ''
		indextext += '</div>\n\
		</div>\n\
'
		indextext += '	</div>\n\
	<div class="main">\n\
		<div class="aside"><?php include "phpinc/aside.php"; ?></div>\n\
		<div class="article">\n\
	<div class = "map etr">\n\
<ul>\n\
'
		for cat in man.subnodes:
			indextext += ''.join(['\t<li><details open><summary>', cat.name,'</summary><ol>\n'])
			for i in range(len(cat.subnodes)):
				page = cat.subnodes[i]
				#print(page.name)
				indextext += ''.join([ '\t\t<li><a href="/', page.short_path(), 
				'" target="_self" title="', str(i+1), '. ', page.runame,'">', page.name,'</a></li>\n'])
			indextext += '\t</ol></details></li>\n'
		indextext += '</ul>\n\
	</div></div></div>\n\
    </body>\n\
</html>\n\
'	
		indexname = os.path.join(man.full_path(), "index.php")
		#print(indexname, "\n", indextext)
		Tools.write_file(indexname, indextext)

	
	''' --------------------------------------------------------'''
	def gen_index_phpinc(node, msg = True):
		
		wProc.gen_indexphp(node, msg = msg)
		wProc.gen_asidephp(node, msg = msg)
		wProc.gen_headerphp(node, msg = msg)
		wProc.gen_partheadphp(node, msg = msg)

	''' --------------------------------------------------------'''
	def gen_root_indexphp(site):
		""" генерация файла index.php на основании карты сайта map.xml"""

		indextext = '<!DOCTYPE html>\n\
<html lang="ru">\n\
<head>\n\
	<title>'
		indextext += site.nid
		indextext += '</title>\n\
	<meta charset="utf-8">\n\
	<meta name="robots" content="noindex"/>\n\
	<link rel="stylesheet" type="text/css" href="../app/styles/root.css" />\n\
	<link rel="stylesheet" type="text/css" href="app/styles/root.css" />\n\
</head>\n\
<body>\n\
	<div class="header"><div class="wrapper3">\n\
		<div class="logo"><a href="../index.php" target="_self"><img src="app/img/icons/logo.png" width="40" height="40" alt="logo"></a></div>\n\
		<div><h1><a href="index.php">'+site.fname+'</a></h1></div>\n\
	</div></div>\n\
	<div class="main">\n'
	
		indextext += '<div class="root">\n\
		<p>'+site.description+'</p>\n\
		<div class = "map"><ul>\n\
'		
		pagecount = 0
		for top in site.subnodes:
			indextext += ''.join(['\t\t\t<li><details open><summary>', top.fname,'</summary><ol>\n'])
			for man in top.subnodes:
				extendstr = "  ("
				for cat in man.subnodes:
					extendstr += cat.nid + ", "
				extendstr += ')'
				extendstr = ""
				indextext += ''.join([ '\t\t\t\t<li><a href="/', man.short_path(), 
				'" target="_self">', man.name, '</a>', extendstr, '</li>\n'])
				
				for cat in man.subnodes:
					for page in cat.subnodes: pagecount+=1
						
			indextext += '\t\t\t</ol></details></li>\n'
		indextext += '\n\
	</ul>\n\
	</div></div></div>\n\
    </body>\n\
</html>'

		indexname = os.path.join(site.full_path(), "index.php")
		#print(indexname, "\n", indextext)
		Tools.write_file(indexname, indextext)
	
	''' --------------------------------------------------------'''
	def gen_plug_pagephp(page, msg = True):
		"""  проверка на существование - файл не перезаписывается """
		
		comments_delimiters = '\n\
<!-- ***************************************************************************************  -->\n\
<!-- =======================================================================================  -->\n\
<!--    + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +     -->\n\
<!--  - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - -  - - - - - - - - - - - -->\n\
<!--  <h3 id="header">Header <a class="selflink" href="#header"></a> </h3>  -->\n'

		
		pagename = page.full_path()
		if (os.path.exists(pagename)):
			#Tools.err_print ( pagename + " already exists")
			Tools.output(''.join([pagename, " already exists"]), outtype = "err")
			return -1
			
		fname = page.fname if page.fname!="" else page.name	
		#print("page.fname-"+page.fname +"-")

		pagetext = fileContentsNew = '<!DOCTYPE html>\n\
<html lang="ru">\n\
<head>\n\
	<?php include "../../phpinc/parthead.php"; ?>\n\
</head>\n\
<body onload="start()">\n\
	<div class="header"><?php include "../../phpinc/header.php"; ?></div>\n\
	<div class="main"><div class="aside"><?php include "../../phpinc/aside.php"; ?></div>\n\
	<div class="article">\n\
	<!--  ' + page.path + '  --> \n\
	<span id="top"></span>\n\
	<div class="goup"><a href="#top" title="Вернуться к началу страницы">^</a></div>\n\
	<!--  header -->\n'
		pagetext += ''.join(['	<h2><a href="', page.path,'.php">', fname, '</a></h2>\n'])
		pagetext += ''.join(['\n	<div class="links_list"><details><summary>Ссылки</summary><ul>\n\
		<li><a href="https://en.wikipedia.org/wiki/Test" target="_blank">wiki Test</a></li>\n\
	</ul></details></div>\n', comments_delimiters, '\n\
</div></div>\n\
</body>\n\
</html>'])
		
		#print(pagename, "\n", pagetext)
		Tools.write_file(pagename, pagetext)
		
	def gen_top_dir(man):
		""" генерация файловой структуры - gentopdir.sh """
		
		man_full_path = man.full_path()

		sh_name = os.path.join(man.site().hostpath, "service", "sh", 'gentopdir_' + man.path + '.sh')
		
		sh_text = '#!/bin/bash\n'
		sh_text += "mkdir -v "+ man_full_path + '\n'
		sh_text += "mkdir -v "+ man_full_path + '/pages\n'
		sh_text += "mkdir -v "+ man_full_path + '/phpinc\n'
		sh_text += "mkdir -v "+ man_full_path + '/app\n'
		sh_text += "mkdir -v "+ man_full_path + '/app/styles\n'
		sh_text += "mkdir -v "+ man_full_path + '/app/scripts\n'
		sh_text += "mkdir -v "+ man_full_path + '/resources\n'
		sh_text += "mkdir -v "+ man_full_path + '/resources/examples\n'
		sh_text += "mkdir -v "+ man_full_path + '/resources/img\n'
		sh_text += "mkdir -v "+ man_full_path + '/resources/books\n'
		
		for cat in man.subnodes:
			sh_text += "mkdir -v "+ man_full_path + "/pages/" + cat.path + '\n'
			 
		#print(sh_text)	
		Tools.write_file(sh_name, sh_text)	
		
		Tools.output(''.join(["chmod u+x ", sh_name]))
		
		
	''' --------------------------------------------------------'''
	def check_map(man):
		"""	проверка карты сайта map   
			все категории и страницы должны быть уникальны по id и path
			не должно быть пустых справочников (manual) и категорий(cat)"""
		
		error_found = False
		catsetpath =  set()
		catsetnid =  set()
		if (len(man.subnodes) == 0):
			error_found = True
			message = "Пустой man - " + man.info()
			Tools.output(message, outtype = "err")
			
		for cat in man.subnodes:
			if (cat.path not in catsetpath): 
				catsetpath.add(cat.path)
			else:
				error_found = True
				message = "Не уникальный cat.path - " + cat.info()
				Tools.output(message, outtype = "err")
				
			if (cat.nid not in catsetnid): 
				catsetnid.add(cat.nid)
			else:
				error_found = True
				message = "Не уникальный cat.nid - " + cat.info()
				Tools.output(message, outtype = "err")
				
			pagesetpath =  set()
			pagesetnid =  set()

			if (len(cat.subnodes) == 0):
				error_found = True
				message = "Пустой cat - " + cat.info()
				Tools.output(message, outtype = "err")
			
			for page in cat.subnodes:
				if (page.path not in pagesetpath): 
					pagesetpath.add(page.path)
				else:
					error_found = True
					message = "Не уникальный page.path - " + page.info()
					Tools.output(message, outtype = "err")
					
				if (page.nid not in pagesetnid): 
					pagesetnid.add(page.nid)
				else:
					error_found = True
					message = "Не уникальный page.nid - " + page.info()
					Tools.output(message, outtype = "err")
					
		return error_found
		
	''' --------------------------------------------------------'''
	def diff_map_by_dir(man):
		"""  сравнение карты справочника map с каталогами и файлами в /pages 
		1
		*всем страницами (page) из карты должны соответствовать файлы 
		всем каталогам (cat) из карты должны соответствовать папки 
		2
		всем файлам и каталогам на диске должны соответствовать cat и page в карте -
		не должно быть лишних файлов и каталогов на диске (не указанных в карте)
		(внутри каталогов (категорий, cat) не должно быть других каталогов 
		*в папке справочника (manual) должны быть только папки каталогов из карты)"""
		
		if wProc.check_map(man):
			return
		
		errtempdirname = "errtemp"
		
		error_found = False
		catsdir_full_path = os.path.join(man.full_path(), man.site().pagedir)
		catsdir_content = next(os.walk(catsdir_full_path))
		# в папке справочника (manual) должны быть только папки каталогов из карты)
		if (len(catsdir_content[2])>0):
			error_found = True
			message = "В папке " + man.info() + " присутствуют файлы " + str(catsdir_content[2])
			Tools.output(message, outtype = "err")
			
		catlistpath = list(map(lambda node: node.path, man.subnodes))
		for catdir in catsdir_content[1]:
			if (catdir not in catlistpath):
				error_found = True
				if (catdir == errtempdirname):
					Tools.output("Присутствует "+errtempdirname)
				else:
					message = "В папке " + catsdir_full_path + " не указанный каталог " + catdir
					Tools.output(message, outtype = "err")
			
		error_file_found = []
		for cat in man.subnodes:
			# всем каталогам (cat) из карты должны соответствовать папки
			if not(os.path.exists(cat.full_path())): 
				error_found = True
				message = "Не существует директории " + cat.info()
				Tools.output(message, outtype = "err")
			
			# всем страницами (page) из карты должны соответствовать файлы 
			for page in cat.subnodes:
				if not(os.path.exists(page.full_path())): 
					error_found = True
					message = "Не существует файла " + page.info()
					Tools.output(message, outtype = "err")
			
			pagesdir_full_path = cat.full_path()
			pagesdir_content = next(os.walk(pagesdir_full_path))
			# (внутри каталогов (категорий, cat) не должно быть других каталогов 
			if (len(pagesdir_content[1])>0):
				error_found = True
				message = "В папке " + cat.full_path() + " не указанный каталог " + str(pagesdir_content[1])
				Tools.output(message, outtype = "err")
			
			# всем файлам  на диске должны соответствовать page в карте
			pagelistpath = list(map(lambda node: node.path + ".php", cat.subnodes)) 
			for page in pagesdir_content[2]:
				if (page not in pagelistpath):
					error_found = True
					error_file_found.append((pagesdir_full_path, page))
					message = "В папке " + cat.full_path() + " не указанный файл " + page
					Tools.output(message, outtype = "err")
			
		# переносим лишние файлы в папку ошибок
		if (len(error_file_found)>0):
			message = "Файлы не указанные в карте, будут перенесены в папку pages/errtemp"
			Tools.output(message )
			import shutil
			errtempdir = os.path.join(catsdir_full_path, errtempdirname) 
			if not(os.path.exists(errtempdir)): os.mkdir(errtempdir)
			
			for f in error_file_found:
				page = f[1]
				source = os.path.join(f[0], page)
				target = os.path.join(errtempdir, page)
				#print(source, target)
				shutil.move(source, target)
		
		if (not error_found): Tools.output("Карта справочника '"+ man.fname +"' соответствует файловой структуре.")
		
"""  -----------------------class wProc------------------------------------------------  """


# "site": 'conspect', 'top': "web", 'man': "html", "cat": "intro", "page": "links"	

"""  ------------------------------   ----------------------------------------------  """
if __name__ == "__main__":
	""" сервисный запуск """
	#site = Site(nid = "healix", name="HEALIX", fill = "site")
	#gen_root_indexphp(site)
	#gen_top_dir(man)
	#host = Host(nid = "iclear", name="iclear", path="iclear")
	
 
	

