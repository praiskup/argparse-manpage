"""
A tooling helpers for the argparse-manpage project.
"""

import imp
import os
import sys

def _get_obj(module, objname, objtype):
    """
    Get OBJNAME from MODULE, and call first if OBJTYPE is function
    """
    obj = getattr(module, objname)
    if objtype != 'object':
        obj = obj()
    return obj


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

    import importlib
    mod = importlib.import_module(module)
    obj = _get_obj(mod, objname, objtype)

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

    # We used to call 'runpy.run_path()' here, but that did not work correctly
    # with Python 2.7 where the imported object did not see it's own
    # globals/imported modules (including the 'argparse' module).
    module_loaded = imp.load_source("argparse_manpage_loaded_file", filename)

    # Get the ArgumentParser object
    obj = _get_obj(module_loaded, objname, objtype)

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
