"""
Compat hacks for argparse-manpage's build_manpages module
"""

# pylint: disable=unused-import,deprecated-module,raise-missing-from

try:
    from setuptools import Command
    from setuptools.command.build_py import build_py
    from setuptools.command.install import install
except ImportError:
    try:
        from distutils.core import Command
        from distutils.command.build_py import build_py
        from distutils.command.install import install
    except ImportError as orig_err:
        raise ImportError(
            "To use the 'build_manpages' tool on Python 3.12+, "
            "you need to install 'setuptools'."
        )

# A separate try-except block from the one above.  This is more likely to fail
# than the above setuptools part and we would start using distutils just
# beacause of the exception.
try:
    from setuptools.errors import OptionError as DistutilsOptionError
except ImportError:
    from distutils.errors import DistutilsOptionError
