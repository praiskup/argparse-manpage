from argparse import SUPPRESS, HelpFormatter

class Manpage(object):
    def __init__(self, parser):
        self.prog = parser.prog
        self.parser = parser
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
        lines.append(self.prog)

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
        lines.append('.SH OPTIONS')
        for action_group in self.parser._action_groups:
            ag_lines = []
            for action in action_group._group_actions:
                if action.help == SUPPRESS:
                    continue
                ag_lines.append('.TP')
                fa = self.mf.format_action(action)
                if len(fa) == 1:
                    ag_lines.extend(fa)
                else:
                    # This is a subcommand
                    for command in fa:
                        if isinstance(command, list):
                            ag_lines.extend(command)
                        else:
                            ag_lines.append(command)

            if action_group.title and ag_lines:
                lines.append('.SS ' + action_group.title)
                lines.extend(ag_lines)

        # Additional Section
        for section in self.parser._manpage:
            lines.append('.SH {}'.format(section['heading'].upper()))
            lines.append(self.format_text(section['content']))

        return '\n'.join(lines).strip('\n') + '\n'


class _ManpageFormatter(HelpFormatter):
    def __init__(self, prog, old_formatter):
        super().__init__(prog)
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

    def _format_action(self, action):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        if not action.help:
            # no help; start on same line and add a final newline
            tup = self._current_indent, '', action_header
            action_header = '%*s%s' % tup
        elif len(action_header) <= action_width:
            # short action name; start on the same line and pad two spaces
            tup = self._current_indent, '', action_width, action_header
            action_header = '%*s%-*s  ' % tup
        else:
            # long action name; start on the next line
            tup = self._current_indent, '', action_header
            action_header = '%*s%s' % tup

        # collect the pieces of the action help
        parts = [action_header]

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self.of._format_text(self._expand_help(action)).strip('\n')
            help_text = help_text.replace('\n', '\n.br\n')
            parts.append(help_text)

        # if there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        return [self._markup(p) for p in parts]

    def format_action(self, action):
        return self._format_action(action)

    def format_text(self, text):
        return self._markup(text.strip('\n').replace('\n', '\n.br\n') + '\n')
