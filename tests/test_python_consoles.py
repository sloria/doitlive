import pytest

import doitlive


class TestPlayerConsole:
    @pytest.fixture
    def console(self):
        return doitlive.PythonPlayerConsole()

    @pytest.mark.parametrize(
        "command,expected",
        [
            ("1 + 1", b"2"),
            ('print("f" + "o" + "o")', b"foo"),
            ("import math; math.sqrt(144)", b"12"),
        ],
    )
    def test_interact(self, runner, console, command, expected):
        console.commands = [command]
        with runner.isolation(input="{}\n\n".format(command)) as (stdout, stderr):
            console.interact()
        assert expected in stdout.getvalue()


class TestRecorderConsole:
    def test_interact_stores_commands(self, runner):
        cons = doitlive.PythonRecorderConsole()
        commands = ['print("foo")', "import math"]
        with runner.isolation(input="\n".join(commands)):
            cons.interact()
        for command in commands:
            assert (command + "\n") in cons.commands
