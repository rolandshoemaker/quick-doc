# `quick-doc.py`

`quick-doc.py` is a super simple comment based *Markdown* documentation generator
writen in *Python*. Currently it only supports `sh` but in the future I might
extend it into different languages if I need to quickly document something else...

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
