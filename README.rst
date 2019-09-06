==================
 argparse-manpage
==================

------------------------------------------
Automatically build manpages from argparse
------------------------------------------

This repository contains a command for ``setuptools`` to build a manpage for
your project.


History
-------

The initial code was developed for CrunchyFrog, a database query tool for
Gnome.  The `frog`_ is now retired and `RunSQLRun`_ is it's successor.  Then,
the ``build_manpage`` command was developed in `andialbrecht`_ and edited
slightly in `gabrielegiammatteo`_.  There's even an [old blog post] about this
command.

Since some useful work has been done in `Python pull request`_, the code from
the PR has been used here too (with a belief that upstream merges this, some
day). Then, some more flexibility has been added.

The ``build_manpages`` command for ``setup.py`` is on it's own way (right here).
The old usage from ``build_manpage`` is still supported, documented in
`old documentation <examples/old_format/README.md>`__.

.. _gabrielegiammatteo: https://github.com/andialbrecht/build\_manpage
.. _andialbrecht: https://github.com/andialbrecht/build\_manpage
.. _frog: http://crunchyfrog.googlecode.com/svn/
.. _RunSQLRun: https://github.com/andialbrecht/runsqlrun
.. _old blog post: https://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/
.. _Python pull request: https://github.com/python/cpython/pull/1169


Installation
------------

Install from PyPI or from the git repo. To install from PyPI, run:

.. code-block:: shell

    $ pip install --user argparse-manpage

To install from source, run:

.. code-block:: shell

    $ git clone https://github.com/praiskup/build_manpages
    $ cd build_manpages
    $ pip install --user .

Usage
-----

*argparse-manpage* can be used as a standalone command-line script or
integrated into your ``setup.py`` file.

setuptools integration
~~~~~~~~~~~~~~~~~~~~~~

In your ``setup.py`` add:

.. code-block:: python

    from setuptools.command.build_py import build_py
    from setuptools.command.install import install

    from build_manpages import build_manpages
    from build_manpages import get_build_py_cmd
    from build_manpages import get_install_cmd

    setup(
        # [...]
        cmdclass={
            'build_manpages': build_manpages,
            # Re-define build_py and install commands so the manual pages
            # are automatically re-generated and installed (optional)
            'build_py': get_build_py_cmd(build_py),
            'install': get_install_cmd(install),
        },
    )

In your ``setup.cfg`` add:

.. code-block:: ini

    [build_manpages]
    manpages =
        man/foo.1:object=parser:pyfile=bin/foo.py
        man/bar.1:function=get_parser:pyfile=bin/bar

where each line means one manual page to be generated.  The format of the lines
is colon separated set of arguments/options.  The first argument determines the
filename of the generated manual page.  Then follows a list of options of
format `option=value`;  and are about "how to get the particular argparse
object".

Supported values are:

``pyfile``
  What Python file the argparse object resides in

``object``
  The name of arparse object in ``pyfile`` to import

``function``
  The name of function in ``pyfile`` to call to get the argparse object

Then run ``setup.py build_manpages`` to build a manpages for your project.  If
you use the ``get_build_py`` helper, ``setup.py build`` will transitively
builds the manual pages.

Command-line usage
~~~~~~~~~~~~~~~~~~

You can also use ``argparse-manpage`` command on a command-line. For example:

.. code-block:: shell

    $ argparse-manpage --pyfile ./pythonfile --function get_parser \
        --author me --author-email me@domain.com --project-name myproject \
        --url https://pagure.io/myproject > cool-manpage.1

This reads ``./pythonfile`` and executes function ``get_parser`` from it. The
function should be programmed to return an ``ArgumentParser`` instance which is
then used together with the other info supplied on the command-line to generate
the man page.

See ``argparse-manpage --help`` for full info.


License
-------

This work is released under the terms of the Apache License v2.0.
See LICENSE for details.
