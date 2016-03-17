This repository contains a command for `setup.py` to build
a manpage for your project.

The initial code was developed for CrunchyFrog, a database query
tool for Gnome. The [frog] is now retired and [RunSQLRun] is it's
successor. The `build_manpage` command for `setup.py` is on it's
own way (right here). There's even an [old blog post] about this
script.

# Usage

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

where `output` is the destination path for the generated
manpage and `parser` is an import path pointing to a optparser
instance or a function returning such an instance.

Then run `setup.py build_manpage` to build a manpage for
your project.

## Limitations

- Works with optparse only (no argparse, yet).
- No Python 3 support (yet).


# License

This work is released under the terms of the Apache License v2.0.
See LICENSE for details.

[frog]: http://crunchyfrog.googlecode.com/svn/
[RunSQLRun]: https://github.com/andialbrecht/runsqlrun
[old blog post]: https://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/
