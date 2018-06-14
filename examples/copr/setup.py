# -*- coding: utf-8 -*-

# Example of argparse taken from:
# https://pagure.io/copr/copr/blob/a4feb01bc35b8554f503d41795e7a184ff929dd4/f/cli/copr_cli

import os
import sys

from setuptools import setup, find_packages

# Just to make sure that build_manpage can be found.
sys.path = [os.path.join(os.getcwd(), 'fake-deps')] + sys.path

from build_manpages.build_manpages \
        import build_manpages, get_build_py_cmd, get_install_cmd

from setuptools.command.build_py import build_py
from setuptools.command.install import install

setup(
    name='example',
    description='This project does nothing.',
    long_description=('Long description of the project.'),
    author='John Doe',
    author_email='jd@example.com',
    version='0.1.0',
    url='http://example.com',
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
    packages=find_packages(),
)
