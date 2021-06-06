import unittest
import os.path
import sys
import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from build_manpages.manpage import Manpage


class Tests(unittest.TestCase):

    def test_backslash_escape(self):
        parser = argparse.ArgumentParser('duh')
        parser.add_argument("--jej", help="c:\\something")
        man = Manpage(parser)
        assert 'c:\\\\something' in str(man).split('\n')
        assert '.SH OPTIONS' in str(man).split('\n')

    def test_argument_groups(self):
        parser1 = argparse.ArgumentParser('duh')
        parser = parser1.add_argument_group('g1')
        parser.add_argument("--jej", help="c:\\something")
        parser2 = parser1.add_argument_group('g2')
        parser2.add_argument("--jej2", help="c:\\something")
        parser2.add_argument("--else", help="c:\\something")
        man = Manpage(parser1)
        self.assertIn('.SH G1', str(man).split('\n'))
        self.assertIn('.SH G2', str(man).split('\n'))
        self.assertNotIn('.SH OPTIONS', str(man).split('\n'))

if __name__ == "__main__":
    unittest.main()
