# -*- coding: utf-8 -*-
"""doitlive IPython support."""
from __future__ import absolute_import, print_function

import itertools as it

from click import Abort
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.ipapp import TerminalIPythonApp

from prompt_toolkit.key_binding import KeyPress
from prompt_toolkit.keys import Keys

from doitlive import RETURNS, wait_for, echo


class DoitliveKeyProcessor:
    def __init__(self, wrapped_processor, next_keys):
        self.__wrapped = wrapped_processor
        self.__next_keys = next_keys

    def feed(self, key_press, first=False) -> None:
        self.feed_multiple([key_press], first=first)

    def feed_multiple(self, key_presses, first=False) -> None:
        key_presses = self.__next_keys(key_presses)

        if first:
            self.__wrapped.input_queue.extendleft(reversed(key_presses))
        else:
            self.__wrapped.input_queue.extend(key_presses)

    def __getattr__(self, item):
        return getattr(self.__wrapped, item)


class DoitliveTerminalInteractiveShell(TerminalInteractiveShell):
    """A magic IPython terminal shell."""

    def __init__(self, commands, speed=1, *args, **kwargs):
        self.commands = commands or []
        self.speed = speed

        # Index of current command
        self.current_command_index = 0
        # Index of current character in current command
        self.current_command_pos = 0

        super(DoitliveTerminalInteractiveShell, self).__init__(*args, **kwargs)

    def next_keys(self, key_presses):
        return list(
            it.chain.from_iterable(
                [self._next_keys(key_press) for key_press in key_presses]
            )
        )

    def _next_keys(self, key_press):
        """Handles the magic typing when a key is pressed"""

        if key_press.key in {Keys.Escape, Keys.ControlC}:
            echo(carriage_return=True)
            raise Abort()

        if key_press.key == Keys.Backspace:
            self.current_command_pos = max(0, self.current_command_pos - 1)
            return [key_press]

        if key_press.key == Keys.CPRResponse:
            return []

        if self.current_command_pos < len(self.current_command()):
            current_keys = self.current_command_keys()
            self.advance()
            return [KeyPress(k) for k in current_keys]

        # Command is finished, wait for Enter
        if key_press.key != Keys.Enter:
            return []

        self.current_command_index += 1
        self.current_command_pos = 0
        return [key_press]

    def current_command(self):
        return self.commands[self.current_command_index]

    def current_command_keys(self):
        current_command = self.current_command()
        end = min(self.current_command_pos + self.speed, len(current_command))
        return current_command[self.current_command_pos : end]

    def advance(self):
        self.current_command_pos += min(
            [self.speed, len(self.current_command()) - self.current_command_pos]
        )

    # Override TerminalInteractiveShell
    # Much of this is copy-and-pasted from the parent class implementation
    # due to lack of hooks
    def interact(self):
        self.keep_running = True
        while self.keep_running:
            print(self.separate_in, end="")

            if self.current_command_index > len(self.commands) - 1:
                echo("Do you really want to exit ([y]/n)? ", nl=False)
                wait_for(RETURNS)
                self.ask_exit()
                return None

            try:
                code = self.prompt_for_code()
            except EOFError:
                if (not self.confirm_exit) or self.ask_yes_no(
                    "Do you really want to exit ([y]/n)?", "y", "n"
                ):
                    self.ask_exit()

            else:
                if code:
                    self.run_cell(code, store_history=True)

    # Override TerminalInteractiveShell
    def init_prompt_toolkit_cli(self):
        super(DoitliveTerminalInteractiveShell, self).init_prompt_toolkit_cli()
        self.pt_app.app.key_processor = DoitliveKeyProcessor(
            wrapped_processor=self.pt_app.app.key_processor, next_keys=self.next_keys
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
        self.shell = DoitliveTerminalInteractiveShell.instance(
            commands=self.commands,
            speed=self.speed,
            parent=self,
            display_banner=False,
            profile_dir=self.profile_dir,
            ipython_dir=self.ipython_dir,
            user_ns=self.user_ns,
        )
        self.shell.configurables.append(self)
