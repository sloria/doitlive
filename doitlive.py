#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  doitlive
  ~~~~~~~~

  A tool for "live" presentations in the terminal.

  :copyright: (c) 2014 by Steven Loria.
  :license: MIT, see LICENSE for more details.
"""

from __future__ import unicode_literals
import os
import sys
import re
import getpass
import socket
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict

import click
from click import echo, style, secho, getchar
from click.termui import strip_ansi

__version__ = '1.0'
__author__ = 'Steven Loria'
__license__ = 'MIT'

env = os.environ
PY2 = int(sys.version[0]) == 2
if not PY2:
    unicode = str
    basestring = (str, bytes)

THEMES = OrderedDict([
    ('default', '{user.cyan.bold}@{hostname.blue}:{dir.green} $'),

    ('sorin', '{cwd.cyan} {git_branch.green.square} '
        '{r_angle.red}{r_angle.yellow}{r_angle.green}'),

    ('nicolauj', '{r_angle.white}'),

    ('steeef', '{user.red} at {hostname.yellow} in {cwd.green} '
                '{git_branch.cyan.paren}\n$'),

    ('redhat', '[{user}@{hostname} {dir}]$'),
    ('redhat_color', '[{user.cyan.bold}@{hostname.blue} {dir.green}]$'),

    ('walters', '{user}@{hostname.underlined}>'),
    ('walters_color', '{user.cyan.bold}@{hostname.blue.underlined}>'),

    ('minimal', '{dir} {git_branch.square} »'),
    ('minimal_color', '{dir.cyan} {git_branch.blue.square} »'),

    ('osx', '{hostname}:{dir} {user}$'),
    ('osx_color', '{hostname.blue}:{dir.green} {user.cyan}$')
])


ESC = '\x1b'
RETURNS = {'\r', '\n'}
OPTION_RE = re.compile(r'^#\s?doitlive\s+'
            '(?P<option>prompt|shell|alias|env|speed):'
            '\s*(?P<arg>.+)$')


TESTING = False


class TermString(unicode):
    """A string-like object that can be formatted with ANSI styles. Useful for
    styling strings within a string.format "template."
    """

    def _styled(self, **styles):
        return TermString(style(self, **styles))

    # Colors

    @property
    def blue(self): return self._styled(fg='blue')
    @property
    def magenta(self): return self._styled(fg='magenta')
    @property
    def red(self): return self._styled(fg='red')
    @property
    def white(self): return self._styled(fg='white')
    @property
    def green(self): return self._styled(fg='green')
    @property
    def black(self): return self._styled(fg='black')
    @property
    def yellow(self): return self._styled(fg='yellow')
    @property
    def cyan(self): return self._styled(fg='cyan')
    @property
    def reset(self): return self._styled(fg='reset')

    # Styling

    @property
    def bold(self):
        return self._styled(bold=True)

    @property
    def blink(self):
        return self._styled(blink=True)

    @property
    def underlined(self):
        return self._styled(underline=True)

    @property
    def dim(self):
        return self._styled(dim=True)

    def _bracketed(self, left, right):
        if strip_ansi(self):
            return TermString(''.join([left, self, right]))
        else:
            return TermString('')

    @property
    def paren(self):
        return self._bracketed('(', ')')

    @property
    def square(self):
        return self._bracketed('[', ']')

    @property
    def curly(self):
        return self._bracketed('{', '}')


def get_current_git_branch():
    command = ['git', 'symbolic-ref', '--short', '-q', 'HEAD']
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return out.strip()
    except subprocess.CalledProcessError:
        pass
    return ''


# Some common symbols used in prompts
R_ANGLE = TermString('❯')
R_ANGLE_DOUBLE = TermString('»')
DOLLAR = TermString('$')
PERCENT = TermString('%')

def get_prompt_state():
    full_cwd = os.getcwd()
    cwd_raw = full_cwd.replace(env['HOME'], '~')
    dir_raw = '~' if full_cwd == env['HOME'] else os.path.split(full_cwd)[-1]
    return {
        'user': TermString(getpass.getuser()),
        'cwd': TermString(cwd_raw),
        'dir': TermString(dir_raw),
        'hostname': TermString(socket.gethostname()),
        'git_branch': TermString(get_current_git_branch()),
        # Symbols
        'r_angle': R_ANGLE,
        'r_angle_double': R_ANGLE_DOUBLE,
        'dollar': DOLLAR,
        'percent': PERCENT,
    }


def ensure_utf(string):
    return string.encode('utf-8') if PY2 else string


def run_command(cmd, shell=None, aliases=None, envvars=None, test_mode=True):
    shell = shell or env.get('DOITLIVE_INTERPRETER') or '/bin/bash'
    if cmd.startswith("cd "):
        directory = cmd.split()[1]
        os.chdir(os.path.expanduser(directory))
    else:
        # Need to make a temporary command file so that $ENV are used correctly
        # and that shell built-ins, e.g. "source" work
        with NamedTemporaryFile('w') as fp:
            fp.write('#!{0}\n'.format(shell))
            fp.write('# -*- coding: utf-8 -*-\n')
            # Make aliases work in bash:
            if 'bash' in shell:
                fp.write("shopt -s expand_aliases\n")

            if envvars:
                # Write envvars
                for envvar in envvars:
                    envvar_line = 'export {0}\n'.format(envvar)
                    fp.write(ensure_utf(envvar_line))

            if aliases:
                # Write aliases
                for alias in aliases:
                    alias_line = 'alias {0}\n'.format(alias)
                    fp.write(ensure_utf(alias_line))
            cmd_line = cmd + '\n'
            fp.write(ensure_utf(cmd_line))
            fp.flush()
            if test_mode:
                return subprocess.check_output([shell, fp.name])
            else:
                return subprocess.call([shell, fp.name])

def wait_for(chars):
    while True:
        in_char = getchar()
        if in_char == ESC:
            echo()
            raise click.Abort()
        if in_char in chars:
            echo()
            return in_char

def magictype(text, shell, prompt_template='default', aliases=None,
        envvars=None, speed=1, test_mode=False):
    prompt_func = make_prompt_formatter(prompt_template)
    prompt = prompt_func()
    echo(prompt + ' ', nl=False)
    i = 0
    while i < len(text):
        char = text[i:i + speed]
        in_char = getchar()
        if in_char == ESC:
            echo()
            raise click.Abort()
        echo(char, nl=False)
        i += speed
    wait_for(RETURNS)
    output = run_command(text, shell, aliases=aliases, envvars=envvars,
        test_mode=test_mode)
    if isinstance(output, basestring):
        echo(output)

def format_prompt(prompt):
    return prompt.format(**get_prompt_state())


def make_prompt_formatter(template):
    tpl = THEMES.get(template) or template
    return lambda: format_prompt(tpl)


def run(commands, shell='/bin/bash', prompt_template='default', speed=1,
        test_mode=False):
    secho("We'll do it live!", fg='red', bold=True)
    secho('STARTING SESSION: Press ESC at any time to exit.', fg='yellow', bold=True)

    click.pause()
    click.clear()
    aliases, envvars = [], []
    for line in commands:
        command = line.strip()
        if not command:
            continue
        if command.startswith('#'):
            # Parse comment magic
            match = OPTION_RE.match(command)
            if match:
                option, arg = match.group('option'), match.group('arg')
                if option == 'prompt':
                    prompt_template = arg
                elif option == 'shell':
                    shell = arg
                elif option == 'alias':
                    aliases.append(arg)
                elif option == 'env':
                    envvars.append(arg)
                elif option == 'speed':
                    speed = int(arg)
            continue
        magictype(command, shell, prompt_template=prompt_template, aliases=aliases,
            envvars=envvars, speed=speed, test_mode=test_mode)
    prompt = make_prompt_formatter(prompt_template)()
    echo(prompt + ' ', nl=False)
    wait_for(RETURNS)
    secho("FINISHED SESSION", fg='yellow', bold=True)


@click.version_option(__version__, '--version', '-v')
@click.option('--shell', '-S', metavar='<shell>',
    default='/bin/bash', help='The shell to use.', show_default=True)
@click.option('--speed', '-s', metavar='<int>', default=1, help='Typing speed.',
    show_default=True)
@click.option('--themes-preview', '-T', is_flag=True, default=False,
    is_eager=True, help='Preview the available prompt themes.')
@click.option('--themes', '-t', is_flag=True, default=False,
    is_eager=True, help='List the available prompt themes.')
@click.option('--prompt', '-p', metavar='<prompt_theme>',
    default='default', type=click.Choice(THEMES.keys()),
    help='Prompt theme.',
    show_default=True)
@click.argument('session_file', required=False, type=click.File('r', encoding='utf-8'))
@click.command(context_settings={'help_option_names': ('-h', '--help')})
def cli(session_file, shell, speed, prompt, themes, themes_preview):
    """doitlive: A tool for "live" presentations in the terminal

    \b
    How to use:
        1. Create a file called session.sh. Fill it with bash commands.
        2. Run "doitlive session.sh"
        3. Type like a madman.

    Press ESC or ^C at any time to exit the session.
    To see a demo session, run "doitlive-demo".
    """
    if themes_preview:
        preview_themes()
    elif themes:
        list_themes()
    elif session_file is not None:
        run(session_file.readlines(),
            shell=shell,
            speed=speed,
            test_mode=TESTING,
            prompt_template=prompt)
    else:
        raise click.UsageError('Must provide a SESSION_FILE. '
            'Run "doitlive --help" for more options.')

def preview_themes():
    secho('Theme previews:', bold=True)
    echo()
    for name, template in THEMES.items():
        echo('"{}" theme:'.format(name))
        echo(format_prompt(template), nl=False)
        echo(' command arg1 arg2 ... argn')
        echo()

def list_themes():
    secho('Available themes:', bold=True)
    echo(' '.join(THEMES.keys()))


DEMO = [
    'echo "Greetings"',
    'echo "This is just a demo session"',
    'echo "For more info, check out the home page..."',
    'echo "http://doitlive.rtfd.org"'
]


@click.option('--shell', '-S', metavar='<shell>',
    default='/bin/bash', help='The shell to use.', show_default=True)
@click.option('--speed', '-s', metavar='<int>', default=1, help='Typing speed.',
    show_default=True)
@click.option('--prompt', '-p', metavar='<prompt_theme>',
    default='default', type=click.Choice(THEMES.keys()),
    help='Prompt theme.',
    show_default=True)
@click.command()
def demo(shell, speed, prompt):
    """Run a demo doitlive session."""
    run(DEMO, shell=shell, speed=speed, test_mode=TESTING, prompt_template=prompt)


if __name__ == '__main__':
    cli()
