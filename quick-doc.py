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
		self.end = len(self.source)

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
		for line_num in range(self.pos, self.end):
			if re.match(FUNC_END, self.source[line_num]):
				return line_num+1

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

def process_block(block):
	body = "%s `%s`" % (H_LEVEL, block["name"])+"\n\n"

	if len(block["description"]) > 0:
		body += "\n".join(block["description"])+"\n\n"

	if len(block["usage"]) > 0:
		body += code_block(block["usage"])+"\n\n"

	body += "%s# Source\n\n" % (H_LEVEL) 
	body += code_block(block["source"])

	if len(block["requires"]) > 0:
		body += "\n\n%s# Requires\n\n" % (H_LEVEL)
		body += "\n".join(["* [`%s`](#%s)" % (r, r) for r in block["requires"]])
	return body

def generate_toc(blocks):
	functions = [b["name"] for b in blocks]
	toc_body = "%s Table of Contents\n\n" % (H_LEVEL)
	toc_body += "\n".join(["* [`%s`](#%s)" % (f, f) for f in functions])
	return toc_body

def render(blocks):
	output = []
	if not args.no_toc:
		output.append(generate_toc(blocks))
	for block in blocks:
		output.append(process_block(block))
	return "\n\n".join(output)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="generate markdown documentation from quick shell script comments")
	parser.add_argument("-i", "--input", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="Input script to parse")
	parser.add_argument("-o", "--output", nargs="?", type=argparse.FileType("w"), default=sys.stdout, help="Where to output the Markdown")
	parser.add_argument("-hl", "--header-level", default=2, help="How indented is wherever you are putting this? [default: 2 (##)]")
	parser.add_argument("-nt", "--no-toc", action="store_true", default=False, help="Don't generate a table of contents")
	args = parser.parse_args()

	OUTPUT = args.output
	SOURCE = [l.strip("\n") for l in args.input]

	H_LEVEL = args.header_level*"#"

	sh_parser = ShellDoc(SOURCE)

	function_blocks = sh_parser.parse()

	markdown_output = render(function_blocks)
	
	OUTPUT.write(markdown_output)
