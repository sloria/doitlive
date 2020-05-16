from __future__ import unicode_literals

import os
import click
import pytest
from prompt_toolkit.key_binding.input_processor import KeyPress
from prompt_toolkit.keys import Keys

from doitlive.ipython_consoles import PlayerTerminalInteractiveShell


@pytest.mark.skipif(
    # FIXME
    "CI" in os.environ,
    reason="IPython shell does not work in Azure Pipelines",
)
class TestPlayerTerminalInteractiveShell:
    @pytest.fixture()
    def make_shell(self):
        def func(commands, speed=1):
            shell = PlayerTerminalInteractiveShell(commands=commands, speed=speed)
            shell.init_prompt_toolkit_cli()
            return shell

        return func

    @pytest.fixture()
    def shell(self, make_shell):
        return make_shell(commands=["import math", "1 + 1"])

    def test_current_command(self, shell):
        assert shell.current_command == "import math"
        shell.current_command_index += 1
        assert shell.current_command == "1 + 1"

    def test_current_command_key(self, shell):
        assert shell.current_command_key == "i"
        shell.current_command_pos += 1
        assert shell.current_command_key == "m"

    def test_on_feed_key(self, shell):
        assert shell.current_command_key == "i"
        key_press = KeyPress("x")
        shell.on_feed_key(key_press)
        assert shell.current_command_key == "m"

    def test_on_feed_key_goes_to_next_command_after_enter(self, shell):
        assert shell.current_command_key == "i"
        for _ in range(len("import math")):
            shell.on_feed_key(KeyPress("x"))
        shell.on_feed_key(KeyPress(Keys.Enter))
        assert shell.current_command == "1 + 1"

    def test_assert_on_feed_key_with_speed(self, make_shell):
        shell = make_shell(commands=["import math", "1 + 1"], speed=2)
        assert shell.current_command_key == "im"
        shell.on_feed_key(KeyPress("x"))
        assert shell.current_command_key == "po"

    def test_on_feed_key_escape_aborts(self, shell):
        with pytest.raises(click.Abort):
            shell.on_feed_key(KeyPress(Keys.Escape))

    def test_on_feed_key_ctrlc_aborts(self, shell):
        with pytest.raises(click.Abort):
            shell.on_feed_key(KeyPress(Keys.ControlC))

    def test_on_feed_key_backspace(self, shell):
        shell.on_feed_key(KeyPress("x"))
        assert shell.current_command_key == "m"
        shell.on_feed_key(KeyPress(Keys.Backspace))
        assert shell.current_command_key == "i"
        shell.on_feed_key(KeyPress(Keys.Backspace))
        assert shell.current_command_key == "i"

    def test_on_feed_key_backspace_with_speed(self, make_shell):
        shell = make_shell(commands=["1+1"], speed=2)
        shell.on_feed_key(KeyPress("x"))
        assert shell.current_command_key == "1"
        shell.on_feed_key(KeyPress(Keys.Backspace))
        assert shell.current_command_key == "+1"

    def test_on_feed_key_does_not_increment_pos_past_length_of_command(
        self, make_shell
    ):
        shell = make_shell(commands=["1+1"], speed=2)
        shell.on_feed_key(KeyPress("xx"))
        assert shell.current_command_pos == len("1+1") - 1
        shell.on_feed_key(KeyPress("x"))
        assert shell.current_command_pos == len("1+1")
        shell.on_feed_key(KeyPress("x"))
        assert shell.current_command_pos == len("1+1")
