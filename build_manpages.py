"""
build_manpages command -- generate set of manual pages by the setup()
command.
"""

from distutils.core import Command
from distutils.errors import DistutilsOptionError

from .build_manpage import ManPageWriter, get_parser

class build_manpages(Command):
    description = 'Generate set of man pages from setup().'
    user_options = [
        ('manpages=', 'O', 'list man pages specifications'),
    ]

    manpages_parsed = {}

    def parse_manpages_option(self):
        for spec in self.manpages.strip().split('\n'):
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

            self.manpages_parsed[outputfile] = manpagedata


    def initialize_options(self):
        self.manpages = None


    def finalize_options(self):
        if not self.manpages:
            raise DistutilsOptionError('\'manpages\' option is required')
        self.parse_manpages_option()


    def run(self):
        for page, data in self.manpages_parsed.items():
            print ("generating " + page)
            parser = get_parser(data['import_type'], data['import_from'], data['objname'], data['objtype'])
            type(parser)
            mw = ManPageWriter(parser, self)
            mw.write(page)


def get_build_py(command):
    class build_py(command):
        def run(self):
            self.run_command('build_manpages')
            command.run(self)

    return build_py
