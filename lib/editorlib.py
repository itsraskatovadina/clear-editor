#! /usr/bin/python3

class EditLib(object):
	
	def capital_first_letter(txt):
		lines = txt.split('\n')
		out_lines = []
		for line in lines:
			out_lines.append(line.strip().capitalize())
		return '\n'.join(out_lines)
		
	def remove_empty_lines(txt):
		lines = txt.split('\n')
		out_lines = []
		for line in lines:
			if line:	
				out_lines.append(line)
		return '\n'.join(out_lines)
	
	def	replace_entity(txt):
		txt = txt.replace("&", "&amp;")
		txt = txt.replace("<", "&lt;")
		txt = txt.replace(">", "&gt;")
		return txt  
		
	def	wrap(txt, tag = ''):
		if tag == 'b':
			txt = "<b>"+txt+"</b>"
		elif tag == 'div':
			txt = "<div>"+txt+"</div>"
		elif tag == 'span':
			txt = "<span>"+txt+"</span>"
		elif tag == 'p':
			if (txt.count('\n')==0):
				txt = "<p>"+txt+"</p>"
			else:
				lines = txt.split('\n')
				txt = ""
				for i in lines[:]:
					# пустые строки не оборачиваем
					if (len(i.strip()) > 0):
						ilstrip = i.lstrip()
						# если в строке есть лидирующие пробелы - оставляем их перед тегом
						if (i == ilstrip):
							txt = txt +"<p>"+i+"</p>"+'\n'
						else:
							lenprefix = len(i)-len(ilstrip)
							txt = txt + i[0:lenprefix] + "<p>"+ilstrip+"</p>"+'\n'
					else:
						txt = txt +'\n'
				txt =  txt[:-1] # последний перенос лишний
		else:
			print('not implemented')	
		return txt
		
	def make_list(txt):
		''' формируем список '''
		lines = []
		lines = txt.split('\n')
		outtxt = "<ul>\n"
		for i in lines[:]:
			s = i.strip()
			if (len(s) > 0):
				outtxt = outtxt + "\t<li>"+i.strip()+"</li>\n"
		outtxt = outtxt + "</ul>"
		return outtxt
