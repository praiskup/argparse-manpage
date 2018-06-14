# -*- coding: utf-8 -*-

# Example setup.py script
#
# The path tweaking at the top is just to make sure, that build_manpage
# can be imported.
#
# 1. Run "setup.py build_manpage"
# 2. Run "man ./example.1" to see the result.
#

import os
import sys

from distutils.core import setup


# Just to make sure that build_manpage can be found.
sys.path.insert(0, os.getcwd())

from build_manpages.build_manpage import build_manpage

setup(
    name='example',
    description='This script does nothing.',
    long_description=(
        'Description and long description are both used by build_manpage.'),
    author='John Doe',
    author_email='jd@example.com',
    version='0.1.0-dev',
    url='http://example.com',
    py_modules=['example'],
    cmdclass={'build_manpage': build_manpage}
)
