#!/usr/bin/python3


import argparse


class HelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            for i in action._get_subactions():
                if i.help == argparse.SUPPRESS:
                    # don't display commands with suppressed help
                    continue
                if len(i.metavar) > 20:
                    parts.append("%*s%-21s" % (self._current_indent, "", i.metavar))
                    parts.append("%*s %s" % (self._current_indent + 21, "", i.help))
                else:
                    parts.append("%*s%-21s %s" % (self._current_indent, "", i.metavar, i.help))
            return "\n".join(parts)
        return super(HelpFormatter, self)._format_action(action)

    def _format_usage(self, usage, actions, groups, prefix):
        if usage:
            usage = usage.strip()
            usage = usage % dict(prog=self._prog)
        else:
            usage = super(HelpFormatter, self)._format_usage(usage, actions, groups, prefix)
            if usage.startswith("usage: "):
                usage = usage[7:]

        result = ["usage: "]
        for line in usage.strip().splitlines():
            result.append("  " + line)
        result.append("")
        result.append("")
        return "\n".join(result)


def get_parser():
    parser = argparse.ArgumentParser(
        prog="osc",
        usage=
            "%(prog)s [global opts] <command> [--help] [opts] [args]\n"
            "%(prog)s --help",
        formatter_class=HelpFormatter,
    )

    commands = parser.add_subparsers(
        title="commands",
        dest="command",
    )

    # IMPORTANT:
    # it is necessary to specify 'prog=' in all subcommands to get usage rendered correctly

    cmd_build = commands.add_parser(
        "build",
        help="Build a package on your local machine",
        description="Build command description.",
        prog="osc [global opts] build",
        usage=
            "%(prog)s (will try to guess a build environment)\n"
            "%(prog)s REPOSITORY ARCH BUILD_DESCR\n"
            "%(prog)s REPOSITORY ARCH\n"
            "%(prog)s REPOSITORY (ARCH = hostarch, BUILD_DESCR is detected automatically)\n"
            "%(prog)s ARCH (REPOSITORY = build_repository (config option), BUILD_DESCR is detected automatically)\n"
            "%(prog)s BUILD_DESCR (REPOSITORY = build_repository (config option), ARCH = hostarch)\n"
            "%(prog)s (REPOSITORY = build_repository (config option), ARCH = hostarch, BUILD_DESCR is detected automatically)",
        formatter_class=HelpFormatter,
    )
    cmd_build.add_argument(
        "--clean",
        action="store_true",
        help="Delete old build root before initializing it",
    )

    cmd_list = commands.add_parser(
        "list",
        help="List sources or binaries on the server",
        description="List command description.",
        prog="osc [global opts] list",
        usage=
            "%(prog)s [PROJECT [PACKAGE]]\n"
            "%(prog)s -b [PROJECT [PACKAGE [REPO [ARCH]]]]",
        formatter_class=HelpFormatter,
    )
    cmd_list.add_argument(
        "-M", "--meta",
        action="store_true",
        help="list meta data files",
    )
    cmd_list.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="print extra information",
    )

    cmd_foo = commands.add_parser(
        "foo",
        help="Test command with subcommands",
        description="Some description.",
        prog="osc [global opts] foo",
        formatter_class=HelpFormatter,
    )

    cmd_foo_subcommands = cmd_foo.add_subparsers(
        title="commands",
        dest="commands",
    )

    cmd_foo_bar = cmd_foo_subcommands.add_parser(
        "bar",
        help="help bar",
        prog="osc [global opts] foo bar",
    )
    cmd_foo_bar.add_argument("--opt-bar1", help="help opt-bar1")
    cmd_foo_bar.add_argument("--opt-bar2", help="help opt-bar2")

    cmd_foo_baz = cmd_foo_subcommands.add_parser(
        "baz",
        help="help baz",
        prog="osc [global opts] foo baz",
    )
    cmd_foo_baz.add_argument("--opt-baz1", help="help opt-baz1")
    cmd_foo_baz.add_argument("--opt-baz2", help="help opt-baz2")

    cmd_hidden = commands.add_parser(
        "hidden",
        help=argparse.SUPPRESS,
        description="A hidden command, not displayed in help",
        formatter_class=HelpFormatter,
    )

    return parser


def main():
    parser = get_parser()
    parser.parse_args()


if __name__ == "__main__":
    main()
