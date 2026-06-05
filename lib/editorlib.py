#! /usr/bin/python3

class EditLib():
	
	@staticmethod
	def capital_first_letter(txt):
		lines = txt.split('\n')
		out_lines = []
		for line in lines:
			out_lines.append(line.strip().capitalize())
		return '\n'.join(out_lines)
		
	@staticmethod
	def remove_empty_lines(txt):
		lines = txt.split('\n')
		out_lines = []
		for line in lines:
			if line:	
				out_lines.append(line)
		return '\n'.join(out_lines)
		
	@staticmethod
	def	replace_entity(txt):
		txt = txt.replace("&", "&amp;")
		txt = txt.replace("<", "&lt;")
		txt = txt.replace(">", "&gt;")
		return txt  
		
	@staticmethod
	def	wrap(txt, tag = ''):
		if tag == 'p':
			''' We wrap each line separately, we do not wrap empty lines,
			  if there are leading spaces in the line, we leave them before the opening tag.  '''
			if txt.count('\n') == 0:
				txt = "<p>" + txt + "</p>"
			else:
				lines = txt.split('\n')
				result = []
				for i in lines:
					if len(i.strip()) > 0:
						ilstrip = i.lstrip()
						if i == ilstrip:
							result.append("<p>" + i + "</p>")
						else:
							lenprefix = len(i) - len(ilstrip)
							result.append(i[:lenprefix] + "<p>" + ilstrip + "</p>")
					else:
						result.append('')
				txt = '\n'.join(result)
		else:
			txt = f'<{tag}>{txt}</{tag}>'
		return txt
		
	@staticmethod
	def make_list(txt):
		lines = txt.split('\n')
		result = ["<ul>"]
		for i in lines:
			s = i.strip()
			if len(s) > 0:
				result.append("\t<li>" + s + "</li>")
		result.append("</ul>")
		return '\n'.join(result)

