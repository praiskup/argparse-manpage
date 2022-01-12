# Usage (DEPRECATED, USE BUILD\_MANPAGES INSTEAD OF BUILD\_MANPAGE)

Download `build_manpage.py` and place it somewhere where Python can
find it.

In your `setup.py` add:

```python
[...]
from build_manpage import build_manpage

setup(
  [...]
  cmdclass={'build_manpage': build_manpage}
)
```

In your `setup.cfg` add:

```
[build_manpage]
output=data/mymanpage.1
parser=myapp.somemod:get_parser
```

It's also possible to specify filename to use:

```
[build_manpage]
output=data/mymanpage.1
parser=UNUSED:get_parser
parser-file=example.py
```

The `output` is the destination path for the generated
manpage and `parser` is an import path pointing to a optparser
instance or a function returning such an instance.
Note that this doesn't work with `argparse` module.  Please use
`build_manpages` (not `build_manpage`) to have argparse support.

Then run `setup.py build_manpage` to build a manpage for
your project.
