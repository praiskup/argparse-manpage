# -*- coding: utf-8 -*-

"""build_manpage command -- Generate man page from setup()"""

import datetime
import os
import sys
import optparse
from distutils.errors import DistutilsOptionError

from setuptools import Command


def get_parser_from_file(filename, objname):
    from runpy import run_path
    filedict = run_path(filename)
    return filedict[objname]


class ManPageWriter(object):
    _parser = None
    _command = None

    def __init__(self, parser, command):
        self._parser = parser
        self.description = command.description
        self.distribution = command.distribution
        self._today = datetime.date.today()

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
            name = self._markup('%s - %s' % (self._markup(appname),
                                             description.splitlines()[0]))
        else:
            name = self._markup(appname)
        ret.append('.SH NAME\n%s\n' % name)
        synopsis = self._parser.format_usage()
        if synopsis:
            synopsis = synopsis.replace('%s ' % appname, '')
            ret.append('.SH SYNOPSIS\n.B %s\n%s\n' % (self._markup(appname),
                                                      synopsis))
        long_desc = self.distribution.get_long_description()
        if long_desc:
            ret.append('.SH DESCRIPTION\n%s\n' % self._markup(long_desc))
        return ''.join(ret)

    def _write_options(self):
        ret = ['.SH OPTIONS\n']
        ret.append(self._parser.format_help())
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

    def write(self, filename, seealso=None):
        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        if seealso:
            manpage.append(self._write_seealso(seealso))
        stream = open(filename, 'w')
        stream.write(''.join(manpage))
        stream.close()


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

    def get_parser_from_module(self):
        mod_name, func_name = self.parser.split(':')
        fromlist = mod_name.split('.')

        try:
            if self.parser_file:
                #
                # Alternative method to load the module. We use the path to the module file (if the user provide it).
                # This beacuse, if the module uses namespaces, the original method does not work
                #
                # inspired from https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
                #
                # praiskup: this is not working for python2, and is pretty
                # hacky.  Kept for compat option parser-file..
                import importlib.util
                spec = importlib.util.spec_from_file_location(mod_name, self.parser_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            else:
                mod = __import__(mod_name, fromlist=fromlist)

            return getattr(mod, func_name)()

        except ImportError as err:
            raise

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
            self._parser = self.get_parser_from_module()


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
