import os
import sys
from setuptools import setup, find_packages

from setuptools.command.build_py import build_py
from setuptools.command.install import install
from build_manpages import __version__
from build_manpages.build_manpages \
    import build_manpages, get_build_py_cmd, get_install_cmd

ld = """
Generate manual page an automatic way from ArgumentParser object, so the manpage
1:1 corresponds to the automatically generated --help output.  The manpage
generator needs to known the location of the object, user can specify that by
(a) the module name or corresponding python filename and (b) the object name or
the function name which returns the object.  There's a limited support for
(deprecated) optparse objects, too.
"""

setup(
    name='argparse-manpage',
    version=__version__,
    url='https://github.com/praiskup/argparse-manpage',
    license='Apache 2.0',
    py_modules = ['build_manpage'],
    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',
    maintainer='Pavel Raiskup',
    maintainer_email='praiskup@redhat.com',
    packages=find_packages(),
    scripts=['bin/argparse-manpage'],
    data_files=[("", ["LICENSE", "NEWS"])],
    description='Build manual page from python\'s ArgumentParser object.',
    long_description=ld,
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
