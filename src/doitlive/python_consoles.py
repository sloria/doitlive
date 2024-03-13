"""InteractiveConsole subclasses for recording and playback
of canned Python statements.
"""

import sys
from code import InteractiveConsole

from doitlive.keyboard import RETURNS, magictype, wait_for
from doitlive.styling import echo_prompt


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
                    if command.strip() == "exit()":
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
            sys.ps1  # noqa: B018
        except AttributeError:
            sys.ps1 = ">>>"
        try:
            sys.ps2  # noqa: B018
        except AttributeError:
            sys.ps2 = "... "
        cprt = (
            'Type "help", "copyright", "credits" or "license" for ' "more information."
        )
        if banner is None:
            self.write(f"Python {sys.version} on {sys.platform}\n{cprt}\n")
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
        self.commands.append(ret + "\n")
        if ret.strip() == "exit()":
            raise EOFError()
        return ret
