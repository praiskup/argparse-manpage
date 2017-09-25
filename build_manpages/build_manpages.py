"""
build_manpages command -- generate set of manual pages by the setup()
command.
"""

DEFAULT_CMD_NAME = 'build_manpages'

from distutils.core import Command
from distutils.errors import DistutilsOptionError
import configparser
from .build_manpage import ManPageWriter, get_parser


def parse_manpages_spec(string):
    manpages_parsed = {}
    for spec in string.strip().split('\n'):
        manpagedata = {}
        output = True
        for option in spec.split(':'):
            if output:
                outputfile = option
                output = False
                continue

            oname, ovalue = option.split('=')

            if oname == 'function' or oname == 'object':
                assert(not 'objtype' in manpagedata)
                manpagedata['objtype'] = oname
                manpagedata['objname'] = ovalue

            elif oname == 'pyfile' or oname == 'module':
                assert(not 'import_type' in manpagedata)
                manpagedata['import_type'] = oname
                manpagedata['import_from'] = ovalue

            elif oname == 'format':
                assert(not 'format' in manpagedata)
                manpagedata[oname] = ovalue

        manpages_parsed[outputfile] = manpagedata

    return manpages_parsed


class build_manpages(Command):
    description = 'Generate set of man pages from setup().'
    user_options = [
        ('manpages=', 'O', 'list man pages specifications'),
    ]

    def initialize_options(self):
        self.manpages = None


    def finalize_options(self):
        if not self.manpages:
            raise DistutilsOptionError('\'manpages\' option is required')

        self.manpages_parsed = parse_manpages_spec(self.manpages)


    def run(self):
        for page, data in self.manpages_parsed.items():
            print ("generating " + page)
            parser = get_parser(data['import_type'], data['import_from'], data['objname'], data['objtype'])
            mw = ManPageWriter(parser, self)
            if not 'format' in data or data['format'] == 'pretty':
                mw.write_with_manpage(page)
            elif data['format'] == 'old':
                mw.write(page)


def get_build_py(command):
    class build_py(command):
        def run(self):
            self.run_command(DEFAULT_CMD_NAME)
            command.run(self)

    return build_py
