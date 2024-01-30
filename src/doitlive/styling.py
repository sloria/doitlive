"""Functions and classes for styling sessions."""
import datetime as dt
import getpass
import os
import socket
from collections import OrderedDict

import click
from click import echo as click_echo
from click import style
from click.termui import strip_ansi

from doitlive.exceptions import ConfigurationError
from doitlive.version_control import (
    get_current_git_branch,
    get_current_hg_bookmark,
    get_current_hg_branch,
    get_current_hg_id,
    get_current_vcs_branch,
)

env = os.environ

THEMES = OrderedDict(
    [
        ("default", "{user.cyan.bold}@{hostname.blue}:{dir.green} $"),
        (
            "sorin",
            "{cwd.blue} {vcs_branch.cyan} "
            "{r_angle.red}{r_angle.yellow}{r_angle.green}",
        ),
        ("stev", "{cwd.blue} {vcs_branch.cyan} " "{r_angle.green}"),
        ("damoekri", "{dir.cyan} {r_angle.green}"),
        ("smiley", "{vcs_branch.blue.paren}{dir.white.bold} {TTY.GREEN}ツ{TTY.RESET}"),
        ("nicolauj", "{r_angle.white}"),
        (
            "steeef",
            "{user.red} at {hostname.yellow} in {cwd.green} "
            "{vcs_branch.cyan.paren}\n$",
        ),
        ("redhat", "[{user}@{hostname} {dir}]$"),
        ("redhat_color", "[{user.red.bold}@{hostname.red} {dir.blue}]$"),
        ("walters", "{user}@{hostname.underlined}>"),
        ("walters_color", "{user.cyan.bold}@{hostname.blue.underlined}>"),
        ("minimal", "{dir} {vcs_branch.square} »"),
        ("minimal_color", "{dir.cyan} {vcs_branch.blue.square} »"),
        ("osx", "{hostname}:{dir} {user}$"),
        ("osx_color", "{hostname.blue}:{dir.green} {user.cyan}$"),
        ("pws", "{TTY.BOLD}+{TTY.YELLOW}{now:%I:%M}{TTY.RESET}%"),
        ("robbyrussell", "{r_arrow.red} {dir.cyan} {vcs_branch.red.paren.git}"),
        (
            "giddie",
            "{user.magenta}@{hostname.yellow}|{cwd.green} "
            "on {vcs_branch.magenta}\n{TTY.BLUE}±{TTY.RESET}",
        ),
        ("deadsimple", "$"),
    ]
)


class Style:
    """Descriptor that adds ANSI styling to a string when accessed."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        return TermString(style(instance, **self.kwargs))


class TermString(str):
    """A string-like object that can be formatted with ANSI styles. Useful for
    styling strings within a string.format "template."
    """

    # Colors

    blue = Style(fg="blue")
    magenta = Style(fg="magenta")
    red = Style(fg="red")
    white = Style(fg="white")
    green = Style(fg="green")
    black = Style(fg="black")
    yellow = Style(fg="yellow")
    cyan = Style(fg="cyan")
    reset = Style(fg="reset")

    bright_black = Style(fg="bright_black")
    bright_red = Style(fg="bright_red")
    bright_green = Style(fg="bright_green")
    bright_yellow = Style(fg="bright_yellow")
    bright_blue = Style(fg="bright_blue")
    bright_magenta = Style(fg="bright_magenta")
    bright_cyan = Style(fg="bright_cyan")
    bright_white = Style(fg="bright_white")

    # Styling

    bold = Style(bold=True)
    blink = Style(blink=True)
    underlined = Style(underline=True)
    dim = Style(dim=True)
    inverse = Style(reverse=True)

    def _bracketed(self, left, right):
        if strip_ansi(self):
            return TermString("".join([left, self, right]))
        else:
            return TermString("\b")

    @property
    def paren(self):
        return self._bracketed("(", ")")

    @property
    def square(self):
        return self._bracketed("[", "]")

    @property
    def curly(self):
        return self._bracketed("{", "}")

    def _vcs(self, vcsname):
        if strip_ansi(self):
            return TermString("{}:{}".format(style(vcsname, fg="blue"), self))
        else:
            return TermString("\b")

    @property
    def git(self):
        return self._vcs("git")

    @property
    def hg(self):
        return self._vcs("hg")


# Some common symbols used in prompts
R_ANGLE = TermString("❯")
R_ANGLE_DOUBLE = TermString("»")
R_ARROW = TermString("➔")
DOLLAR = TermString("$")
PERCENT = TermString("%")
NEW_LINE = TermString("\n")


class ANSICode:
    """Descriptor that returns the ANSI code the given styles passed to
    the constructor.
    """

    def __init__(self, **styles):
        self.styles = styles

    def __get__(self, instance, owner):
        reset = self.styles.pop("reset", False)
        return style("", reset=reset, **self.styles)


class TTY:
    """Namespace for all ANSI escape sequences provided by click."""

    BLUE = ANSICode(fg="blue")
    MAGENTA = ANSICode(fg="magenta")
    RED = ANSICode(fg="red")
    WHITE = ANSICode(fg="white")
    GREEN = ANSICode(fg="green")
    BLACK = ANSICode(fg="black")
    YELLOW = ANSICode(fg="yellow")
    CYAN = ANSICode(fg="cyan")
    RESET = click.termui._ansi_reset_all  # pylint: disable=W0212
    BOLD = ANSICode(bold=True)
    BLINK = ANSICode(blink=True)
    UNDERLINE = ANSICode(underline=True)
    DIM = ANSICode(dim=True)


def _branch_to_term_string(branch_string):
    if strip_ansi(branch_string):
        return TermString(branch_string)
    else:
        # Prevent extra space when not in a VCS repo
        return TermString("\b")


def format_prompt(prompt):
    try:
        return prompt.format(**get_prompt_state())
    except KeyError:
        raise ConfigurationError("Invalid variable in prompt template.")


def echo(
    message=None, file=None, nl=True, err=False, color=None, carriage_return=False
):
    """
    Patched click echo function.
    """
    message = message or ""
    if carriage_return and nl:
        click_echo(message + "\r\n", file, False, err, color)
    elif carriage_return and not nl:
        click_echo(message + "\r", file, False, err, color)
    else:
        click_echo(message, file, nl, err, color)


def make_prompt_formatter(template):
    tpl = THEMES.get(template) or template
    return lambda: format_prompt(tpl)


def echo_prompt(template):
    prompt = make_prompt_formatter(template)()
    echo(prompt + " ", nl=False)


def get_prompt_state():
    full_cwd = os.getcwd()
    home = env.get("HOME", "")
    cwd_raw = full_cwd.replace(home, "~")
    dir_raw = "~" if full_cwd == home else os.path.split(full_cwd)[-1]
    return {
        "user": TermString(getpass.getuser()),
        "cwd": TermString(cwd_raw),
        "dir": TermString(dir_raw),
        "hostname": TermString(socket.gethostname()),
        "git_branch": _branch_to_term_string(get_current_git_branch()),
        "hg_id": TermString(get_current_hg_id()),
        "hg_branch": _branch_to_term_string(get_current_hg_branch()),
        "hg_bookmark": TermString(get_current_hg_bookmark()),
        "vcs_branch": _branch_to_term_string(get_current_vcs_branch()),
        # Symbols
        "r_angle": R_ANGLE,
        "r_angle_double": R_ANGLE_DOUBLE,
        "r_arrow": R_ARROW,
        "dollar": DOLLAR,
        "percent": PERCENT,
        "now": dt.datetime.now(),
        "new_line": NEW_LINE,
        "nl": NEW_LINE,
        # ANSI values object
        "TTY": TTY,
    }
