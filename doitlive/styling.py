# -*- coding: utf-8 -*-
"""Functions and classes for styling sessions."""
import os
import getpass
import datetime as dt
import socket
from collections import OrderedDict

import click
from click import style
from click import echo as click_echo
from click.termui import strip_ansi

from doitlive.exceptions import ConfigurationError
from doitlive.compat import PY2
from doitlive.version_control import (
    get_current_git_branch,
    get_current_hg_bookmark,
    get_current_hg_branch,
    get_current_hg_id,
    get_current_vcs_branch,
)

env = os.environ

THEMES = OrderedDict([
    ('default', u'{user.cyan.bold}@{hostname.blue}:{dir.green} $'),

    ('sorin', u'{cwd.blue} {vcs_branch.cyan} '
              '{r_angle.red}{r_angle.yellow}{r_angle.green}'),

    ('stev', u'{cwd.blue} {vcs_branch.cyan} '
             '{r_angle.green}'),

    ('damoekri', u'{dir.cyan} {r_angle.green}'),
    ('smiley', u'{vcs_branch.blue.paren}{dir.white.bold} {TTY.GREEN}ツ{TTY.RESET}'),

    ('nicolauj', u'{r_angle.white}'),

    ('steeef', u'{user.red} at {hostname.yellow} in {cwd.green} '
               u'{vcs_branch.cyan.paren}\n$'),

    ('redhat', u'[{user}@{hostname} {dir}]$'),
    ('redhat_color', u'[{user.red.bold}@{hostname.red} {dir.blue}]$'),

    ('walters', u'{user}@{hostname.underlined}>'),
    ('walters_color', u'{user.cyan.bold}@{hostname.blue.underlined}>'),

    ('minimal', u'{dir} {vcs_branch.square} »'),
    ('minimal_color', u'{dir.cyan} {vcs_branch.blue.square} »'),

    ('osx', u'{hostname}:{dir} {user}$'),
    ('osx_color', u'{hostname.blue}:{dir.green} {user.cyan}$'),

    ('pws', u'{TTY.BOLD}+{TTY.YELLOW}{now:%I:%M}{TTY.RESET}%'),

    ('robbyrussell', u'{r_arrow.red} {dir.cyan} {vcs_branch.red.paren.git}'),

    ('giddie', u'{user.magenta}@{hostname.yellow}|{cwd.green} '
               u'on {vcs_branch.magenta}\n{TTY.BLUE}±{TTY.RESET}')

])

class Style(object):
    """Descriptor that adds ANSI styling to a string when accessed."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        return TermString(style(instance, **self.kwargs))

if PY2:
    text_type = unicode  # noqa
else:
    text_type = str  # noqa

class TermString(text_type):
    """A string-like object that can be formatted with ANSI styles. Useful for
    styling strings within a string.format "template."
    """

    # Colors

    blue = Style(fg='blue')
    magenta = Style(fg='magenta')
    red = Style(fg='red')
    white = Style(fg='white')
    green = Style(fg='green')
    black = Style(fg='black')
    yellow = Style(fg='yellow')
    cyan = Style(fg='cyan')
    reset = Style(fg='reset')

    # Styling

    bold = Style(bold=True)
    blink = Style(blink=True)
    underlined = Style(underline=True)
    dim = Style(dim=True)
    inverse = Style(reverse=True)

    def _bracketed(self, left, right):
        if strip_ansi(self):
            return TermString(u''.join([left, self, right]))
        else:
            return TermString(u'\b')

    @property
    def paren(self):
        return self._bracketed(u'(', u')')

    @property
    def square(self):
        return self._bracketed(u'[', u']')

    @property
    def curly(self):
        return self._bracketed(u'{', u'}')

    def _vcs(self, vcsname):
        if strip_ansi(self):
            return TermString(u'{}:{}'.format(style(vcsname, fg='blue'), self))
        else:
            return TermString(u'\b')

    @property
    def git(self):
        return self._vcs(u'git')

    @property
    def hg(self):
        return self._vcs(u'hg')

# Some common symbols used in prompts
R_ANGLE = TermString(u'❯')
R_ANGLE_DOUBLE = TermString(u'»')
R_ARROW = TermString(u'➔')
DOLLAR = TermString(u'$')
PERCENT = TermString(u'%')
NEW_LINE = TermString(u'\n')


class ANSICode(object):
    """Descriptor that returns the ANSI code the given styles passed to
    the constructor.
    """

    def __init__(self, **styles):
        self.styles = styles

    def __get__(self, instance, owner):
        reset = self.styles.pop('reset', False)
        return style('', reset=reset, **self.styles)


class TTY(object):
    """Namespace for all ANSI escape sequences provided by click."""

    BLUE = ANSICode(fg='blue')
    MAGENTA = ANSICode(fg='magenta')
    RED = ANSICode(fg='red')
    WHITE = ANSICode(fg='white')
    GREEN = ANSICode(fg='green')
    BLACK = ANSICode(fg='black')
    YELLOW = ANSICode(fg='yellow')
    CYAN = ANSICode(fg='cyan')
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
        return TermString(u'\b')


def format_prompt(prompt):
    try:
        return prompt.format(**get_prompt_state())
    except KeyError:
        raise ConfigurationError('Invalid variable in prompt template.')

def echo(message=None, file=None, nl=True, err=False, color=None, carriage_return=False):
    """
    Patched click echo function.
    """
    message = message or ''
    if carriage_return and nl:
        click_echo(message + '\r\n', file, False, err, color)
    elif carriage_return and not nl:
        click_echo(message + '\r', file, False, err, color)
    else:
        click_echo(message, file, nl, err, color)

def make_prompt_formatter(template):
    tpl = THEMES.get(template) or template
    return lambda: format_prompt(tpl)


def echo_prompt(template):
    prompt = make_prompt_formatter(template)()
    echo(prompt + ' ', nl=False)


def get_prompt_state():
    full_cwd = os.getcwd()
    home = env.get('HOME', '')
    cwd_raw = full_cwd.replace(home, '~')
    dir_raw = '~' if full_cwd == home else os.path.split(full_cwd)[-1]
    return {
        'user': TermString(getpass.getuser()),
        'cwd': TermString(cwd_raw),
        'dir': TermString(dir_raw),
        'hostname': TermString(socket.gethostname()),
        'git_branch': _branch_to_term_string(get_current_git_branch()),
        'hg_id': TermString(get_current_hg_id()),
        'hg_branch': _branch_to_term_string(get_current_hg_branch()),
        'hg_bookmark': TermString(get_current_hg_bookmark()),
        'vcs_branch': _branch_to_term_string(get_current_vcs_branch()),
        # Symbols
        'r_angle': R_ANGLE,
        'r_angle_double': R_ANGLE_DOUBLE,
        'r_arrow': R_ARROW,
        'dollar': DOLLAR,
        'percent': PERCENT,
        'now': dt.datetime.now(),
        'new_line': NEW_LINE,
        'nl': NEW_LINE,
        # ANSI values object
        'TTY': TTY,
    }
