# -*- coding: utf-8 -*-

# Example of argparse taken from:
# https://pagure.io/copr/copr/blob/a4feb01bc35b8554f503d41795e7a184ff929dd4/f/cli/copr_cli

import os
import sys

from setuptools import setup

# Just to make sure that build_manpage can be found.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.getcwd())

from build_manpages.build_manpages import build_manpages

setup(
    name='example',
    description='This project does nothing.',
    long_description=('Long description of the project.'),
    author='John Doe',
    author_email='jd@example.com',
    version='0.1.0',
    url='http://example.com',
    py_modules=['example'],
    cmdclass={'build_manpages': build_manpages}
)
