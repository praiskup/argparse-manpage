from build_manpages.manpage import Manpage

import argparse

class TestEscapes(object):

    def test_backslash_escape(self):
        parser = argparse.ArgumentParser('duh')
        parser.add_argument("--jej", help="c:\\something")
        man = Manpage(parser)
        assert 'c:\\\\something' in str(man).split('\n')
