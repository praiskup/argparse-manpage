# Copyright (C) 2017 Red Hat, Inc.

# Python 2.7 hack.  Without this, 'from build_manpages.build_manpage' attempts
# to import 'build_manpages.build_manpages.build_manpage' because of our
# unfortunate file naming.
from __future__ import absolute_import

import argparse

from argparse_manpage.tooling import get_parser, write_to_filename
from argparse_manpage.manpage import MANPAGE_DATA_ATTRS, Manpage


description = """
Build manual page from Python's argparse.ArgumentParser object.
""".strip()

ap = argparse.ArgumentParser(
    prog='argparse-manpage',
    description=description,
)

src_group = ap.add_mutually_exclusive_group(required=True)
src_group.add_argument(
    "--module",
    help="search the OBJECT/FUNCTION in MODULE"
)

src_group.add_argument(
    "--pyfile",
    help="search the OBJECT/FUNCTION in FILE"
)

obj_group = ap.add_mutually_exclusive_group(required=True)
obj_group.add_argument(
    "--function",
    help="call FUNCTION from MODULE/FILE to obtain ArgumentParser object",
)
obj_group.add_argument(
    "--object",
    help="obtain ArgumentParser OBJECT from FUNCTION (to get argparse object) from MODULE or FILE",
)


ap.add_argument("--project-name", help="Name of the project the documented program is part of.")
ap.add_argument("--prog", help="Substitutes %%prog in ArgumentParser's usage.")
ap.add_argument("--version", help=(
    "Version of the program, will be visible in the "
    "manual page footer."))
ap.add_argument("--description", metavar="TEXT", help=(
    "description of the program, used in the NAME section, after the "
    "leading 'name - ' part, see man (7) man-pages for more info"))
ap.add_argument("--long-description", metavar="TEXT", help=argparse.SUPPRESS)
ap.add_argument("--author", action="append", dest="authors", metavar="[AUTHOR]",
                help="Author of the program. Can be specified multiple times.")
ap.add_argument("--author-email", action="append", dest="authors",
                help=argparse.SUPPRESS)
ap.add_argument("--url", help="Link to project's homepage")
ap.add_argument("--format", default="pretty", choices=("pretty", "single-commands-section"),
                help="Format of the generated man page. Defaults to 'pretty'.")
ap.add_argument("--output", dest='outfile', default='-',
                help="Output file. Defaults to stdout.")
ap.add_argument("--manual-section", help=(
    "Section of the manual, by default 1.  See man (7) man-pages for more "
    "info about existing sections."))
ap.add_argument("--manual-title", help=(
    "The title of the manual, by default \"Generated Python Manual\". "
    "See man (7) man-pages for more instructions."))


def args_to_manpage_data(args):
    data = {}
    for attr in MANPAGE_DATA_ATTRS:
        value = getattr(args, attr)
        data[attr] = value
    return data


def main():
    args = ap.parse_args()

    import_type = 'pyfile'
    import_from = args.pyfile
    if args.module:
        import_type = 'module'
        import_from = args.module

    obj_type = 'object'
    obj_name = args.object
    if args.function:
        obj_type = 'function'
        obj_name = args.function

    parser = get_parser(import_type, import_from, obj_name, obj_type, prog=args.prog)
    data = args_to_manpage_data(args)
    manpage = Manpage(parser, format=args.format, _data=data)
    write_to_filename(str(manpage), args.outfile)
