#!/usr/bin/python3
import sys, re, argparse

parser = argparse.ArgumentParser(description="generate markdown documentation from quick shell script comments")
parser.add_argument("-i", "--input", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="Input script to parse")
parser.add_argument("-o", "--output", nargs="?", type=argparse.FileType("w"), default=sys.stdout, help="Where to output the Markdown")
parser.add_argument("-hl", "--header-level", default=2, help="How indented is wherever you are putting this? [default: 2 (##)]")
parser.add_argument("-nt", "--no-toc", action="store_true", default=False, help="Don't generate a table of contents.")
args = parser.parse_args()

INPUT = args.input
OUTPUT = args.output
H_LEVEL = args.header_level*"#"

SYNTAX = "sh"

FUNC_START = "([a-zA-Z_]+)\(\) {"
FUNC_END = "^}$"

DESC_PRE = "# desc: "
USAGE_PRE = "# usage: "
REQUIRE_PRE = "# requires: "

CURRENT_LINE = 0

SOURCE = [l.strip("\n") for l in INPUT.readlines()]

def blank_line(line_num):
	return SOURCE[line_num].strip() == ""

def preamble_line(line_num):
	return SOURCE[line_num].startswith("# ")

def get_preamble(start_line):
	preamble = []
	for line_num in range(start_line, 0, -1):
		if preamble_line(line_num):
			preamble.append(SOURCE[line_num])
		if blank_line(line_num):
			break
	preamble.reverse()
	return preamble	

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

def find_func_end(start_line):
	for line_num in range(start_line, len(SOURCE)-1):
		if re.match(FUNC_END, SOURCE[line_num]):
			return line_num+1

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

function_blocks = []

for S_LNUM in range(0, len(SOURCE)):
	function = re.search(FUNC_START, SOURCE[S_LNUM])
	if function:
		func_name = function.groups()[0]
		preamble = get_preamble(S_LNUM)
		desc, usage, requires = dissemble_preamble(preamble)
		func_end = find_func_end(S_LNUM)
		function_blocks.append({
			"name": func_name,
			"description": desc,
			"usage": usage,
			"requires": requires,
			"source": SOURCE[S_LNUM:func_end]
		})

markdown_output = []
if not args.no_toc:
	markdown_output.append(generate_toc(function_blocks))
for block in function_blocks:
	markdown_output.append(process_block(block))

markdown_output = "\n\n".join(markdown_output)

OUTPUT.write(markdown_output)
