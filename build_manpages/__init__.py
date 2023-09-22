"""
Export some useful methods in top-level.
"""

from argparse_manpage import __version__
from .build_manpages import build_manpages, get_build_py_cmd, get_install_cmd

install = get_install_cmd()
build_py = get_build_py_cmd()
