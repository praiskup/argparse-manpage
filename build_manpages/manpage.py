from argparse import SUPPRESS, HelpFormatter, _SubParsersAction, _HelpAction
from collections import OrderedDict


DEFAULT_GROUP_NAMES = {
    # We replace ArgumentGroup title (value) with alias (key).
    None: [
        'positional arguments',
    ],
    'OPTIONS': [
        'optional arguments',
        'options',
    ]
}


class Manpage(object):
    def __init__(self, parser):
        self.prog = parser.prog
        self.parser = parser
        if not getattr(parser, '_manpage', None):
            self.parser._manpage = []

        self.formatter = self.parser._get_formatter()
        self.mf = _ManpageFormatter(self.prog, self.formatter)
        self.synopsis = self.parser.format_usage().split(':')[-1].split()
        self.description = self.parser.description

    def format_text(self, text):
        # Wrap by parser formatter and convert to manpage format
        return self.mf.format_text(self.formatter._format_text(text)).strip('\n')


    def __str__(self):
        lines = []

        # Header
        lines.append('.TH {prog} "1" Manual'.format(prog=self.prog))

        # Name
        lines.append('.SH NAME')
        line = self.prog
        if getattr(self.parser, 'man_short_description', None):
            line += " \\- " + self.parser.man_short_description
        lines.append(line)

        # Synopsis
        if self.synopsis:
            lines.append('.SH SYNOPSIS')
            lines.append('.B {}'.format(self.synopsis[0]))
            lines.append(' '.join(self.synopsis[1:]))

        # Description
        if self.description:
            lines.append('.SH DESCRIPTION')

        lines.extend(self.mf.format_parser(self.parser))

        if self.parser.epilog != None:
            lines.append('.SH COMMENTS')
            lines.append(self.format_text(self.parser.epilog))

        # Additional Section
        for section in self.parser._manpage:
            lines.append('.SH {}'.format(section['heading'].upper()))
            lines.append(self.format_text(section['content']))

        return '\n'.join(lines).strip('\n') + '\n'


def underline(text):
    """
    Wrap text with \fI for underlined text
    """
    return r'\fI\,{}\/\fR'.format(text)


def bold(text):
    """ Wrap text by "bold" groff tags """
    if not text.strip().startswith(r'\fB'):
        text = r'\fB{}'.format(text)
    if not text.strip().endswith(r'\fR'):
        text = r'{}\fR'.format(text)
    return text


def quoted(text):
    """ Wrap by single-quotes """
    return "'{0}'".format(text)


class _ManpageFormatter(HelpFormatter):
    def __init__(self, prog, old_formatter):
        super(HelpFormatter, self).__init__()
        self._prog = prog
        self.of = old_formatter

    def _markup(self, text):
        if isinstance(text, str):
            return text.replace('-', r'\-')
        return text

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return bold(metavar)

        parts = []

        # if the Optional doesn't take a value, format is:
        #    -s, --long
        if action.nargs == 0:
            parts.extend(map(bold, action.option_strings))

        # if the Optional takes a value, format is:
        #    -s ARGS, --long ARGS
        else:
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            for option_string in action.option_strings:
                parts.append('{} {}'.format(bold(option_string),
                                            underline(args_string)))
        return ', '.join(parts)


    def _format_parser(self, parser, subcommand=None):
        # The parser "tree" looks like
        # ----------------------------
        # Parser -> [ActionGroup, ActionGroup, ..]
        # Group -> [Action, Action, ..]
        # Action -> Option
        # Action -> Subparsers
        # Subparser -> [Parser, Parser, ..] So called "choices".

        lines = []
        if subcommand:
            first_line = ".SH COMMAND"
            first_line += " " + underline(quoted(subcommand))
            lines.append(first_line)
            lines.append(parser.format_usage())

        if parser.description:
            lines.append(self.format_text(parser.description))

        for group in parser._action_groups:
            lines.extend(self._format_action_group(group, subcommand))

        return lines

    def format_parser(self, parser):
        """
        Return lines Groff formated text for given parser
        """
        return self._format_parser(parser)

    def _format_action(self, action):
        parts = []
        parts.append('.TP')

        action_header = self._format_action_invocation(action)
        parts.append(self._markup(action_header))

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self.of._format_text(self._expand_help(action)).strip('\n')
            parts.append(self.format_text(help_text))

        return parts


    def _format_ag_subcommands(self, actions, prog):
        lines = []

        for action in actions:
            lines.append('.TP')
            lines.append(bold(prog) + ' ' + underline(action.dest))
            if hasattr(action, 'help'):
                lines.append(action.help)

        return '\n'.join(lines)

    def _format_subparsers(self, action_group, action, subcommand=None):
        lines = []
        lines.append('.SH')
        title = action_group.title.upper()
        if subcommand:
            title += " " + underline(quoted(subcommand))
        lines.append(title)

        lines.append(self._format_ag_subcommands(action._choices_actions,
                     subcommand or self._prog))
        for name, choice in action.choices.items():
            new_subcommand = "{} {}".format(subcommand or self._prog, name)
            lines.extend(self._format_parser(choice, new_subcommand))
        return lines


    def _format_action_group(self, action_group, subcommand=None):
        # Parser consists of these action_groups:
        # - positional arguments (no group_actions)
        # - ungrouped options
        # - group 1 options
        # - group 2 options
        # - ...
        # - subparsers

        content = []
        some_action = False
        for action in action_group._group_actions:
            if action.help == SUPPRESS:
                continue

            if isinstance(action, _SubParsersAction):
                return self._format_subparsers(action_group, action,
                                               subcommand)

            if '--help' in action.option_strings:
                # TODO: put out some man page comment ..
                continue

            some_action = True
            content.extend(self._format_action(action))

        # We don't print empty argument groups.
        if not some_action:
            return []

        title = action_group.title
        for replace_with, defaults in DEFAULT_GROUP_NAMES.items():
            if title in defaults:
                title = replace_with
        if title:
            title = title.upper()
        if title and subcommand:
            title += " " + underline(quoted(subcommand))
        title = [] if not title else [".SH " + title]

        description = []
        if action_group.description:
            description.append(self.format_text(action_group.description))

        return title + description + content

    def format_action(self, action):
        return self._format_action(action)

    def format_text(self, text):
        return self._markup(text.strip('\n')\
                   .replace('\\', '\\\\')\
                   .replace('\n', '\n') + '\n')
