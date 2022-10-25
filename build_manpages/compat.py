"""
Compatibility hacks for the argparse-manpage project.
"""

# Drop once Python 2.7 is dropped
# pylint: disable=unused-import
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser  # type: ignore
