import unittest
import os.path
import sys
import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from build_manpages.manpage import Manpage


class TestEscapes(unittest.TestCase):

    def test_backslash_escape(self):
        parser = argparse.ArgumentParser('duh')
        parser.add_argument("--jej", help="c:\\something")
        man = Manpage(parser)
        assert 'c:\\\\something' in str(man).split('\n')

if __name__ == "__main__":
    unittest.main()
