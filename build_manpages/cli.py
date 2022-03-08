# Copyright (C) 2017 Red Hat, Inc.

import argparse

from build_manpages.build_manpage import ManPageWriter, get_parser, MANPAGE_DATA_ATTRS


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
ap.add_argument("--version", help="Version of the program.")
ap.add_argument("--description", metavar="TEXT", help="Description of the program.")
ap.add_argument("--long-description", metavar="TEXT", help="Extended description of the program.")
ap.add_argument("--author", action="append", dest="authors", metavar="[AUTHOR]",
                help="Author of the program. Can be specified multiple times.")
ap.add_argument("--url", help="Link to project's homepage")
ap.add_argument("--output", dest='outfile', default='-',
                help="Output file. Defaults to stdout.")


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

    mw = ManPageWriter(parser, args_to_manpage_data(args))
    mw.write_with_manpage(args.outfile)
