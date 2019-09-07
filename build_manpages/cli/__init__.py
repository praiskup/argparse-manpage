# Copyright (C) 2017 Red Hat, Inc.

import argparse

from build_manpages.build_manpage import ManPageWriter, get_parser
from build_manpages.cli import hack

description = """
Build manual page from Python's argparse.ArgumentParser object.
""".strip()

fake_cmd = hack.FakeCommand()

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


ap.add_argument("--author", action=fake_cmd.getAction())
ap.add_argument("--author-email", action=fake_cmd.getAction())
ap.add_argument("--project-name", dest='name', action=fake_cmd.getAction())
ap.add_argument("--url", action=fake_cmd.getAction())
ap.add_argument("--output", dest='outfile', default='-',
                help="output file; default to stdout")


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

    parser = get_parser(import_type, import_from, obj_name, obj_type)
    mw = ManPageWriter(parser, fake_cmd)
    mw.write_with_manpage(args.outfile)
