#!/usr/bin/python3
import sys, re, argparse

SYNTAX = "sh"

FUNC_START = "([a-zA-Z_]+)\(\) {"
FUNC_END = "^}$"

DESC_PRE = "# desc: "
USAGE_PRE = "# usage: "
REQUIRE_PRE = "# requires: "

CURRENT_LINE = 0

def dissemble_preamble(preamble):
	description = []
	usage = []
	requirements = []
	for p in preamble:
		if p.startswith(DESC_PRE):
			description.append(p[len(DESC_PRE):])
		elif p.startswith(USAGE_PRE):
			usage.append(p[len(USAGE_PRE):])
		elif p.startswith(REQUIRE_PRE):
			requirements += p[len(REQUIRE_PRE):].split(" ")
	return description, usage, requirements

class ShellDoc():
	def __init__(self, source, pos=0):
		self.ast = []
		self.source = source
		self.pos = pos
		self.end = len(self.source)-1

	def blank_line(self):
		return self.source[self.pos].strip() == ""

	def preamble_line(self):
		return self.source[self.pos].startswith("# ")

	def get_preamble(self):
		preamble = []
		start_pos = self.pos
		while True:
			if self.preamble_line():
				preamble.append(self.source[self.pos])
			if self.blank_line():
				break
			self.pos -= 1
		self.pos = start_pos
		preamble.reverse()
		return dissemble_preamble(preamble)

	def find_func_end(self):
		start_pos = self.pos
		while True:
			if re.match(FUNC_END, self.source[self.pos]):
				end_pos = self.pos+1
				self.pos = start_pos
				return end_pos
			self.pos += 1

	def process_line(self):
		function = re.search(FUNC_START, self.source[self.pos])
		if function:
			desc, usage, requires = self.get_preamble()
			func_end = self.find_func_end()
			self.ast.append({
				"name": function.group(1),
				"description": desc,
				"usage": usage,
				"requires": requires,
				"source": self.source[self.pos:func_end]
			})
			self.pos = func_end
		else:
			self.pos += 1

	def parse(self):
		while self.pos < self.end:
			self.process_line()
		return self.ast

def code_block(code, lang=SYNTAX):
	return "```%s\n%s\n```" % (lang, "\n".join(code))

def generate_toc(blocks, indent):
	functions = [b["name"] for b in blocks]
	toc_body = "%s Table of Contents\n\n" % (indent)
	toc_body += "\n".join(["* [`%s`](#%s)" % (f, f) for f in functions])
	return toc_body

def render_block(block, indent):
	body = "%s `%s`" % (indent, block["name"])+"\n\n"
	if len(block["description"]) > 0:
		body += "\n".join(block["description"])+"\n\n"
	if len(block["usage"]) > 0:
		body += code_block(block["usage"])+"\n\n"
	body += "%s# Source\n\n" % (indent) 
	body += code_block(block["source"])
	if len(block["requires"]) > 0:
		body += "\n\n%s# Requires\n\n" % (indent)
		body += "\n".join(["* [`%s`](#%s)" % (r, r) for r in block["requires"]])
	return body

def render(blocks, indent, no_toc):
	output = []
	if not no_toc:
		output.append(generate_toc(blocks, indent))
	for block in blocks:
		output.append(render_block(block, indent))
	return "\n\n".join(output)

def run():
	parser = argparse.ArgumentParser(description="generate markdown documentation from quick shell script comments")
	parser.add_argument("-i", "--input", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="Input script to parse")
	parser.add_argument("-o", "--output", nargs="?", type=argparse.FileType("w"), default=sys.stdout, help="Where to output the Markdown")
	parser.add_argument("-hl", "--header-level", default=2, help="How indented is wherever you are putting this? [default: 2 (##)]")
	parser.add_argument("-nt", "--no-toc", action="store_true", default=False, help="Don't generate a table of contents")
	args = parser.parse_args()

	source = [l.strip("\n") for l in args.input]

	h_level = args.header_level*"#"

	function_blocks = ShellDoc(source).parse()
	markdown_output = render(function_blocks, h_level, args.no_toc)
	
	args.output.write(markdown_output)

if __name__ == "__main__":
	run()