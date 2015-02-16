# `quick-doc.py`

`quick-doc.py` is a super simple comment based *Markdown* documentation generator
writen in *Python*. Currently it only supports `sh` but in the future I might
extend it into different languages if I need to quickly document something else...

## Usage

You can either pipe a file to quick-doc.py and then redirect the output somewhere
yourself or you can specify input and/or output files using the `-i` and `-o` arguments.

	$ ./quick-doc.py -h
	usage: quick-doc.py [-h] [-i [INPUT]] [-o [OUTPUT]] [-hl HEADER_LEVEL]
	
	generate markdown documentation from quick shell script comments
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -i [INPUT], --input [INPUT]
	                        Input script to parse
	  -o [OUTPUT], --output [OUTPUT]
	                        Where to output the Markdown
	  -hl HEADER_LEVEL, --header-level HEADER_LEVEL
	                        How indented is wherever you are putting this?
	                        [default: 2 (##)]
	  -nt, --no-toc         Don't generate a table of contents.

## Comment format

```sh
# desc: this is the description, any *markdown* can be
# desc: put here since we are just passing it through
# desc: as markdown!
# usage: function "argument" [optional argument]
# requires: required_function another_required
a_function() {
        echo "woop woop"
}
```

This script renders out to the following markdown

### `a_function`

this is the description, any *markdown* can be put here since we are just
passing it through as markdown!

#### source

```sh
a_function() {
        echo "woop woop"
}
```

#### requires

* required_function
* another_required
