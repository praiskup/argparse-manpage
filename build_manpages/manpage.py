from argparse import SUPPRESS, HelpFormatter, _SubParsersAction, _HelpAction
from collections import OrderedDict



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


    def _has_options(self):
        for action in self.parser._actions:
            if isinstance(action, _HelpAction):
                continue
            return True
        return False


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
            lines.append(self.format_text(self.description))

        # Options
        if self._has_options():
            lines.append('.SH OPTIONS')
        for action_group in self.parser._action_groups:
            lines.append(self.mf.format_action_group(action_group, self.parser.prog))

        if self.parser.epilog != None:
            lines.append('.SH COMMENTS')
            lines.append(self.format_text(self.parser.epilog))

        # Additional Section
        for section in self.parser._manpage:
            lines.append('.SH {}'.format(section['heading'].upper()))
            lines.append(self.format_text(section['content']))

        return '\n'.join(lines).strip('\n') + '\n'


class _ManpageFormatter(HelpFormatter):
    def __init__(self, prog, old_formatter):
        super(HelpFormatter, self).__init__()
        self._prog = prog
        self.of = old_formatter

    def _markup(self, text):
        if isinstance(text, str):
            return text.replace('-', r'\-')
        return text

    def _underline(self, text):
        return r'\fI\,{}\/\fR'.format(text)

    def _bold(self, text):
        if not text.strip().startswith(r'\fB'):
            text = r'\fB{}'.format(text)
        if not text.strip().endswith(r'\fR'):
            text = r'{}\fR'.format(text)
        return text

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            metavar = self._bold(metavar)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(map(self._bold, action.option_strings))

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._underline(action.dest.upper())
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('{} {}'.format(self._bold(option_string),
                                                args_string))
            return ', '.join(parts)


    def _format_parser(self, parser, name):
        lines = []
        lines.append(".SH OPTIONS '{0}'".format(name))
        lines.append(parser.format_usage())

        if parser.description:
            lines.append(self.format_text(parser.description))

        groups = parser._action_groups
        if len(groups):
            for group in groups:
                lines.append(self._format_action_group(group, name))

        return lines


    def _format_action(self, action):
        if '--help' in action.option_strings:
            return ""

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
        lines = [
            '.SS',
            self._bold('Sub-commands'),
        ]

        for action in actions:
            lines.append('.TP')
            lines.append(self._bold(prog) + ' ' + self._underline(action.dest))
            if hasattr(action, 'help'):
                lines.append(action.help)

        return '\n'.join(lines)


    def _format_action_group(self, action_group, prog):
        lines = []

        actions = action_group._group_actions
        for action in actions:
            if action.help == SUPPRESS:
                continue

            if isinstance(action, _SubParsersAction):
                lines.append(self._format_ag_subcommands(
                        action._choices_actions, prog))

                for name, choice in action.choices.items():
                    lines.extend(self._format_parser(choice, prog + ' ' + name))
                continue

            lines.extend(self._format_action(action))

        return '\n'.join(lines)

    def format_action(self, action):
        return self._format_action(action)

    def format_action_group(self, action_group, prog):
        return self._format_action_group(action_group, prog)

    def format_text(self, text):
        return self._markup(text.strip('\n')\
                   .replace('\\', '\\\\')\
                   .replace('\n', '\n') + '\n')
