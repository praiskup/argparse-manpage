# -*- coding: utf-8 -*-

"""build_manpage command -- Generate man page from setup()"""

import imp
import os
import sys
import datetime
import optparse
import argparse

from distutils.core import Command
from distutils.errors import DistutilsOptionError

from .manpage import Manpage


def get_obj(module, objname, objtype):
    """
    Get OBJNAME from MODULE, and call first if OBJTYPE is function
    """
    obj = getattr(module, objname)
    if objtype != 'object':
        obj = obj()
    return obj


def environ_hack():
    os.environ['BUILD_MANPAGES_RUNNING'] = 'TRUE'


def get_parser_from_module(module, objname, objtype='object'):
    environ_hack()
    import importlib
    mod = importlib.import_module(module)
    return get_obj(mod, objname, objtype)


def get_parser_from_file(filename, objname, objtype='object'):
    """
    Load the given filename as a module and return the requested object from
    there.
    """
    environ_hack()
    # We need to set argv[0] to properly so argparse returns appropriate "usage"
    # strings.  Like "usage: argparse-manpage [-h] ...", instead of
    # "usage: setup.py ...".
    backup_argv = sys.argv
    sys.argv = [os.path.basename(filename)]

    # We used to call 'runpy.run_path()' here, but that did not work correctly
    # with Python 2.7 where the imported object did not see it's own
    # globals/imported modules (including the 'argparse' module).
    module_loaded = imp.load_source("argparse_manpage_loaded_file", filename)

    # Get the ArgumentParser object
    obj = get_obj(module_loaded, objname, objtype)

    # Restore callee's argv
    sys.argv = backup_argv
    return obj


def get_parser(import_type, import_from, objname, objtype):
    if import_type == 'pyfile':
        return get_parser_from_file(import_from, objname, objtype)
    return get_parser_from_module(import_from, objname, objtype)


class ManPageWriter(object):
    _parser = None
    _command = None
    _type = None

    def __init__(self, parser, command):
        self._parser = parser
        self.distribution = command.distribution
        self._today = datetime.date.today()

        if isinstance(parser, argparse.ArgumentParser):
            self._type = 'argparse'
            if parser.formatter_class == argparse.HelpFormatter:
                # Hack for issue #36, to have reproducible manual page content
                # regardless the terminal window size.  Long term we should avoid
                # using the built-in usage formatter, and generate our own.
                parser.formatter_class = \
                        lambda prog: argparse.HelpFormatter(prog, width=78)

        else:
            self._parser.formatter = ManPageFormatter()
            self._parser.formatter.set_parser(self._parser)

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def _write_header(self):
        version = self.distribution.get_version()
        appname = self.distribution.get_name()
        ret = []
        ret.append('.TH %s 1 %s "%s v.%s"\n' % (self._markup(appname),
                                      self._today.strftime('%Y\\-%m\\-%d'), appname, version))
        description = self.distribution.get_description()
        if description:
            name = self._markup('%s - %s' % (appname, description.splitlines()[0]))
        else:
            name = self._markup(appname)
        ret.append('.SH NAME\n%s\n' % name)
        if getattr(self._parser, 'format_usage', None):
            synopsis = self._parser.format_usage()
        else:
            synopsis = self._parser.get_usage()

        if synopsis:
            synopsis = synopsis.replace('%s ' % appname, '')
            ret.append('.SH SYNOPSIS\n.B %s\n%s\n' % (self._markup(appname),
                                                      synopsis))
        long_desc = self.distribution.get_long_description()
        if long_desc:
            ret.append('.SH DESCRIPTION\n%s\n' % self._markup(long_desc))
        return ''.join(ret)

    def _write_options(self, action_name=None, parser=None):
        if not parser:
            parser = self._parser

        if not action_name:
            ret = ['.SH OPTIONS\n']
        else:
            ret = ['.SH OPTIONS ' + action_name.upper() + '\n']

        ret.append(parser.format_option_help())
        if self._type != 'argparse':
            return ''.join(ret)

        subparsers_actions = [
            action for action in parser._actions
                if isinstance(action, argparse._SubParsersAction)]

        for subparser_action in subparsers_actions:
            for name, obj in subparser_action.choices.items():
                if action_name:
                    an = action_name + " " + name
                else:
                    an = name
                ret.append(self._write_options(an, obj))

        return ''.join(ret)

    def _write_seealso(self, text):
        ret = []
        ret.append('.SH "SEE ALSO"\n')

        for i in text:
            name, sect = i.split(":")

            if len(ret) > 1:
                ret.append(',\n')

            ret.append('.BR %s (%s)' % (name, sect))

        return ''.join(ret)

    def _write_footer(self):
        ret = []
        appname = self.distribution.get_name()
        author = '%s <%s>' % (self.distribution.get_author(),
                              self.distribution.get_author_email())
        ret.append(('.SH AUTHORS\n.B %s\nwas written by %s.\n'
                    % (self._markup(appname), self._markup(author))))
        homepage = self.distribution.get_url()
        ret.append(('.SH DISTRIBUTION\nThe latest version of %s may '
                    'be downloaded from\n'
                    '.UR %s\n.UE\n'
                    % (self._markup(appname), self._markup(homepage),)))
        return ''.join(ret)

    def _write_filename(self, filename, what):
        filename = filename if filename != '-' else '/dev/stdout'
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'w') as stream:
            stream.write(what)


    def write(self, filename, seealso=None):
        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        if seealso:
            manpage.append(self._write_seealso(seealso))
        self._write_filename(filename, ''.join(manpage))


    def write_with_manpage(self, filename):
        man = Manpage(self._parser)
        man = str(man) + "\n" +  self._write_footer()
        self._write_filename(filename, man)


class build_manpage(Command):

    description = 'Generate man page from setup().'

    user_options = [
        ('output=', 'O', 'output file'),
        ('parser=', None, 'module path to optparser (e.g. mymod:func'),
        ('parser-file=', None, 'file to the parser module'),
        ('file-and-object=', None, 'import parser object from file, e.g. "bin/blah.py:fooparser"'),
        ('seealso=', None, 'list of manpages to put into the SEE ALSO section (e.g. bash:1)')
        ]

    def initialize_options(self):
        self.output = None
        self.parser = None
        self.seealso = None
        self.parser_file = None
        self.file_and_object = None

    def _get_parser_from_module(self):
        mod_name, func_name = self.parser.split(':')
        if self.parser_file:
            # The 'modname' is entirely ignored in this case.  This is a design
            # issue from 516ca12512979ab8e1a45f24e502a9cd1331f284.  But we keep
            # the 'build_manpage' for compatibility reasons.
            return get_parser_from_file(self.parser_file, func_name,
                                            'function')
        return get_parser_from_module(mod_name, func_name, 'function')

    def finalize_options(self):
        if self.output is None:
            raise DistutilsOptionError('\'output\' option is required')
        if self.parser is None and self.file_and_object is None:
            raise DistutilsOptionError('\'parser\' or \'file-and-object\' option is required')

        self.ensure_string_list('seealso')

        if self.file_and_object:
            filename, objname = self.file_and_object.split(':')
            self._parser = get_parser_from_file(filename, objname)
        else:
            self._parser = self._get_parser_from_module()


    def run(self):
        self.announce('Writing man page %s' % self.output)
        mpw = ManPageWriter(self._parser, self)
        mpw.write(self.output, seealso=self.seealso)


class ManPageFormatter(optparse.HelpFormatter):

    def __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 short_first=1):
        optparse.HelpFormatter.__init__(self, indent_increment,
                                        max_help_position, width, short_first)

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def format_usage(self, usage):
        return self._markup(usage)

    def format_heading(self, heading):
        if self.level == 0:
            return ''
        return '.TP\n%s\n' % self._markup(heading.upper())

    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        result.append('.TP\n.B %s\n' % self._markup(opts))
        if option.help:
            help_text = '%s\n' % self._markup(self.expand_default(option))
            result.append(help_text)
        return ''.join(result)
