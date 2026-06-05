#! /usr/bin/python3

import copy
from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.formatter import HTMLFormatter

'''
import xml.etree.ElementTree as ET
import os, os.path
import sys 
'''
if __name__ == "__main__":
	""" сервисный запуск """
	import iclear as iclib
	from mintreelib import TNode 

else:
	import lib.iclear as iclib
	from lib.mintreelib import TNode

# узел HTML, в nid записываем имя тега
class NodeHTML(TNode):
	def __init__(self, nid, attrid=None, innertxt=None):
		super(__class__, self).__init__(nid)
		self.attrid = attrid
		self.innertxt = innertxt
		
	def __repr__(self):
		return "".join([self.nid,  ", id: ", str(self.attrid), ", intxt: ", str(self.innertxt)])
		
	def info(self):
		return "".join([self.nid, ", lvl:", str(self.lvl), ", id: ", str(self.attrid), ", intxt: ", str(self.innertxt)])
		
	@staticmethod
	def create(nid, attrid=None, innertxt=None, parent=None, children=None):  
		node = NodeHTML(nid, attrid, innertxt)
		if parent: node.set_parent(parent)
		if children: node.add_children(children)
		return node
		
class htmlSrv():
	''' --------------------  content_list  ------------------------------------'''
	def get_head_tree(page_abs_path, start_h_level=3, msg = True):
		""" получаем  дерево из тэгов "h1", "h2", "h3", "h4", "h5", "h6"
			start_h_level - уровень заголовка с которого начинаем генерировать содержание (обычно это 3 (h3)),
			заголовки с классом nocontents пропускаем.
			Допустимы ситуации, когда после h3 идет сразу h5, то есть разрыв в порядке уровня вложенности  """
			
		tag_all_head_list = ["h1", "h2", "h3", "h4", "h5", "h6"]
		tag_head_list = tag_all_head_list[start_h_level - 1:]
		
		with open(page_abs_path, "r") as file_handler:
			fileContents = file_handler.read()
			pagesoup = BeautifulSoup(fileContents, 'lxml')
		
		# формируем список заголовков
		head_list = []
		for elm in pagesoup.find_all(tag_head_list):
			if ((elm.attrs.get('class')!= None) and (elm.attrs.get('class')[0] == "nocontents")):
				continue	# заголовки с классом nocontents пропускаем
			elmid = str(elm['id']) if elm.has_attr('id') else ""
			head_list.append(dict([('name', elm.name), ('attrid', elmid), ('innertxt', elm.get_text().strip())]))
		
		#for i in head_list: print (i) # debugging
		
		# формируем дерево из заголовков с учетом возможных разрывов в порядке уровня вложенности
		# на следующем этапе из дерева будет сформирован многоуровневый вложенный список
		level = start_h_level;
		head_tree = NodeHTML("ul")
		currentgroup = head_tree # текущая группа
		
		for elm in head_list:
			currentlevel = level	# запоминаем текущий уровень
			level = int(elm.get("name")[1:])  # уровень элемента
			# обрабатываем возможную смену уровня вложенности (чем больше level, тем ниже уровень)
			difference = level - currentlevel
			if difference != 0:		# это условие лишнее
				# если уровень заголовка понижается (difference > 0) 
				# текущей группой становится первый потомок ul последнего потомка прошлой группы,
				# если последнего потомка прошлой группы нет (разрыв в порядке уровня вложенности) - открываем новый список (возможно несколько раз)
				while difference > 0:
					if (currentgroup.size() > 0): 
						lastchild = currentgroup.children[currentgroup.size() - 1] # последний потомок
						newgroup = NodeHTML.create("ul", parent = lastchild) # последний потомок
					else:
						interim = NodeHTML.create("ul", parent = currentgroup)
						newgroup = NodeHTML.create("ul", parent = interim)
					currentgroup = newgroup
					
					difference -= 1
				# если уровень заголовка повышается - возврат в соответствующий родительский список  
				while difference < 0:	
					# возврат на два уровня вверх - это закрытие тегов ul и li(ul при разрыве)
					currentgroup = currentgroup.parent.parent
					difference += 1 
			
			# создаем элемент в текущем списке
			newleaf = NodeHTML.create("li", elm.get("attrid"), elm.get("innertxt"),parent = currentgroup)

		return head_tree
		
	def get_content_list(page_abs_path, start_h_level=3, msg = True, pagepath = None):
		
		head_tree = htmlSrv.get_head_tree(page_abs_path)
		#head_tree.render_info()
		# генератор вложенного списка BeautifulSoup не имеет смысла
		# потому что его невозможно корректно напечатать средствами BeautifulSoup
		def render_nested_list(root, pagepath = None):
			intxt = ""
			if (root.nid == "li"):
				linkhref = "".join(['#', (str(root.attrid).strip() if (root.attrid) else "")])
				# формируем длинные ссылки, если указан pagepath
				if pagepath: linkhref = str(pagepath) + linkhref
				intxt = "".join(['<a href="', linkhref, '">',
					(str(root.innertxt).strip() if (root.innertxt) else ""), '</a>'])
			if (root.size() == 0): 
				outtxt = "\t"*root.lvl + "<"+root.nid+">" + intxt + "</"+root.nid+">\n"
			else:
				outtxt = "\t"*root.lvl + "<"+root.nid+">" + intxt + "\n" 
				for tag in root.children:
					outtxt = outtxt + render_nested_list(tag, pagepath)
				outtxt = outtxt + "\t"*root.lvl + "</"+root.nid+">\n"
			return outtxt
			
		outtext = render_nested_list(head_tree, pagepath)
		#print(outtext)
		return outtext
		
	def wrap_content_list(outtext, header = None):
		"""  оборачиваем в content_list и сдвигаем """
		inlines = outtext.split('\n')
		outlines = []
		summaryTxt = header if header else 'Содержание'
		outlines.append('\t<div class="content_list"><details><summary>'+summaryTxt+'</summary>\n')
 
		for i in range(0, len(inlines)-1):
			#outlines.append('\t' + inlines[i] + '\n')
			outlines.append("".join(['\t', inlines[i], '\n']))
			#outlines[i + 1] = '\t' + outlines[i] + '\n'
		outlines.append('\t</details></div>')
		#outlines[len(outlines)-2] = '\t</details></div>'
		outtext = ''.join(outlines)
		return outtext
		
	def get_page_content_list(page, start_h_level=3, msg = False):
		"""  получаем  content_list для одной отдельной страницы, ссылки внутренние """
		outtext = htmlSrv.get_content_list(page.full_path(), start_h_level, msg = False)
		outtext = htmlSrv.wrap_content_list(outtext)
		return outtext
		
	def get_cat_content_list(cat, start_h_level=3, msg = True, pagepath = None):
		"""  получаем  content_list для нескольких страниц, ссылки внешние (в параметре pagepath указан путь ) """
		outtext = ""
		for page in cat.subnodes:
			outtext = outtext + '<p><b>' + page.fname + '</b></p>\n'
			outtext = outtext + htmlSrv.get_content_list(page.full_path(), msg = False, pagepath = page.path + '.php') + '\n'
		outtext = htmlSrv.wrap_content_list(outtext)
		return outtext
		
	''' ------------------------  validator   --------------------------------'''
	def validator_page_expat(pageContents, stdout, outhandler):
		from xml.parsers.expat import ParserCreate, ExpatError, errors

		wProc.validator_page_expat.lastnode = ""
	
		def start_element(name, attrs): wProc.validator_page_expat.lastnode = name

		p = ParserCreate()
		p.StartElementHandler = start_element
		
		errmess = False
		
		try:
			p.Parse(pageContents)
			#print("No Errors")
		except ExpatError as err:
			lines = pageContents.split('\n')
			#errline = lines[err.lineno-1][err.offset-5:err.offset+5]
			errline = ""
			#errline = lines[err.lineno-1].strip()
			errmess = "".join(["Error:", errors.messages[err.code], ' row:', str(err.lineno), ' col:', str(err.offset),
				' tag:', wProc.validator_page_expat.lastnode,' line:', errline])
		finally:
			return errmess
				
	def validator_page_html5lib(pageContents, stdout, outhandler):
		import html5lib
		
		pageContents = pageContents.replace('<?php include "../../phpinc/parthead.php"; ?>', '')
		pageContents = pageContents.replace('<?php include "../../phpinc/header.php"; ?>', '')
		pageContents = pageContents.replace('<?php include "../../phpinc/aside.php"; ?>', '')
		pageContents = pageContents.replace('<!--  --------------------------  -->', '')
		
		html5parser = html5lib.HTMLParser(strict = True)
		errmess = False
		try:
			htree = html5parser.parse(pageContents)
		except html5lib.html5parser.ParseError as err:  
			errmess = "".join(["Error:", str(html5parser.errors)])
		finally:
			return errmess
			
	def validator(nodnav, msg = True, stdout= True, outhandler = None):
		
		def validator_page(page, stdout, outhandler):
			
			f = open(page.full_path(), "r")
			pageContents = f.read()
			f.close()
			#res = wProc.validator_page_expat(pageContents, stdout = stdout, outhandler = outhandler)
			res = htmlSrv.validator_page_html5lib(pageContents, stdout = stdout, outhandler = outhandler)			
			if res:
				errmess = "".join(["http://iclear/", page.short_path(), " - ", res])
				iclib.Tools.output(errmess, stdout = stdout, outhandler = outhandler)
				
		results = nodnav.call_func_by_nodes("page",
			lambda node: validator_page(node, stdout = stdout, outhandler = outhandler))
			
		iclib.Tools.output("Called "+ str(len(results))+" nodes", stdout = stdout, outhandler = outhandler)
		
	''' --------------------------------------------------------'''
	def find_html_class(nodnav, msg = True, stdout= True, outhandler = None):
		
		#classname = "basic" "alert"
		classname = "basic"
		
		def find_html_class_in_page(page, stdout, outhandler ):
			f = open(page.full_path(), "r")
			fileContents = f.read()
			lines = fileContents.split('\n')
			soup = BeautifulSoup(fileContents, 'html.parser')
			for elm in soup.body.descendants: #перебрать всех потомков
				if isinstance(elm, Tag):
					if ((elm.attrs.get('class')!= None)and
						(len(elm.attrs.get('class')) == 0)): print(page.short_path())
							
					if ((elm.attrs.get('class')!= None)and
						(elm.attrs.get('class')[0] == classname)):
							outmess = "".join(["http://iclear/", page.short_path(),
								' line:', str(elm.sourceline), ' pos:', str(elm.sourcepos),' str:',
								wSrv.replace_entity(lines[elm.sourceline-1])])
							Tools.output(outmess , stdout = stdout, outhandler = outhandler)
			
		results = nodnav.call_func_by_nodes("page",
			lambda node: find_html_class_in_page(node, stdout = stdout, outhandler = outhandler))
			
		Tools.output("Called "+ str(len(results))+" nodes", stdout = stdout, outhandler = outhandler)
						

	''' --------------------------------------------------------'''
	def gen_view_resources_site(path):
	
		import os, json
		
		def is_image_file(filename):
			image_extensions = ( '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico')
			return filename.lower().endswith(image_extensions)

		def build_tree(path, name=None, level=0):
			"""Рекурсивно строит дерево каталогов"""
			if name is None:
				name = os.path.basename(path)
			item = { 'name': name, 'path': path, 'level': level }
			
			if os.path.isdir(path):
				item['type'] = 'directory'
				item['children'] = []
				try:
					for entry in os.listdir(path):
						full_path = os.path.join(path, entry)
						child_item = build_tree(full_path, entry, level+1)
						item['children'].append(child_item)
				except PermissionError:
					item['error'] = 'Permission denied'
			else:
				item['type'] = 'file'
				item['size'] = os.path.getsize(path)
			return item
		
		def render_nested_list(root):

			if (root['type'] == "file"):
				# file
				liinnertxt = "".join(['<a href="', root['path'], '" target="_blank">',
					(root['name'] + " (" + str(root['size'])), ')</a>'])
				
				if is_image_file(root["name"]):
					liinnertxt = (liinnertxt + 
					"".join(['<img src="', root["path"],'" width = "50" height = "30" title ="' + root["name"] + '">']))
				
				outtxt = "\t"*root['level'] + "<li>" + liinnertxt + "</li>\n"
			else:
				# directory
				outtxt = "\t"*root['level'] + "<li><b>" + root['name'] + "</b></li>"+ "<ul>" + "\n" 
				# сначала обход вложенных directory, затем вложенных file
				for child in root['children']:
					if (child['type'] == "file"):
						outtxt = outtxt + render_nested_list(child)
				for child in root['children']:
					if (child['type'] == "directory"):
						outtxt = outtxt + render_nested_list(child)

				outtxt = outtxt + "\t"*root['level'] + "</ul>\n"
				
			return outtxt
		
		if not os.path.isdir(path):
			outtxt = "Папка не существует"
		else:
			tree = build_tree(path)
			if (len(tree) > 0):
				outtxt = "<ul>" + render_nested_list(tree) + "</ul>"
			else: 
				outtxt = "Папка пуста"
			
		return outtxt
			
	''' --------------------------------------------------------'''
	def gen_view_man(man):
		
		import os.path
		
		viewname = os.path.join(man.full_path(), "view.html")

		respathname = os.path.join(man.full_path(), "resources")
		resources_content = htmlSrv.wrap_content_list(htmlSrv.gen_view_resources_site(respathname), "Resources")
		
		man.cats = len(man.subnodes)
		man.pages = 0
		for cat in man.subnodes:
			cat.pages = len(cat.subnodes)
			man.pages += cat.pages		 
				
		mantext = ('<p>'+man.name+' (cats-' + str(man.cats)+ ', pages-' + str(man.pages)+ ')</p>\n')
		
		mantext = mantext  + resources_content + "\n"
				
		viewtext = '<!DOCTYPE html>\n\
	<html lang="ru">\n\
	<head>\n\
		<title>view_'+man.nid+'</title>\n\
		<meta charset="utf-8">\n\
		<meta name="robots" content="noindex"/>\n\
		<link rel="stylesheet" type="text/css" href="app/styles/view.css" />\n\
	</head>\n\
	<body>\n'
		viewtext += viewtext + '<p>' + mantext +'</p></body>\n\
	</html>'
	
		iclib.Tools.write_file(viewname, viewtext)
			
	''' --------------------------------------------------------'''
	def gen_view_site(site):
		import os.path
		
		viewname = os.path.join(site.full_path(), "view.html")
		
		respathname = os.path.join(site.full_path(), "resources")
		resources_content = htmlSrv.wrap_content_list(htmlSrv.gen_view_resources_site(respathname), "Resources")
		topstxt  = ""
						
		site.tops = len(site.subnodes)
		site.mans = 0
		site.cats = 0
		site.pages = 0
		
		for top in site.subnodes:
			manstxt = " - "
			top.mans = len(top.subnodes)
			top.cats = 0
			top.pages = 0
			site.mans += top.mans
			for man in top.subnodes:
				man.cats = len(man.subnodes)
				man.pages = 0
				top.cats += man.cats
				site.cats += man.cats
				for cat in man.subnodes:
					cat.pages = len(cat.subnodes)
					man.pages += cat.pages
					
				htmlSrv.gen_view_man(man)
				
				linkman = "".join(['<a href="', os.path.join(man.full_path(), "view.html"), '" target="_blank">',
				 man.name, ' (cats-', str(man.cats), ' (pages-', str(man.pages), ')</a>'])
				manstxt = manstxt + linkman +', '
				
				top.pages += man.pages
			site.pages += top.pages
			
			topstxt = topstxt + '<li>'+ top.name+' (mans-'+str(top.mans)+', cats-'+str(top.cats)+ ', pages-'+str(top.pages)+ ')'+manstxt[:-2]+'</li>\n'
		
		sitetext = ('<p class="site">'+site.name+' (tops-'+str(site.tops)+
			', mans-'+str(site.mans)+', cats-'+str(site.cats)+ ', pages-'+str(site.pages)+ ')</p>\n' +
			'<ul>'+topstxt+'</ul>\n')
			
		sitetext = sitetext  + resources_content + "\n"
			
		viewtext = '<!DOCTYPE html>\n\
	<html lang="ru">\n\
	<head>\n\
		<title>view_'+site.nid+'</title>\n\
		<meta charset="utf-8">\n\
		<meta name="robots" content="noindex"/>\n\
		<link rel="stylesheet" type="text/css" href="app/styles/view.css" />\n\
	</head>\n\
	<body>\n'+ sitetext+' </body>\n\
	</html>'
	
		iclib.Tools.write_file(viewname, viewtext)
		
	''' --------------------------------------------------------'''
	def get_links_page_bs(page):
		""" чтение php файла с помощью BeautifulSoup и печать тегов <link> <a> <img> с внутренними ссылками
			циклические ссылки на yourself и внешние ссылки http:// https:// пропускаются
			если check_exist = True оставляем только теги, которые ссылаются на несуществующие файлы"""
			
		import os.path
		#if "bs4" not in sys.modules: from bs4 import BeautifulSoup
			
		check_exist = True
		page_full_path = page.full_path()

		f = open(page.full_path(), "r")
		fileContents = f.read()
		soup = BeautifulSoup(fileContents, 'lxml')

		man = page.man()
		cat = page.parent
		cat_full_path = cat.full_path()
		
		for el in soup.find_all('link'):
			href = el['href'].strip()
			if href[0:7] == "http://": continue
			if href[0:8] == "https://": continue
			#if check_exist: Tools.check_exists_file(cat_full_path + "/" + href)

		for el in soup.find_all('a'):
			href = el['href'].strip()
			if href == page_full_path: continue  # ссылка на yourself
			if href[0] == "#": continue						# ссылка на yourself
			if href[0:7] == "http://": continue
			if href[0:8] == "https://": continue
			#if check_exist: Tools.check_exists_file(cat_full_path + "/" + href)
			
		for el in soup.find_all('img'):
			href = el['src'].strip()
			if href[0:7] == "http://": continue
			if href[0:8] == "https://": continue
			 
			if check_exist: iclib.Tools.check_exists_file(os.path.abspath(os.path.join(cat_full_path, href)))


	''' --------------------------------------------------------'''
	def replace_text(nodnav, msg = True, stdout= True, outhandler = None):
		""" замена текста """
		oldtxt = '<div class = "basic">'
		newtxt = '<div class = "term">'
		
		def replace_text_in_page(page, stdout, outhandler ):

			f = open(page.full_path(), "r")
			fileContents = f.read()
			f.close()

			if fileContents.find(oldtxt)>-1:
				# копия на проверку
				f = open(page.full_path()[:-4]+'1.php', "w")
				f.write(fileContents) #запись
				f.close()
				text = fileContents.replace(oldtxt, newtxt, 1)
				f = open(page.full_path(), "w")
				f.write(text) #запись
				f.close()
				
				outmess = "".join(["replace_text  http://iclear/", page.short_path()])
				Tools.output(outmess , stdout = stdout, outhandler = outhandler)

			
		results = nodnav.call_func_by_nodes("page",
			lambda node: replace_text_in_page(node, stdout = stdout, outhandler = outhandler))
			
		Tools.output("Called "+ str(len(results))+" nodes", stdout = stdout, outhandler = outhandler)
		
if __name__ == "__main__":
	""" сервисный запуск """
	page_full_path = '/home/dina/www/iclear/conspect/ref/soft/python/pages/datatypes/str.php'
	htmlSrv.get_page_content_list(page_full_path)
		
