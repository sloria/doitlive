# -*- coding: utf-8 -*-
"""doitlive IPython support."""
from __future__ import absolute_import, print_function

from warnings import warn

from click import Abort
from IPython.terminal.interactiveshell import (DISPLAY_BANNER_DEPRECATED,
                                               TerminalInteractiveShell)
from IPython.terminal.ipapp import TerminalIPythonApp
from prompt_toolkit.interface import (CommandLineInterface,
                                      _InterfaceEventLoopCallbacks)
from prompt_toolkit.key_binding.input_processor import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import create_output

from doitlive import RETURNS, wait_for, echo

class _PlayerInterfaceEventLoopCallbacks(_InterfaceEventLoopCallbacks):
    def __init__(self, cli, on_feed_key):
        super(_PlayerInterfaceEventLoopCallbacks, self).__init__(cli)
        self.on_feed_key = on_feed_key

    # Override _InterfaceEventLoopCallbacks
    def feed_key(self, key_press, *args, **kwargs):
        key_press = self.on_feed_key(key_press)
        if key_press is not None:
            return super(_PlayerInterfaceEventLoopCallbacks, self).feed_key(key_press,
                                                                           *args, **kwargs)


class _PlayerCommandLineInterface(CommandLineInterface):
    def __init__(self, application, eventloop=None, input=None, output=None,
                 on_feed_key=None):
        super(_PlayerCommandLineInterface, self).__init__(application, eventloop, input, output)
        self.on_feed_key = on_feed_key

    # Overrride CommandLineInterface
    def create_eventloop_callbacks(self):
        return _PlayerInterfaceEventLoopCallbacks(self, on_feed_key=self.on_feed_key)


class PlayerTerminalInteractiveShell(TerminalInteractiveShell):
    """A magic IPython terminal shell."""
    def __init__(self, commands, speed=1, *args, **kwargs):
        self.commands = commands or []
        self.speed = speed
        # Index of current command
        self.current_command_index = 0
        # Index of current character in current command
        self.current_command_pos = 0
        super(PlayerTerminalInteractiveShell, self).__init__(*args, **kwargs)

    def on_feed_key(self, key_press):
        """Handles the magictyping when a key is pressed"""
        if key_press.key in {Keys.Escape, Keys.ControlC}:
            echo(carriage_return=True)
            raise Abort()
        if key_press.key == Keys.Backspace:
            if self.current_command_pos > 0:
                self.current_command_pos -= 1
            return key_press
        ret = None
        if key_press.key != Keys.CPRResponse:
            if self.current_command_pos < len(self.current_command):
                current_key = self.current_command_key
                ret = KeyPress(current_key)
                increment = min([self.speed, len(self.current_command) - self.current_command_pos])
                self.current_command_pos += increment
            else:
                # Command is finished, wait for Enter
                if key_press.key != Keys.Enter:
                    return None
                self.current_command_index += 1
                self.current_command_pos = 0
                ret = key_press
        return ret

    @property
    def current_command(self):
        return self.commands[self.current_command_index]

    @property
    def current_command_key(self):
        pos = self.current_command_pos
        end = min(pos + self.speed, len(self.current_command))
        return self.current_command[pos:end]

    # Overrride TerminalInteractiveShell
    # Much of this is copy-and-pasted from the parent class implementation
    # due to lack of hooks
    def interact(self, display_banner=DISPLAY_BANNER_DEPRECATED):

        if display_banner is not DISPLAY_BANNER_DEPRECATED:
            warn('interact `display_banner` argument is deprecated since IPython 5.0. Call `show_banner()` if needed.', DeprecationWarning, stacklevel=2)  # noqa

        self.keep_running = True
        while self.keep_running:
            print(self.separate_in, end='')

            if self.current_command_index > len(self.commands) - 1:
                echo('Do you really want to exit ([y]/n)? ', nl=False)
                wait_for(RETURNS)
                self.ask_exit()
                return None

            try:
                code = self.prompt_for_code()
            except EOFError:
                if (not self.confirm_exit) \
                        or self.ask_yes_no('Do you really want to exit ([y]/n)?', 'y', 'n'):
                    self.ask_exit()

            else:
                if code:
                    self.run_cell(code, store_history=True)

    # Overrride TerminalInteractiveShell
    def init_prompt_toolkit_cli(self):
        super(PlayerTerminalInteractiveShell, self).init_prompt_toolkit_cli()
        # override CommandLineInterface
        self.pt_cli = _PlayerCommandLineInterface(
            self._pt_app, eventloop=self._eventloop,
            output=create_output(true_color=self.true_color),
            on_feed_key=self.on_feed_key,
        )

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
