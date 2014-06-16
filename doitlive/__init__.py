#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  doitlive
  ~~~~~~~~

  :copyright: (c) 2014 by Steven Loria.
  :license: MIT, see LICENSE for more details.
"""

from __future__ import unicode_literals
import os
import sys
import re
import io
import getpass
import subprocess
from tempfile import NamedTemporaryFile

import click
from click import echo, style, getchar

__version__ = "0.1.0-dev"
__author__ = "Steven Loria"
__license__ = "MIT"

env = os.environ
PY2 = int(sys.version[0]) == 2
if PY2:
    basestring = basestring
else:
    basestring = (str, bytes)

HERE = os.path.abspath(os.path.dirname(__file__))
DEMO_FILE = os.path.join(HERE, 'doitlive-demo.sh')
ESC = u'\x1b'
RETURNS = {'\r', '\n'}
OPTION_RE = re.compile(r'^#\s?doitlive\s+'
            '(?P<option>prompt|shell|alias|env):\s*(?P<arg>.+)$')

class PromptState(object):
    user = ''
    cwd = ''
    display_dir = ''

    def update(self):
        self.user, self.cwd = getpass.getuser(), os.getcwd()
        self.display_cwd = '~' if self.cwd == env['HOME'] else os.path.split(self.cwd)[-1]

_prompt_state = PromptState()

def echof(text, *args, **kwargs):
    echo(style(text, *args, **kwargs))

def get_default_prompt():
    if env.get('DOITLIVE_PROMPT'):
        return env['DOITLIVE_PROMPT']
    _prompt_state.update()
    return '{user}@{dir}: $'.format(
        user=style(_prompt_state.user, fg='cyan', bold=True),
        dir=style(_prompt_state.display_cwd, fg='green')
    )

def ensure_utf(string):
    return string.encode('utf-8') if PY2 else string


def run_command(cmd, shell=None, check_output=False, aliases=None, envvars=None):
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
            if check_output:
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

def magictype(text, shell, check_output,
        prompt=get_default_prompt, aliases=None, envvars=None):
    if callable(prompt):
        prompt = prompt()
    echo(prompt + ' ', nl=False)
    for c in text:
        in_char = getchar()
        if in_char == ESC:
            echo()
            raise click.Abort()
        echo(c, nl=False)
    wait_for(RETURNS)
    output = run_command(text, shell, check_output=check_output,
        aliases=aliases, envvars=envvars)
    if isinstance(output, basestring):
        echo(output)

def format_prompt(prompt):
    _prompt_state.update()
    return prompt.format(
        user=_prompt_state.user,
        cwd=_prompt_state.display_cwd,
        full_cwd=_prompt_state.cwd
    )

def run(commands, shell='/bin/bash',
        check_output=False, prompt=get_default_prompt):
    echof("We'll do it live!", fg='red', bold=True)
    echof('STARTING SESSION: Press ESC at any time to exit.', fg='yellow', bold=True)

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
                    prompt = format_prompt(arg)
                elif option == 'shell':
                    shell = arg
                elif option == 'alias':
                    aliases.append(arg)
                elif option == 'env':
                    envvars.append(arg)
            continue
        magictype(command, shell, check_output,
            prompt=prompt, aliases=aliases, envvars=envvars)
    if callable(prompt):
        prompt = prompt()
    echo(prompt + ' ', nl=False)
    wait_for(RETURNS)
    echof("FINISHED SESSION", fg='yellow', bold=True)

@click.option('--check-output', is_flag=True, default=False)
@click.option('--shell', '-i', default='/bin/bash')
@click.argument('session_file', type=click.File('r', encoding='utf-8'))
@click.version_option(__version__, '--version', '-v')
@click.command(context_settings={'help_option_names': ('-h', '--help')})
def cli(session_file, shell, check_output):
    """The doitlive CLI.

    \b
    How to use:
        1. Create a file called session.sh
        2. Put some bash commands in that file.
        3. Run "doitlive session.sh"
        4. Type like a madman.

    Press ESC or ^C at any time to exit the session.
    To see a demo session, run "doitlive-demo".
    """
    run(session_file.readlines(),
        shell=shell,
        check_output=check_output)


@click.option('--check-output', is_flag=True, default=False)
@click.option('--shell', '-i', default='/bin/bash')
@click.command()
def demo(shell, check_output):
    """Run a demo doitlive session."""
    with io.open(DEMO_FILE, 'r', encoding='utf-8') as fp:
        run(fp.readlines(), shell=shell, check_output=check_output)


if __name__ == '__main__':
    cli()
