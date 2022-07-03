from __future__ import unicode_literals

import os
import click
import pytest
from prompt_toolkit.key_binding import KeyPress
from prompt_toolkit.keys import Keys

from doitlive.ipython.app import DoitliveTerminalInteractiveShell


@pytest.mark.skipif(
    # FIXME
    "CI" in os.environ,
    reason="IPython shell does not work in Azure Pipelines",
)
class TestPlayerTerminalInteractiveShell:
    @pytest.fixture()
    def make_shell(self):
        def func(commands, speed=1):
            shell = DoitliveTerminalInteractiveShell(commands=commands, speed=speed)
            shell.init_prompt_toolkit_cli()
            return shell

        return func

    @pytest.fixture()
    def shell(self, make_shell):
        return make_shell(commands=["import math", "1 + 1"])

    def test_current_command(self, shell):
        assert shell.current_command() == "import math"
        shell.current_command_index += 1
        assert shell.current_command() == "1 + 1"

    def test_current_command_key(self, shell):
        assert shell.current_command_keys() == "i"
        shell.current_command_pos += 1
        assert shell.current_command_keys() == "m"

    def test_on_feed_key(self, shell):
        assert shell.current_command_keys() == "i"
        key_press = KeyPress("x")
        shell.next_keys([key_press])
        assert shell.current_command_keys() == "m"

    def test_on_feed_key_goes_to_next_command_after_enter(self, shell):
        assert shell.current_command_keys() == "i"
        for _ in range(len("import math")):
            shell.next_keys([KeyPress("x")])
        shell.next_keys([KeyPress(Keys.Enter)])
        assert shell.current_command() == "1 + 1"

    def test_assert_on_feed_key_with_speed(self, make_shell):
        shell = make_shell(commands=["import math", "1 + 1"], speed=2)
        assert shell.current_command_keys() == "im"
        shell.next_keys([KeyPress("x")])
        assert shell.current_command_keys() == "po"

    def test_on_feed_key_escape_aborts(self, shell):
        with pytest.raises(click.Abort):
            shell.next_keys([KeyPress(Keys.Escape)])

    def test_on_feed_key_ctrlc_aborts(self, shell):
        with pytest.raises(click.Abort):
            shell.next_keys([KeyPress(Keys.ControlC)])

    def test_on_feed_key_backspace(self, shell):
        shell.next_keys([KeyPress("x")])
        assert shell.current_command_keys() == "m"
        shell.next_keys([KeyPress(Keys.Backspace)])
        assert shell.current_command_keys() == "i"
        shell.next_keys([KeyPress(Keys.Backspace)])
        assert shell.current_command_keys() == "i"

    def test_on_feed_key_backspace_with_speed(self, make_shell):
        shell = make_shell(commands=["1+1"], speed=2)
        shell.next_keys([KeyPress("x")])
        assert shell.current_command_keys() == "1"
        shell.next_keys([KeyPress(Keys.Backspace)])
        assert shell.current_command_keys() == "+1"

    def test_on_feed_key_does_not_increment_pos_past_length_of_command(
        self, make_shell
    ):
        shell = make_shell(commands=["abcde"], speed=2)
        shell.next_keys([KeyPress("x"), KeyPress("x")])
        assert shell.current_command_pos == len("abcde") - 1
        shell.next_keys([KeyPress("x")])
        assert shell.current_command_pos == len("abcde")
        shell.next_keys([KeyPress("x")])
        assert shell.current_command_pos == len("abcde")
