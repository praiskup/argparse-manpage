# -*- coding: utf-8 -*-

# Example of argparse taken from:
# https://pagure.io/copr/copr/blob/a4feb01bc35b8554f503d41795e7a184ff929dd4/f/cli/copr_cli

import os
import sys

from setuptools import setup, find_packages

# Just to make sure that build_manpage can be found.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from build_manpages.build_manpages \
        import build_manpages, get_build_py_cmd, get_install_cmd

from setuptools.command.install import install
from distutils.command.build import build

setup(
    name='example',
    description='This project does nothing.',
    long_description=('Long description of the project.'),
    author='John Doe',
    author_email='jd@example.com',
    version='0.1.0',
    url='http://example.com',
    packages=find_packages(),
    scripts=['bin/test'],
    cmdclass={
        'build_manpages': build_manpages,
        'build': get_build_py_cmd(build),
        'install': get_install_cmd(install),
    },
)
