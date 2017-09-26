"""
build_manpages command -- generate set of manual pages by the setup()
command.
"""

import os

DEFAULT_CMD_NAME = 'build_manpages'

from distutils.core import Command
from distutils.errors import DistutilsOptionError
import shutil

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

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


def get_build_py_cmd(command):
    class build_py(command):
        def run(self):
            self.run_command(DEFAULT_CMD_NAME)
            command.run(self)

    return build_py


def get_install_cmd(command):
    class install(command):
        def install_manual_pages(self):
            config = ConfigParser()
            config.read('setup.cfg')
            spec = config.get(DEFAULT_CMD_NAME, 'manpages')
            data = parse_manpages_spec(spec)

            mandir = os.path.join(self.install_data, 'share/man/man1')
            if not os.path.exists(mandir):
                os.makedirs(mandir)
            for key, _ in data.items():
                print ('installing {0}'.format(key))
                shutil.copy(key, mandir)

        def run(self):
            command.run(self)
            self.install_manual_pages()

    return install
