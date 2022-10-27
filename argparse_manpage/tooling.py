"""
A tooling helpers for the argparse-manpage project.
"""

import importlib
import os
import sys

from .compat import load_file_as_module, get_module_object


def _environ_hack():
    os.environ['BUILD_MANPAGES_RUNNING'] = 'TRUE'


def get_parser_from_module(module, objname, objtype='object', prog=None):
    """
    Read the given module and return the requested object from there.
    """
    _environ_hack()
    # We need to set argv[0] to properly so argparse returns appropriate "usage"
    # strings.  Like "usage: argparse-manpage [-h] ...", instead of
    # "usage: setup.py ...".
    backup_argv = sys.argv
    if prog:
        sys.argv = [prog]

    mod = importlib.import_module(module)
    obj = get_module_object(mod, objname, objtype)

    # Restore callee's argv
    sys.argv = backup_argv
    return obj


def get_parser_from_file(filename, objname, objtype='object', prog=None):
    """
    Load the given filename as a module and return the requested object from
    there.
    """
    _environ_hack()
    # We need to set argv[0] to properly so argparse returns appropriate "usage"
    # strings.  Like "usage: argparse-manpage [-h] ...", instead of
    # "usage: setup.py ...".
    backup_argv = sys.argv
    if prog:
        sys.argv = [prog]
    else:
        sys.argv = [os.path.basename(filename)]

    # Get the ArgumentParser object
    module_loaded = load_file_as_module(filename)
    obj = get_module_object(module_loaded, objname, objtype)

    # Restore callee's argv
    sys.argv = backup_argv
    return obj


def get_parser(import_type, import_from, objname, objtype, prog=None):
    """
    Load a function or object from a given file or module.
    """
    if import_type == 'pyfile':
        return get_parser_from_file(import_from, objname, objtype, prog=prog)
    return get_parser_from_module(import_from, objname, objtype, prog=prog)


def write_to_filename(text, filename):
    """
    Write given text into a filename at once.  Pre-create the parent directory
    if it doesn't exist yet.  Print to stdout if filename == '-'.
    """
    filename = filename if filename != '-' else '/dev/stdout'
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'w') as stream:
        stream.write(text)
