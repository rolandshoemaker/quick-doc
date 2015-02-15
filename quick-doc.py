#!/usr/bin/python3
import re, argparse

parser = argparse.ArgumentParser(description="generated markdown documentation from shell script comments")
parser.add_argument("INPUT_FILE", help="Input script to parse")
parser.add_argument("-hl", "--header-level", default=2, help="How indented is wherever you are putting this? [default: 2 (##)]")
args = parser.parse_args()

INPUT = args.INPUT_FILE
H_LEVEL = args.header_level*"#"

SYNTAX = "sh"

FUNC_START = "([a-zA-Z_]+)\(\) {"
FUNC_END = "^}$"

DESC_PRE = "# desc: "
USAGE_PRE = "# usage: "
REQUIRE_PRE = "# requires: "

CURRENT_LINE = 0

with open(INPUT, "r") as f:
	SOURCE = [l.strip("\n") for l in f.readlines()]

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

def code_block(code):
	return "```%s\n%s\n```" % (SYNTAX, "\n".join(code))

def process_block(block):
	body = "%s `%s`" % (H_LEVEL, block["name"])+"\n\n"
	body += "\n".join(block["description"])+"\n\n"
	# body += "\n".join(["\t%s" % (l) for l in block["usage"]])+"\n\n"
	body += code_block(block["usage"])+"\n\n"
	body += "%s# source\n\n" % (H_LEVEL) 
	# body += "\n".join(["\t%s" % (l) for l in block["source"]])
	body += code_block(block["source"])
	if len(block["requires"]) > 0:
		body += "\n\n%s# requires\n\n" % (H_LEVEL)
		body += "\n".join(["* [%s](#%s)" % (r, r) for r in block["requires"]])
	return body

def generate_toc(blocks):
	functions = [b["name"] for b in blocks]
	toc_body = "%s table of contents\n\n" % (H_LEVEL)
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
markdown_output.append(generate_toc(function_blocks))
for block in function_blocks:
	markdown_output.append(process_block(block))

markdown_output = "\n\n".join(markdown_output)

print(markdown_output)
