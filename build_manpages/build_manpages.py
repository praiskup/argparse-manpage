"""
build_manpages command -- generate set of manual pages by the setup()
command.
"""

import os
import shutil

from argparse_manpage.compat import ConfigParser
from argparse_manpage.tooling import get_parser, write_to_filename
from argparse_manpage.manpage import (
    Manpage,
    MANPAGE_DATA_ATTRS,
    get_manpage_data_from_distribution,
)

from build_manpages.compat import Command, DistutilsOptionError

# TODO: drop the "old" format support, and stop depending on ManPageWriter
# TODO: No more deps from this module, please.
from .build_manpage import ManPageWriter

DEFAULT_CMD_NAME = 'build_manpages'

def parse_manpages_spec(string):
    manpages_data = {}
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
                if oname == 'pyfile':
                    manpagedata['prog'] = os.path.basename(ovalue)

            elif oname == 'format':
                assert(not 'format' in manpagedata)
                manpagedata[oname] = ovalue

            elif oname == 'author':
                manpagedata.setdefault("authors", []).append(ovalue)

            elif oname in MANPAGE_DATA_ATTRS and oname != "authors":
                assert(not oname in manpagedata)
                manpagedata[oname] = ovalue

            else:
                raise ValueError("Unknown manpage configuration option: {}".format(oname))

        manpages_data[outputfile] = manpagedata

    return manpages_data


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

        self.manpages_data = parse_manpages_spec(self.manpages)

        # if a value wasn't set in setup.cfg, use the value from setup.py
        for page, data in self.manpages_data.items():
            get_manpage_data_from_distribution(self.distribution, data)

    def run(self):
        for page, data in self.manpages_data.items():
            print ("generating " + page)
            parser = get_parser(data['import_type'], data['import_from'], data['objname'], data['objtype'], data.get('prog', None))
            format = data.get('format', 'pretty')
            if format in ('pretty', 'single-commands-section'):
                manpage = Manpage(parser, data, format)
                write_to_filename(str(manpage), page)
            elif format == 'old':
                # TODO: drop this entirely
                mw = ManPageWriter(parser, data)
                mw.write(page)
            else:
                raise ValueError("Unknown format: {}".format(format))


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
