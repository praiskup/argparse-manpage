import os
import sys
from setuptools import setup, find_packages

# Simplify bootstrapping.  We don't need to have an older argparse-manpage
# installed to successfully build argparse-manpage.
# pylint: disable=wrong-import-position
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from build_manpages import __version__
from build_manpages import (
    build_manpages,
    get_build_py_cmd,
    get_install_cmd,
)



def get_readme():
    with open(os.path.join(ROOT_DIR, 'README.md')) as fh:
        return ''.join(fh.readlines())

setup(
    name='argparse-manpage',
    version=__version__,
    url='https://github.com/praiskup/argparse-manpage',
    license='Apache 2.0',
    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',
    maintainer='Pavel Raiskup',
    maintainer_email='praiskup@redhat.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'argparse-manpage=argparse_manpage.cli:main',
        ],
    },
    description='Build manual page from python\'s ArgumentParser object.',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(),
        'install': get_install_cmd(),
    },
    extras_require={
        'setuptools': ["setuptools"]
    },
)
