# -*- coding: utf-8 -*-
"""doitlive IPython support."""
from __future__ import absolute_import

from IPython.utils import py3compat
from IPython.utils.warn import warn
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.utils.text import num_ini_spaces


from doitlive import magictype, wait_for, RETURNS
from click import echo


class PlayerTerminalInteractiveShell(TerminalInteractiveShell):
    """A magic Ipython terminal shell."""
    def __init__(self, commands, speed, *args, **kwargs):
        self.commands = commands
        self.current_command = 0  # Index of current command
        self.speed = speed
        super(PlayerTerminalInteractiveShell, self).__init__(*args, **kwargs)

    # Override raw_input to do magic-typing
    # NOTE: Much of this is copy-and-pasted from the parent class's implementation
    # due to lack of hooks
    def raw_input(self, prompt=''):
        if self.current_command > len(self.commands) - 1:
            echo('Do you really want to exit ([y]/n)? ', nl=False)
            wait_for(RETURNS)
            self.ask_exit()
            return ''
        # raw_input expects str, but we pass it unicode sometimes
        prompt = py3compat.cast_bytes_py2(prompt)

        try:
            command = self.commands[self.current_command]
            magictype(command, prompt_template=prompt, speed=self.speed)
            line = py3compat.cast_unicode_py2(command)
        except ValueError:
            warn("\n********\nYou or a %run:ed script called sys.stdin.close()"
                 " or sys.stdout.close()!\nExiting IPython!\n")
            self.ask_exit()
            return ""

        # Try to be reasonably smart about not re-indenting pasted input more
        # than necessary.  We do this by trimming out the auto-indent initial
        # spaces, if the user's actual input started itself with whitespace.
        if self.autoindent:
            if num_ini_spaces(line) > self.indent_current_nsp:
                line = line[self.indent_current_nsp:]
                self.indent_current_nsp = 0

        self.current_command += 1
        return line

class PlayerTerminalIPythonApp(TerminalIPythonApp):
    """IPython app that runs the PlayerTerminalInteractiveShell."""
    commands = tuple()
    speed = 1

    # Ignore command line args, since this will be run from the doitlive CLI
    def parse_command_line(self, argv=None):
        return None

    def init_shell(self):
        """initialize the InteractiveShell instance"""
        self.shell = PlayerTerminalInteractiveShell.instance(
            commands=self.commands, speed=self.speed,
            parent=self, display_banner=False, profile_dir=self.profile_dir,
            ipython_dir=self.ipython_dir, user_ns=self.user_ns
        )
        self.shell.configurables.append(self)

def start_ipython_player(commands, speed=1):
    """Starts a new magic IPython shell."""
    PlayerTerminalIPythonApp.commands = commands
    PlayerTerminalIPythonApp.speed = speed
    PlayerTerminalIPythonApp.launch_instance()
