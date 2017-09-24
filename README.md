# Automatically build manpage from argparse

This repository contains a command for `setup.py` to build
a manpage for your project.

The initial code was developed for CrunchyFrog, a database query tool for Gnome.
The [frog] is now retired and [RunSQLRun] is it's successor.  Then, the
`build_manpage` command was developed in [andialbrecht] and edited slightly
in [gabrielegiammatteo].  There's even an [old blog post] about this command.

Since some useful work has been done in [python pull request], the code from the
PR has been used here too (with a belief that upstream merges this, some day).
Then, some more flexibility has been added.

The `build_manpages` command for `setup.py` is on it's own way (right here).
The old usage from `build_manpage` is still supported, documented in
[old documentation](examples/old\_format/README.md).

# Usage

Download `./build_manpages` directory and place it somewhere where Python can
find it.  E.g. by:

```bash
git submodule add --name build_manpages https://github.com/praiskup/build_manpages
git submodulde update --init
```

In your `setup.py` add:

```python
[...]
from build_manpages import build_manpages, get_build_py
from setuptools.command.build_py import build_py

setup(
  [...]
  cmdclass={
      'build_manpages': build_manpages,
      # Re-define build-py with new command also calling 'build_manpages'
      'build': get_build_py(build_py),
  }
)
```

In your `setup.cfg` add:

```
[build_manpages]
manpages =
    man/foo.1:object=parser:pyfile=bin/foo.py
    man/bar.1:function=get_parser:pyfile=bin/bar
```

where each line means one manual page to be generated.  The format of the lines
is colon separated set of arguments/options.  The first argument determines the
filename of the generated manual page.  Then follows a list of options of format
`option=value`;  and are about "how to get the particular argparse object".

Supported values are:

- pyfile - what python file the argparse object resides in
- object - the name of arparse object in "pyfile" to import
- function - the name of function in pyfile to call to get the argparse object

Then run `setup.py build_manpages` to build a manpages for your project.  Also,
if you used `get_build_py` helper, `setup.py build` then transitively builds the
manual pages.


# License

This work is released under the terms of the Apache License v2.0.
See LICENSE for details.

[gabrielegiammatteo]: https://github.com/andialbrecht/build\_manpage
[andialbrecht]: https://github.com/andialbrecht/build\_manpage
[frog]: http://crunchyfrog.googlecode.com/svn/
[RunSQLRun]: https://github.com/andialbrecht/runsqlrun
[old blog post]: https://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/
[python pull request]: https://github.com/python/cpython/pull/1169
