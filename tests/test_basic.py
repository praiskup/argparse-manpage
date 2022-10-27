import unittest
import os.path
import sys
import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path

from argparse_testlib import skip_on_python_older_than

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

    def test_aliases(self):
        skip_on_python_older_than("3", "Python 2 doesn't support aliases=")
        parser = argparse.ArgumentParser('aliases_test')
        subparsers = parser.add_subparsers(title="actions")
        parser_list = subparsers.add_parser(
            "list",
            # TEST: add an alias that should not be rendered in the output
            aliases=["ls"],
            help="List all the copr of the "
                 "provided "
        )

        manpage_lines = str(Manpage(parser)).split("\n")
        exp_line = '\\fBaliases_test\\fR \\fI\\,list\\/\\fR'
        not_exp_line = '\\fBaliases_test\\fR \\fI\\,ls\\/\\fR'
        assert exp_line in manpage_lines
        assert not_exp_line not in manpage_lines
        assert 1 == sum([1 if "COMMAND" in line else 0 for line in manpage_lines])


if __name__ == "__main__":
    unittest.main()
