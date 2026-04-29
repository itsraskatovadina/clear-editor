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
