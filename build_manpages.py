"""
build_manpages command -- generate set of manual pages by the setup()
command.
"""

from distutils.core import Command
from distutils.errors import DistutilsOptionError

from .build_manpage import ManPageWriter, get_parser_from_file

class build_manpages(Command):
    description = 'Generate set of man pages from setup().'
    user_options = [
        ('manpages=', 'O', 'list man pages specifications'),
    ]

    manpages_parsed = {}

    def parse_manpages_option(self):
        for spec in self.manpages.strip().split('\n'):
            filename, objectname, outputfile = spec.split(':')
            if outputfile in self.manpages_parsed:
                raise DistutilsOptionError('multiple "{0}" manpages requested'.format(outputfile))

            self.manpages_parsed[outputfile] = {
                'file': filename,
                'object': objectname,
            }


    def initialize_options(self):
        self.manpages = None


    def finalize_options(self):
        if not self.manpages:
            raise DistutilsOptionError('\'manpages\' option is required')
        self.parse_manpages_option()


    def run(self):
        for page, data in self.manpages_parsed.items():
            print ("generating " + page)
            parser = get_parser_from_file(data['file'], data['object'])
            mw = ManPageWriter(parser, self)
            mw.write(page)


def get_build_py(command):
    class build_py(command):
        def run(self):
            self.run_command('build_manpages')
            command.run(self)

    return build_py
