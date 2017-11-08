#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  doitlive
  ~~~~~~~~

  A tool for "live" presentations in the terminal.

  :copyright: (c) 2014-2017 by Steven Loria and contributors.
  :license: MIT, see LICENSE for more details.
"""

from code import InteractiveConsole
from collections import OrderedDict
from tempfile import NamedTemporaryFile
import datetime as dt
import functools
import getpass
import os
import re
import socket
import subprocess
import sys
import textwrap

from click import echo as click_echo
from click import style, secho, getchar
from click.termui import strip_ansi
import click

from doitlive.termutils import raw_mode
from doitlive.version_control import (
    get_current_git_branch,
    get_current_hg_bookmark,
    get_current_hg_branch,
    get_current_hg_id,
    get_current_vcs_branch
)

__version__ = '3.0.3'
__author__ = 'Steven Loria'
__license__ = 'MIT'

env = os.environ
PY2 = int(sys.version[0]) == 2
if not PY2:
    unicode = str
    basestring = (str, bytes)
else:
    from codecs import open  # pylint: disable=W0622

    open = open

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

ESC = '\x1b'
BACKSPACE = '\x7f'
CTRLC = '\x03'
RETURNS = {'\r', '\n'}
OPTION_RE = re.compile(r'^#\s?doitlive\s+'
                       r'(?P<option>prompt|shell|alias|env|speed'
                       r'|unalias|unset|commentecho):\s*(?P<arg>.+)$')

TESTING = False


class Style(object):
    """Descriptor that adds ANSI styling to a string when accessed."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        return TermString(style(instance, **self.kwargs))


class TermString(unicode):
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


# Some common symbols used in prompts
R_ANGLE = TermString(u'❯')
R_ANGLE_DOUBLE = TermString(u'»')
R_ARROW = TermString(u'➔')
DOLLAR = TermString(u'$')
PERCENT = TermString(u'%')
NEW_LINE = TermString(u'\n')


def _branch_to_term_string(branch_string):
    if strip_ansi(branch_string):
        return TermString(branch_string)
    else:
        # Prevent extra space when not in a VCS repo
        return TermString(u'\b')


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


def ensure_utf(string):
    return string.encode('utf-8') if PY2 else string


def write_commands(fp, command, args):
    if args:
        for arg in args:
            line = '{command} {arg}\n'.format(**locals())
            fp.write(ensure_utf(line))
    return None


def write_directives(fp, directive, args):
    if args:
        for arg in args:
            line = '#doitlive {directive}: {arg}\n'.format(**locals())
            fp.write(ensure_utf(line))
    return None


def get_default_shell():
    return env.get('DOITLIVE_INTERPRETER') or env.get('SHELL') or '/bin/bash'


def run_command(cmd, shell=None, aliases=None, envvars=None, test_mode=False):
    shell = shell or get_default_shell()
    if cmd.startswith("cd "):
        cwd = os.getcwd()  # Save cwd
        directory = cmd.split()[1].strip()
        if directory == '-':  # Go back to $OLDPWD
            directory = os.environ.get('OLDPWD', directory)
        try:
            os.chdir(os.path.expandvars(os.path.expanduser(directory)))
        except OSError:
            echo('No such file or directory: {}'.format(directory))
        else:
            os.environ['OLDPWD'] = cwd

    else:
        # Need to make a temporary command file so that $ENV are used correctly
        # and that shell built-ins, e.g. "source" work
        with NamedTemporaryFile('w') as fp:
            fp.write('#!{0}\n'.format(shell))
            fp.write('# -*- coding: utf-8 -*-\n')
            # Make aliases work in bash:
            if 'bash' in shell:
                fp.write('shopt -s expand_aliases\n')

            # Write envvars and aliases
            write_commands(fp, 'export', envvars)
            write_commands(fp, 'alias', aliases)

            cmd_line = cmd + '\n'
            fp.write(ensure_utf(cmd_line))
            fp.flush()
            if test_mode:
                output = subprocess.check_output([shell, fp.name])
                echo(output)
            else:
                return subprocess.call([shell, fp.name])


def wait_for(chars):
    while True:
        in_char = getchar()
        if in_char in {ESC, CTRLC}:
            echo(carriage_return=True)
            raise click.Abort()
        if in_char in chars:
            echo()
            return in_char


def magictype(text, prompt_template='default', speed=1):
    echo_prompt(prompt_template)
    cursor_position = 0
    with raw_mode():
        while True:
            char = text[cursor_position:cursor_position + speed]
            in_char = getchar()
            if in_char in {ESC, CTRLC}:
                echo(carriage_return=True)
                raise click.Abort()
            elif in_char == BACKSPACE:
                if cursor_position > 0:
                    echo("\b \b", nl=False)
                    cursor_position -= 1
            elif in_char in RETURNS:
                # Only return at end of command
                if cursor_position >= len(text):
                    echo("\r", nl=True)
                    break
            else:
                if cursor_position < len(text):
                    echo(char, nl=False)
                    increment = min([speed, len(text) - cursor_position])
                    cursor_position += increment


def magicrun(text, shell, prompt_template='default', aliases=None,
             envvars=None, speed=1, test_mode=False, commentecho=False):
    magictype(text, prompt_template, speed)
    run_command(text, shell, aliases=aliases, envvars=envvars,
                test_mode=test_mode)


def format_prompt(prompt):
    try:
        return prompt.format(**get_prompt_state())
    except KeyError:
        raise ConfigurationError('Invalid variable in prompt template.')


def make_prompt_formatter(template):
    tpl = THEMES.get(template) or template
    return lambda: format_prompt(tpl)


def echo_prompt(template):
    prompt = make_prompt_formatter(template)()
    echo(prompt + ' ', nl=False)


# Exceptions
# ##########


class DoItLiveError(Exception):
    """Base exception class for all doitlive-related errors."""
    pass


class ConfigurationError(DoItLiveError):
    pass


class SessionError(DoItLiveError):
    pass


# Custom Python consoles
# ######################

class PythonPlayerConsole(InteractiveConsole):
    """A magic python console."""

    def __init__(self, commands=None, speed=1, *args, **kwargs):
        self.commands = commands or []
        self.speed = speed
        InteractiveConsole.__init__(self, *args, **kwargs)

    def run_commands(self):
        """Automatically type and execute all commands."""
        more = 0
        prompt = sys.ps1
        for command in self.commands:
            try:
                prompt = sys.ps2 if more else sys.ps1
                try:
                    magictype(command, prompt_template=prompt, speed=self.speed)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    if command.strip() == 'exit()':
                        return
                    more = self.push(command)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0
                sys.exit(1)
        echo_prompt(prompt)
        wait_for(RETURNS)

    def interact(self, banner=None):
        """Run an interactive session."""
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>>'
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = ('Type "help", "copyright", "credits" or "license" for '
                'more information.')
        if banner is None:
            self.write("Python %s on %s\n%s\n" %
                       (sys.version, sys.platform, cprt))
        else:
            self.write("%s\n" % str(banner))
        self.run_commands()


def start_python_player(commands, speed=1):
    PythonPlayerConsole(commands=commands, speed=speed).interact()


class PythonRecorderConsole(InteractiveConsole):
    """An interactive Python console that stores user input in a list."""

    def __init__(self, *args, **kwargs):
        self.commands = []
        InteractiveConsole.__init__(self, *args, **kwargs)

    def raw_input(self, *args, **kwargs):
        ret = InteractiveConsole.raw_input(self, *args, **kwargs)
        self.commands.append(ret + '\n')
        if ret.strip() == 'exit()':
            raise EOFError()
        return ret


class SessionState(dict):
    """Stores information about a fake terminal session."""
    TRUTHY = set(['true', 'yes', '1'])

    def __init__(self, shell, prompt_template, speed,
                 aliases=None, envvars=None,
                 test_mode=False, commentecho=False):
        aliases = aliases or []
        envvars = envvars or []
        dict.__init__(self, shell=shell, prompt_template=prompt_template,
                      speed=speed, aliases=aliases, envvars=envvars,
                      test_mode=test_mode, commentecho=commentecho)

    def add_alias(self, alias):
        self['aliases'].append(alias)

    def add_envvar(self, envvar):
        self['envvars'].append(envvar)

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
                    from doitlive.ipython import start_ipython_player
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
@click.group(context_settings={'help_option_names': ('-h', '--help')})
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


QUIET_OPTION = click.option('--quiet', '-q', help='Suppress startup and ending message.',
                            is_flag=True, default=False, show_default=False)

ECHO_OPTION = click.option('--commentecho', '-e',
                           help='Echo non-magic comments.', is_flag=True,
                           default=False, show_default=False)

SHELL_OPTION = click.option('--shell', '-S', metavar='<shell>',
                            default=get_default_shell, help='The shell to use.',
                            show_default=True)

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
