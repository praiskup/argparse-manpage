import os
import sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install

# insert path to build_manpage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from build_manpages.build_manpages \
        import build_manpages, get_build_py_cmd, get_install_cmd


setup(
    name='osc',
    version='1.0',
    description='openSUSE commander',
    author='openSUSE project',
    author_email='opensuse-buildservice@opensuse.org',
    url='http://en.opensuse.org/openSUSE:OSC',
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
    packages=find_packages(),
)
