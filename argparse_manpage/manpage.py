from argparse import SUPPRESS, HelpFormatter, _SubParsersAction, _HelpAction
from collections import OrderedDict
import datetime
import os
import time


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


DEFAULT_GROUP_NAMES_SUBCOMMANDS = {
    # We replace ArgumentGroup title (value) with alias (key).
    "arguments:": [
        'positional arguments',
    ],
    'options:': [
        'optional arguments',
        'options',
    ]
}


# all manpage attributes that can be set via CLI or setup.cfg
MANPAGE_DATA_ATTRS = (
    "authors",  # just "author" in setup.cfg, can be specified multiple times
    "description",
    "long_description",  # not in the manpage.py, we use parser.description
    "project_name",  # maps to distribution.get_name()
    "prog",
    "url",
    "version",
    "format",
    "manual_section",
    "manual_title",
)


def _markup(text):
    """
    Escape the text for the markdown format.
    """
    if isinstance(text, str):
        return text.replace('\\', '\\\\').replace('-', r'\-')
    return text


def get_manpage_data_from_distribution(distribution, data):
    """
    Update `data` with values from `distribution`.
    """
    # authors
    if not "authors" in data:
        author = distribution.get_author()
        if distribution.get_author_email():
            author += " <{}>".format(distribution.get_author_email())
        data["authors"] = [author]

    attrs = list(MANPAGE_DATA_ATTRS)
    attrs.remove("authors")
    attrs.remove("prog")  # not available, copied from 'project_name' later
    attrs.remove("format")  # not available, must be set in setup.cfg
    # we want the utility description, not the project description
    attrs.remove("description")
    for attr in attrs:
        if data.get(attr, None):
            continue

        # map data["project_name"] to distribution.get_name()
        get_attr = "name" if attr == "project_name" else attr

        getter = getattr(distribution, "get_" + get_attr, None)
        if not getter:
            continue
        value = getter()

        data[attr] = value

    if "prog" not in data:
        data["prog"] = data["project_name"]


def _get_footer_lines(data):
    ret = []
    project_name = data.get("project_name", "")
    authors = data.get("authors")
    url = data.get("url")

    needs_separator = False
    if authors:
        ret.append('.SH AUTHORS')
        for author in authors:
            ret.append(".nf")
            ret.append(author)
            ret.append(".fi")
        needs_separator = True

    if url:
        if needs_separator:
            ret.append("")
        ret.append(".SH DISTRIBUTION")
        ret.append("The latest version of {0} may "
                   "be downloaded from".format(_markup(project_name)))
        ret.append(".UR {0}".format(_markup(url)))
        ret.append(".UE")
    return ret


def get_footer(data):
    """
    Return a manual page footer based on the data returned from
    get_manpage_data_from_distribution().  Used only by the old build_manpage
    module.
    """
    return "\n".join(_get_footer_lines(data)) + "\n"


# This is already considered an API, and seems like a valid scenario:
# https://github.com/pypa/pipx/blob/fd6650bcaeca3088/scripts/generate_man.py

class Manpage(object):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, parser, _data=None, format='pretty'):
        """
        Manual page abstraction.  Generates, with the help of formater, a manual
        page by __str__() method.  Please avoid using the private _data
        argument (see https://github.com/praiskup/argparse-manpage/issues/7),
        instead override the `self.<ATTRIBUTE>` when needed.
        """
        self.prog = parser.prog
        self.parser = parser
        self.format = format
        self._data = _data or {}
        if not getattr(parser, '_manpage', None):
            self.parser._manpage = []

        self.formatter = self.parser._get_formatter()
        self.mf = _ManpageFormatter(self.prog, self.formatter, format=self.format)
        self.synopsis = self.parser.format_usage().split(':')[-1].split()

        self.date = self._data.get("date")
        if not self.date:
            builddate = datetime.datetime.utcfromtimestamp(
                int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
            )
            self.date = builddate.strftime('%Y-%m-%d')

        self.source = self._data.get("project_name")
        if not self.source:
            self.source = self.prog

        version = self._data.get("version")
        if version:
            self.source += " " + str(version)

        self.manual = self._data.get("manual_title")
        if not self.manual:
            self.manual = "Generated Python Manual"

        self.section = self._data.get("manual_section")
        if not self.section:
            self.section = 1

        self.description = self._data.get("description")

    def format_text(self, text):
        # Wrap by parser formatter and convert to manpage format
        return self.mf.format_text(self.formatter._format_text(text)).strip('\n')

    def __str__(self):
        lines = []

        # Header
        # per man (7) man-pages: .TH title section date source manual
        header = '.TH {title} "{section}" "{date}" "{source}" "{manual}"'
        lines.append(header.format(
            title=_markup(self.prog.upper()),
            section=self.section,
            date=_markup(self.date),
            source=_markup(self.source),
            manual=_markup(self.manual),
        ))

        # Name
        lines.append('.SH NAME')
        line = self.prog

        description = None
        if getattr(self.parser, 'man_short_description', None):
            # Let's keep this undocumented.  There's a way to specify this in
            # setup.cfg: 'description'
            description = self.parser.man_short_description
        if self.description:
            description = self.description
        if description:
            line += " - " + description
        lines.append(_markup(line))

        # Synopsis
        if self.synopsis:
            lines.append('.SH SYNOPSIS')
            lines.append('.B {}'.format(_markup(self.synopsis[0])))
            lines.append(' '.join(self.synopsis[1:]))

        lines.extend(self.mf.format_parser(self.parser))

        if self.parser.epilog != None:
            lines.append("")
            lines.append('.SH COMMENTS')
            lines.append(self.format_text(self.parser.epilog))

        # Additional Section
        for section in self.parser._manpage:
            lines.append('.SH {}'.format(section['heading'].upper()))
            lines.append(self.format_text(section['content']))

        lines.append("")
        lines.extend(self.mf.format_footer(self._data))
        return "\n".join(lines).strip("\n") + "\n"


def underline(text):
    """
    Wrap text with \fI for underlined text
    """
    return r'\fI\,{0}\/\fR'.format(_markup(text))


def bold(text):
    """ Wrap text by "bold" groff tags """
    return r"\fB{0}\fR".format(_markup(text))


def quoted(text):
    """ Wrap by single-quotes """
    return "'{0}'".format(text)


class _ManpageFormatter(HelpFormatter):
    def __init__(self, prog, old_formatter, format):
        super(HelpFormatter, self).__init__()
        self._prog = prog
        self.of = old_formatter
        assert format in ("pretty", "single-commands-section")
        self.format = format

    @staticmethod
    def _get_aliases_str(aliases):
        if not aliases:
            return ""
        return " (" + ", ".join(aliases) + ")"

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

    def _format_parser(self, parser, subcommand=None, aliases=None, help=None):
        # The parser "tree" looks like
        # ----------------------------
        # Parser -> [ActionGroup, ActionGroup, ..]
        # Group -> [Action, Action, ..]
        # Action -> Option
        # Action -> Subparsers
        # Subparser -> [Parser, Parser, ..] So called "choices".

        lines = []
        if subcommand:
            if self.format == "pretty":
                lines.append("")
                # start a new section for each command
                first_line = ".SH COMMAND"
                first_line += " " + underline(quoted(subcommand))
            elif self.format == "single-commands-section":
                # do not start a new section, start subsection of COMMANDS instead
                first_line = ".SS"
                first_line += " " + bold(subcommand + self._get_aliases_str(aliases))
            lines.append(first_line)

            if help:
                if self.format == "pretty":
                    # help is printed on top in the list of commands already
                    pass
                elif self.format == "single-commands-section":
                    # print help
                    lines.append(help)
                    lines.append("")

            lines.append(self.format_text(parser.format_usage()))

        if parser.description:
            if subcommand:
                lines.append("")
            else:
                lines.append(".SH DESCRIPTION")

            lines.append(self.format_text(parser.description))

        is_subsequent_ag = True
        for group in parser._action_groups:
            ag_lines = self._format_action_group(group, subcommand)
            if not ag_lines:
                continue
            if is_subsequent_ag:
                lines.append("")
            lines.extend(ag_lines)
            is_subsequent_ag = True

        return lines

    def format_parser(self, parser):
        """
        Return lines Groff formatted text for given parser
        """
        return self._format_parser(parser)

    def _format_action(self, action):
        parts = []
        parts.append('.TP')

        action_header = self._format_action_invocation(action)
        parts.append(action_header)

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self.of._format_text(self._expand_help(action)).strip('\n')
            parts.append(self.format_text(help_text))

        return parts

    def _format_ag_subcommands(self, actions, prog):
        lines = []

        for action in actions:
            if getattr(action, 'help', None) == SUPPRESS:
                continue
            lines.append('.TP')
            lines.append(bold(prog) + ' ' + underline(action.dest))
            if hasattr(action, 'help'):
                lines.append(self.format_text(action.help))

        return '\n'.join(lines)

    def _format_subparsers(self, action_group, action, subcommand=None):
        lines = []

        if subcommand:
            if self.format == "pretty":
                # start a new section for each command
                lines.append('.SH')
                title = action_group.title.upper()
                title += " " + underline(quoted(subcommand))
                lines.append(title)
            elif self.format == "single-commands-section":
                # do not start a new section, append subsections to the COMMANDS section
                pass
        else:
            # start a new section on top-level
            lines.append('.SH')
            title = action_group.title.upper()
            lines.append(title)

        if self.format == "pretty":
            # print list of subcommands
            lines.append(self._format_ag_subcommands(action._choices_actions,
                         subcommand or self._prog))
        elif self.format == "single-commands-section":
            # skip printing list of subcommands
            pass

        # gather (sub-)command aliases
        command_aliases = {}
        command_aliases_names = set()
        for name, command in action._name_parser_map.items():
            if command not in command_aliases:
                command_aliases[command] = []
            else:
                command_aliases[command].append(name)
                command_aliases_names.add(name)

        command_help = {}
        for i in action._choices_actions:
            command_help[i.dest] = i.help

        for name, choice in action.choices.items():
            if name in command_aliases_names:
                # don't print aliased commands multiple times
                continue
            new_subcommand = "{} {}".format(subcommand or self._prog, name)
            aliases = command_aliases[choice]
            help = command_help.get(name, None)
            if help == SUPPRESS:
                # don't print hidden commands
                continue
            lines.extend(self._format_parser(choice, new_subcommand, aliases, help))

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

            if some_action:
                # Separate actions
                content.append("")

            some_action = True
            content.extend(self._format_action(action))

        # We don't print empty argument groups.
        if not some_action:
            return []

        title = action_group.title

        group_names = DEFAULT_GROUP_NAMES
        if subcommand:
            if self.format == "pretty":
                pass
            elif self.format == "single-commands-section":
                group_names = DEFAULT_GROUP_NAMES_SUBCOMMANDS

        for replace_with, defaults in group_names.items():
            if title in defaults:
                title = replace_with

        if subcommand:
            if self.format == "pretty":
                title = title.upper() if title else ""
                if title:
                    title += " " + underline(quoted(subcommand))
                title = [] if not title else [".SH " + title]
            elif self.format == "single-commands-section":
                title = [] if not title else [title]
        else:
            title = title.upper() if title else ""
            title = [] if not title else [".SH " + title]

        description = []
        if action_group.description:
            description.append(self.format_text(action_group.description))
            description.append("")

        if subcommand:
            if self.format == "pretty":
                # don't indent the whole content of a subcommand
                pass
            elif self.format == "single-commands-section":
                # indent the whole content of a subcommand
                content = [".RS 7"] + content + [".RE"] + [""]

        return title + description + content

    @staticmethod
    def format_text(text):
        """
        Format a block of text as it was a single line in set of other lines
        (e.g. no trailing newline).
        """
        return _markup(text.strip('\n'))

    @staticmethod
    def format_footer(data):
        """
        Get lines for footer.
        """
        return _get_footer_lines(data)
