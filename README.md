# ArgumentParser instance → manual page

Avoid documenting your Python script arguments on two places!  This is typically
done in an [argparse.ArgumentParser][ap-docs] help configuration (`help=`,
`description=`, etc.), and also in a manually crafted manual page.

The good thing about an `ArgumentParser` objects is that it actually provides
a traversable "tree-like" structure, with all the necessary info needed to
**automatically generate** documentation, for example in a *groff* typesetting
system (manual pages).  And this is where this project can help.

There are two supported ways to generate the manual, either script it using the
installed command `argparse-manpage`, or via `setup.py build` automation (with a
slight bonus of automatic manual page installation with `setup.py install`).


## What is need?

Most of the (meta)data is stored in the `ArgumentParser` object, therefore
`argparse-manpage` needs to know its location—it can be either the object
itself, or a method to call to get the object [^1].

On top of this, several manual page fields (like *author* or *project* name)
need to be specified, either on command-line or via `setup.py` metadata.


## Command-line usage

See the following example:

```
$ argparse-manpage --pyfile ./pythonfile.py --function get_parser \
                   --author "John --author-email doe@example.com" \
                   --project-name myproject --url https://pagure.io/myproject \
> cool-manpage.1
```

This (a) processes the `./pythonfile.py`, (b) calls the `get_parser` inside to
obtain the `ArgumentParser` instance, (c) transforms it into a manual page and
(d) stores it into the `cool-manpage.1` file.

Alternatively those options above can be combined with

- option `--module mymodule.main`, to load a Python module `mymodule.main`
  from `PYTHONPATH`, or
- `--object parser_object_name` if the `parser_object_name` is a global
  variable.


## Use with setup.py

First, you need to declare that `setup.py` uses an external package in your
`pyproject.toml` file:

```toml
[build-system]
requires = ["argparse-manpage[setuptools]"]
```

Alternatively you can place the `build_manpages` (sub)directory from this
project somewhere onto `PYTHONPATH` so you can use it in `setup.py`.  For
example:

```bash
git submodule add --name build_manpages https://github.com/praiskup/build_manpages
git submodule update --init
```

In your `setup.py` use pattern like:

```python
[...]
from build_manpages import build_manpages, get_build_py_cmd, get_install_cmd

setup(
  [...]
  cmdclass={
      'build_manpages': build_manpages,
      # Re-define build_py and install commands so the manual pages
      # are automatically re-generated and installed
      'build_py': get_build_py_cmd(),
      'install': get_install_cmd(),
  }
)
```

And in `setup.cfg` configure the manual pages you want to automatically
generate and install:

```
[build_manpages]
manpages =
    man/foo.1:object=parser:pyfile=bin/foo.py
    man/bar.1:function=get_parser:pyfile=bin/bar
    man/baz.1:function=get_parser:pyfile=bin/bar:prog=baz
```

Or in `pyproject.toml` (requires setuptools >= 62.2.0):

```toml
[build_manpages]
manpages = [
    "man/foo.1:object=parser:pyfile=bin/foo.py",
    "man/bar.1:function=get_parser:pyfile=bin/bar",
    "man/baz.1:function=get_parser:pyfile=bin/bar:prog=baz",
]
```

The format of those lines is a colon separated list of arguments/options.  The
first argument determines the filename of the generated manual page.  Then
follows a list of options of format `option=value`.  Supported values are:

- pyfile - what python file the argparse object resides in
- object - the name of arparse object in "pyfile" to import
- function - the name of function in pyfile to call to get the argparse object
- format - format of the generated man page: `pretty` (default), `single-commands-section`
- author - author of the program; can be specified multiple times
- description - description of the program, used in the NAME section, after the
    leading 'name - ' part, see man (7) man-pages for more info
- project_name - name of the project the program is part of
- version - version of the project, visible in manual page footer
- prog - value that substitutes %prog in ArgumentParser's usage
- url - link to project download page
- manual_section - section of the manual, by default 1, see man (7) man-pages
    for more info about existing sections
- manual_title - the title of the manual, by default "Generated Python Manual",
    see man (7) man-pages for more instructions
- include - a file of extra material to include; see below for the format
- manfile - a file containing a complete man page that just needs to be installed
    (such files must also be listed in `MANIFEST.in`)

The values from setup.cfg override values from setup.py's setup(). Note that
when `manfile` is set for a particular page, no other option is allowed.

Then run `setup.py build_manpages` to build a manpages for your project.  Also,
if you used `get_build_py` helper, `setup.py build` then transitively builds the
manual pages.

## Include file format

The include file format is based on GNU `help2man`'s `--include` format.

The format is simple:

```
[section]
text

/pattern/
text
```

Blocks of verbatim *roff text are inserted into the output either at
the start of the given `section` (case insensitive), or after a
paragraph matching `pattern`, a Python regular expression.

Lines before the first section are silently ignored and may be used for
comments and the like.

Other sections are prepended to the automatically produced output for the
standard sections given above, or included near the bottom of the man page,
before the `AUTHOR` section, in the order they occur in the include file.

Placement of the text within the section may be explicitly requested by
using the syntax `[<section]`, `[=section]` or `[>section]` to place the
additional text before, in place of, or after the default output
respectively.

## Installation

This package is distributed [in PyPI][pypi-page], can be installed by:

    $ pip install argparse-manpage

It can simply downloaded, or distributed as a git submodule (see above).


## Packaging status

The Git snapshot RPMs–pre-release version automatically built from the `main`
branch–are available in Fedora Copr build system

[![build status](https://copr.fedorainfracloud.org/coprs/praiskup/argparse-manpage-ci/package/argparse-manpage/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/praiskup/argparse-manpage-ci/)

The `argparse-manpage` project is provided natively on many distributions:

![build status](https://repology.org/badge/vertical-allrepos/argparse-manpage.svg?exclude_unsupported=1&header=argparse-manpage)

Try your package manager directly (e.g. on Fedora `dnf install -y
argparse-manpage`).


## History

The initial code was developed for CrunchyFrog, a database query tool for Gnome.
The [frog] is now retired and [RunSQLRun] is it's successor.  Then, the
`build_manpage` command was developed in [andialbrecht] and edited slightly
in [gabrielegiammatteo].  There's even an [old blog post] about this command.

Since some useful work has been done in [python pull request], the code from the
PR has been used here too.

Later more options and flexibility has been implemented in this fork, with the
help of many contributors.  Thank you!

Historically, `build_manpage` setup.py command was provided (mostly for
`OptionParser`).  Later we migrated to more versatile `build_manpages` command.
But the old variant is still [supported](examples/old\_format/README.md).

## License

This work is released under the terms of the Apache License v2.0.
See LICENSE for details.


[^1]: `argparse-manpage` needs to process the location (file/module) via Python
      interpreter, and thus please avoid side-effects (typically, the `main.py`
      files need to use the `if __name__ == "__main__"` condition, and similar).

[gabrielegiammatteo]: https://github.com/andialbrecht/build\_manpage
[andialbrecht]: https://github.com/andialbrecht/build\_manpage
[frog]: http://crunchyfrog.googlecode.com/svn/
[RunSQLRun]: https://github.com/andialbrecht/runsqlrun
[old blog post]: https://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/
[python pull request]: https://github.com/python/cpython/pull/1169
[ap-docs]: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser
[pypi-page]: https://pypi.org/project/argparse-manpage/
