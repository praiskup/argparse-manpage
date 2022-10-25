"""
Compatibility hacks for the argparse-manpage project.
"""

import sys

# Drop once Python 2.7 is dropped
# pylint: disable=unused-import
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser  # type: ignore

if sys.version_info < (3, 0):
    import imp  # pylint: disable=deprecated-module
    def load_py_file(filename):
        """ Small wrapper having the same call arg list as runpy.run_path() """
        return imp.load_source("argparse_manpage_loaded_file", filename)
else:
    from runpy import run_path as load_py_file

def get_module_object(module_or_dict, objname, objtype):
    """
    Get OBJNAME from a given MODULE (or dict, if loaded using runpy.run_path(),
    but call the object first if OBJTYPE is 'function'.
    """
    obj = None
    if isinstance(module_or_dict, dict):
        obj = module_or_dict[objname]
    else:
        obj = getattr(module_or_dict, objname)
    if objtype != 'object':
        obj = obj()
    return obj


def load_file_as_module(filename):
    """
    Load a given python filename as a dict (runpy on Python 3) or as a module
    (imp module, Python 2).  Note that 'runpy.run_path()' doesn't work correctly
    with Python 2.7 (the imported object doesn't see it's own globals/imported
    modules), and 'imp' module is deprecated for modern Python 3.
    """

    # We used to call 'runpy.run_path()' here, but that did not work correctly
    # with Python 2.7 where the imported object did not see it's own
    # globals/imported modules (including the 'argparse' module).
    return load_py_file(filename)
