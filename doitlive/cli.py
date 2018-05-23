# -*- coding: utf-8 -*-
import functools
import os
import re
import shlex
import sys
import textwrap
from codecs import open

import click
import click_completion
from click import secho, style
from click_didyoumean import DYMGroup

from doitlive.__version__ import __version__
from doitlive.compat import ensure_utf8
from doitlive.exceptions import SessionError
from doitlive.keyboard import (RETURNS, magicrun, magictype, run_command,
                               wait_for)
from doitlive.python_consoles import PythonRecorderConsole, start_python_player
from doitlive.styling import THEMES, echo, echo_prompt, format_prompt
from doitlive.termutils import get_default_shell

env = os.environ
click_completion.init()


OPTION_RE = re.compile(r'^#\s?doitlive\s+'
                       r'(?P<option>prompt|shell|alias|env|speed'
                       r'|unalias|unset|commentecho):\s*(?P<arg>.+)$')

TESTING = False


def write_directives(fp, directive, args):
    if args:
        for arg in args:
            line = '#doitlive {directive}: {arg}\n'.format(**locals())
            fp.write(ensure_utf8(line))
    return None


class SessionState(dict):
    """Stores information about a fake terminal session."""
    TRUTHY = set(['true', 'yes', '1'])

    def __init__(self, shell, prompt_template, speed,
                 aliases=None, envvars=None, extra_commands=None,
                 test_mode=False, commentecho=False):
        aliases = aliases or []
        envvars = envvars or []
        extra_commands = extra_commands or []
        dict.__init__(self, shell=shell, prompt_template=prompt_template,
                      speed=speed, aliases=aliases, envvars=envvars,
                      extra_commands=extra_commands,
                      test_mode=test_mode, commentecho=commentecho)

    def add_alias(self, alias):
        self['aliases'].append(alias)

    def add_envvar(self, envvar):
        self['envvars'].append(envvar)

    def add_command(self, command):
        self['extra_commands'].append(command)

    def set_speed(self, speed):
        self['speed'] = int(speed)

    def set_template(self, template):
        self['prompt_template'] = template

    def set_shell(self, shell):
        self['shell'] = shell

    def _remove_var(self, key, variable):
        for each in self[key]:
            value, cmd = each.split('=')
            if variable == value.strip():
                self[key].remove(each)
                return True
        return None

    def remove_alias(self, alias):
        return self._remove_var('aliases', alias)

    def remove_envvar(self, envvar):
        return self._remove_var('envvars', envvar)

    def commentecho(self, doit=None):
        if doit is not None:
            doit = doit.lower()
            self['commentecho'] = doit in self.TRUTHY
        return self['commentecho']


# Map of option names => function that modifies session state
OPTION_MAP = {
    'prompt': lambda state, arg: state.set_template(arg),
    'shell': lambda state, arg: state.set_shell(arg),
    'alias': lambda state, arg: state.add_alias(arg),
    'env': lambda state, arg: state.add_envvar(arg),
    'speed': lambda state, arg: state.set_speed(arg),
    'unalias': lambda state, arg: state.remove_alias(arg),
    'unset': lambda state, arg: state.remove_envvar(arg),
    'commentecho': lambda state, arg: state.commentecho(arg),
}

SHELL_RE = re.compile(r'```(python|ipython)')


def run(commands, shell=None, prompt_template='default', speed=1,
        quiet=False, test_mode=False, commentecho=False):
    """Main function for "magic-running" a list of commands."""
    if not quiet:
        secho("We'll do it live!", fg='red', bold=True)
        secho('STARTING SESSION: Press Ctrl-C at any time to exit.',
              fg='yellow', bold=True)
        click.pause()

    click.clear()
    state = SessionState(shell=shell, prompt_template=prompt_template,
                         speed=speed, test_mode=test_mode,
                         commentecho=commentecho)

    i = 0
    while i < len(commands):
        command = commands[i].strip()
        command_as_list = shlex.split(ensure_utf8(command))
        i += 1
        if not command:
            continue
        shell_match = SHELL_RE.match(command)
        if command.startswith('#'):
            # Parse comment magic
            match = OPTION_RE.match(command)
            if match:
                option, arg = match.group('option'), match.group('arg')
                func = OPTION_MAP[option]
                func(state, arg)
            elif state.commentecho():
                comment = command.lstrip("#")
                secho(comment, fg='yellow', bold=True)
            continue
        # Handle 'export' and 'alias' commands by storing them in SessionState
        elif command_as_list and command_as_list[0] in ['alias', 'export']:
            magictype(command,
                      prompt_template=state['prompt_template'],
                      speed=state['speed'])
            # Store the raw commands instead of using add_envvar and add_alias
            # to avoid having to parse the command ourselves
            state.add_command(command)
        # Handle ```python and ```ipython by running "player" consoles
        elif shell_match:
            shell_name = shell_match.groups()[0].strip()
            py_commands = []
            more = True
            while more:  # slurp up all the python code
                try:
                    py_command = commands[i].rstrip()
                except IndexError:
                    raise SessionError('Unmatched {0} code block in '
                                       'session file.'.format(shell_name))
                i += 1
                if py_command.startswith('```'):
                    i += 1
                    more = False
                else:
                    py_commands.append(py_command)
            # Run the player console
            magictype(shell_name,
                      prompt_template=state['prompt_template'],
                      speed=state['speed'])
            if shell_name == 'ipython':
                try:
                    from doitlive.ipython_consoles import start_ipython_player
                except ImportError:
                    raise RuntimeError('```ipython blocks require IPython to be installed')
                # dedent all the commands to account for IPython's autoindentation
                ipy_commands = [textwrap.dedent(cmd) for cmd in py_commands]
                start_ipython_player(ipy_commands, speed=state['speed'])
            else:
                start_python_player(py_commands, speed=state['speed'])
        else:
            magicrun(command, **state)
    echo_prompt(state['prompt_template'])
    wait_for(RETURNS)
    if not quiet:
        secho("FINISHED SESSION", fg='yellow', bold=True)


# Les CLI
# #######

@click.version_option(__version__, '--version', '-v')
@click.group(cls=DYMGroup, context_settings={'help_option_names': ('-h', '--help')})
def cli():
    """doitlive: A tool for "live" presentations in the terminal

    \b
    Basic:
        1. Create a file called session.sh. Fill it with bash commands.
        2. Run "doitlive play session.sh".
        3. Type like a madman.

    Press Ctrl-C at any time to exit a session.
    To see a demo session, run "doitlive demo".

    You can use --help to get help with subcommands.

    Example: doitlive play --help
    """
    pass

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


@click.option('--preview', '-p', is_flag=True, default=False,
              help='Preview the available prompt themes.')
@click.option('--list', '-l', is_flag=True, default=False,
              help='List the available prompt themes.')
@cli.command()
def themes(preview, list):
    """Preview the available prompt themes."""
    if preview:
        preview_themes()
    else:
        list_themes()

@cli.command()
def completion():
    """Output completion (to be eval'd).

    For bash or zsh, add the following to your .bashrc or .zshrc:

        eval "$(doitlive completion)"

    For fish, add the following to ~/.config/fish/completions/doitlive.fish:

        eval (doitlive completion)
    """
    shell = env.get('SHELL', None)
    if env.get('SHELL', None):
        echo(
            click_completion.get_code(
                shell=shell.split(os.sep)[-1],
                prog_name='doitlive'
            )
        )
    else:
        echo(
            'Please ensure that the {SHELL} environment '
            'variable is set.'.format(SHELL=style('SHELL', bold=True))
        )
        sys.exit(1)


QUIET_OPTION = click.option('--quiet', '-q', help='Suppress startup and ending message.',
                            is_flag=True, default=False, show_default=False)

ECHO_OPTION = click.option('--commentecho', '-e',
                           help='Echo non-magic comments.', is_flag=True,
                           default=False, show_default=False)

SHELL_OPTION = click.option('--shell', '-S', metavar='<shell>',
                            default=get_default_shell, help=(
                                'The shell to use. '
                                '[default: $DOITLIVE_INTERPRETER or $SHELL or /bin/bash]'
                            ),
                            show_default=False)

SPEED_OPTION = click.option('--speed', '-s', metavar='<int>', type=click.IntRange(1),
                            default=1, help='Typing speed.', show_default=True)

PROMPT_OPTION = click.option('--prompt', '-p', metavar='<prompt_theme>',
                             default='default',
                             type=click.Choice(THEMES.keys()),
                             help='Prompt theme.',
                             show_default=True)

ALIAS_OPTION = click.option('--alias', '-a', metavar='<alias>',
                            multiple=True, help='Add a session alias.')

ENVVAR_OPTION = click.option('--envvar', '-e', metavar='<envvar>',
                             multiple=True, help='Adds a session variable.')


def _compose(*functions):
    def inner(func1, func2):
        return lambda x: func1(func2(x))

    return functools.reduce(inner, functions)


# Compose the decorators into "bundled" decorators
player_command = _compose(QUIET_OPTION, SHELL_OPTION, SPEED_OPTION,
                          PROMPT_OPTION, ECHO_OPTION)
recorder_command = _compose(SHELL_OPTION, PROMPT_OPTION, ALIAS_OPTION,
                            ENVVAR_OPTION)


@player_command
@click.argument('session_file', type=click.File('r', encoding='utf-8'))
@cli.command()
def play(quiet, session_file, shell, speed, prompt, commentecho):
    """Play a session file."""
    run(session_file.readlines(),
        shell=shell,
        speed=speed,
        quiet=quiet,
        test_mode=TESTING,
        prompt_template=prompt,
        commentecho=commentecho)


DEMO = [
    'echo "Greetings"',
    'echo "This is just a demo session"',
    'echo "For more info, check out the home page..."',
    'echo "http://doitlive.readthdocs.io"'
]


@player_command
@cli.command()
def demo(quiet, shell, speed, prompt, commentecho):
    """Run a demo doitlive session."""
    run(DEMO, shell=shell, speed=speed, test_mode=TESTING,
        prompt_template=prompt, quiet=quiet, commentecho=commentecho)


HEADER_TEMPLATE = """# Recorded with the doitlive recorder
#doitlive shell: {shell}
#doitlive prompt: {prompt}
"""

STOP_COMMAND = 'stop'
PREVIEW_COMMAND = 'P'
UNDO_COMMAND = 'U'
HELP_COMMANDS = ['H', 'help']


def echo_rec_buffer(commands):
    if commands:
        echo('Current commands in buffer:\n')
        for cmd in commands:
            echo('  ' + cmd, nl=False)  # commands already have newlines
    else:
        echo('No commands in buffer.')


def run_recorder(shell, prompt, aliases=None, envvars=None):
    commands = []
    prefix = '(' + style('REC', fg='red') + ') '
    while True:
        formatted_prompt = prefix + format_prompt(THEMES[prompt]) + ' '
        command = click.prompt(formatted_prompt, prompt_suffix='').strip()

        if command == STOP_COMMAND:
            break
        elif command == PREVIEW_COMMAND:
            echo_rec_buffer(commands)
        elif command == UNDO_COMMAND:
            if commands and click.confirm(
                    'Remove command? "{}"'.format(commands[-1].strip())):
                commands.pop()
                secho('Removed command.', bold=True)
                echo_rec_buffer(commands)
            else:
                echo('No commands in buffer. Doing nothing.')
        elif command == 'python':
            commands.append('```python\n')
            console = PythonRecorderConsole()
            console.interact()
            commands.extend(console.commands)
            commands.append('```\n\n')
        elif command in HELP_COMMANDS:
            print_recorder_instructions()
        else:
            commands.append(command + '\n\n')
            run_command(command, shell=shell,
                        aliases=aliases, envvars=envvars, test_mode=TESTING)
    return commands


def print_recorder_instructions():
    echo()
    echo('INSTRUCTIONS:')
    echo('Enter ' + style('{}'.format(STOP_COMMAND), bold=True) +
         ' when you are done recording.')
    echo('To preview the commands in the buffer, enter {}.'
         .format(style(PREVIEW_COMMAND, bold=True)))
    echo('To undo the last command in the buffer, enter {}.'
         .format(style(UNDO_COMMAND, bold=True)))
    echo('To view this help message again, enter {}.'
         .format(style(HELP_COMMANDS[0], bold=True)))
    echo()


@recorder_command
@click.argument('session_file', default='session.sh',
                type=click.Path(dir_okay=False, writable=True))
@cli.command()
def record(session_file, shell, prompt, alias, envvar):
    """Record a session file. If no argument is passed, commands are written to
    ./session.sh.

    When you are finished recording, run the "stop" command.
    """
    if os.path.exists(session_file):
        click.confirm(
            'File "{0}" already exists. Overwrite?'.format(session_file),
            abort=True, default=False)

    secho("We'll do it live!", fg='red', bold=True)
    filename = click.format_filename(session_file)
    secho('RECORDING SESSION: {}'.format(filename),
          fg='yellow', bold=True)

    print_recorder_instructions()

    click.pause()
    click.clear()
    cwd = os.getcwd()  # Save cwd

    # Run the recorder
    commands = run_recorder(shell, prompt, aliases=alias, envvars=envvar)

    os.chdir(cwd)  # Reset cwd

    secho("FINISHED RECORDING SESSION", fg='yellow', bold=True)
    secho('Writing to {0}...'.format(filename), fg='cyan')
    with open(session_file, 'w', encoding='utf-8') as fp:
        fp.write(HEADER_TEMPLATE.format(shell=shell, prompt=prompt))
        write_directives(fp, 'alias', alias)
        write_directives(fp, 'env', envvar)
        fp.write('\n')
        fp.write(''.join(commands))
        fp.write('\n')

    play_cmd = style('doitlive play {}'.format(filename), bold=True)
    echo('Done. Run {} to play back your session.'.format(play_cmd))


if __name__ == '__main__':
    cli()
