# -*- coding: utf-8 -*-
import os
import random
import getpass
from contextlib import contextmanager
import subprocess

import pytest

import doitlive
from doitlive.cli import cli
from doitlive.__version__ import __version__


# Check if git is installed
git_available = None
if subprocess.call(["which", "git"]) == 0:
    git_available = True
else:
    git_available = False

random.seed(42)
HERE = os.path.abspath(os.path.dirname(__file__))


def random_string(n, alphabet="abcdefghijklmnopqrstuvwxyz1234567890;'\\][=-+_`"):
    return "".join([random.choice(alphabet) for _ in range(n)])


def run_session(runner, filename, user_input, args=None):
    args = args or []
    session = os.path.join(HERE, "sessions", filename)
    # Press ENTER at beginning of session and ENTER twice at end
    user_in = "".join(["\n", user_input, "\n\n"])
    return runner.invoke(cli, ["play", session] + args, input=user_in)


class TestPlayer:
    def test_basic_session(self, runner):
        user_input = random_string(len('echo "Hello"'))
        result = run_session(runner, "basic.session", user_input)

        assert result.exit_code == 0
        assert 'echo "Hello"' in result.output

    def test_session_with_unicode(self, runner):
        user_input = random_string(len(u'echo "H´l¬ø ∑ø®ld"'))
        result = run_session(runner, "unicode.session", user_input)
        assert result.exit_code == 0

    def test_session_with_envvar(self, runner):
        user_input = random_string(len("echo $HOME"))

        result = run_session(runner, "env.session", user_input)
        assert result.exit_code == 0
        assert os.environ["HOME"] in result.output

    def test_session_with_comment(self, runner):
        user_input = random_string(len("echo foo"))
        result = run_session(runner, "comment.session", user_input)
        assert result.exit_code == 0
        assert "foo" not in result.output, "comment was not skipped"
        assert "bar" in result.output

    def test_commentecho_option(self, runner):
        user_input = random_string(len("echo foo"))
        result = run_session(
            runner, "comment.session", user_input, args=["--commentecho"]
        )
        assert result.exit_code == 0
        assert "foo" in result.output, "comment was not echoed"
        assert "bar" in result.output

    def test_commentecho_magic_comment(self, runner):
        user_input = random_string(len("echo"))
        result = run_session(runner, "commentecho.session", user_input)
        assert result.exit_code == 0
        assert "foo" not in result.output
        assert "bar'" in result.output
        assert "baz" not in result.output

    def test_esc_key_aborts(self, runner):
        result = run_session(runner, "basic.session", "echo" + doitlive.ESC)
        assert result.exit_code > 0

    def test_pwd(self, runner):
        user_input = random_string(3)
        result = run_session(runner, "pwd.session", user_input)
        assert os.getcwd() in result.output

    def test_custom_prompt(self, runner):
        user_input = random_string(len("echo"))
        result = run_session(runner, "prompt.session", user_input)
        assert getpass.getuser() in result.output

    def test_custom_var(self, runner):
        user_input = random_string(len("echo $MEANING"))
        result = run_session(runner, "envvar.session", user_input)
        assert "fortytwo" in result.output

    def test_custom_speed(self, runner):
        user_input = random_string(3)
        result = run_session(runner, "speed.session", user_input)
        assert "123456789" in result.output

    def test_bad_theme(self, runner):
        result = runner.invoke(cli, ["-p", "thisisnotatheme"])
        assert result.exit_code > 0

    def test_bad_speed(self, runner):
        result = runner.invoke(cli, ["demo", "-s", "-1"])
        assert result.exit_code > 0

    def test_cd(self, runner):
        user_input = (
            random_string(len("cd ~")) + "\n" + random_string(len("pwd")) + "\n"
        )
        result = run_session(runner, "cd.session", user_input)

        assert result.exit_code == 0
        assert os.environ["HOME"] in result.output

    def test_cd_bad(self, runner):
        user_input = (
            random_string(len("cd /thisisnotadirectory"))
            + "\n"
            + random_string(len("pwd"))
            + "\n"
        )
        result = run_session(runner, "cd_bad.session", user_input)

        assert result.exit_code == 0

    def test_python_session(self, runner):
        user_input = '\npython\nprint("f" + "o" + "o")\n'
        result = run_session(runner, "python.session", user_input)
        assert result.exit_code == 0
        assert "foo" in result.output

    def test_alias(self, runner):
        user_input = random_string(len("foo"))
        result = run_session(runner, "alias_comment.session", user_input)
        assert result.exit_code == 0
        assert "42" in result.output

    def test_unalias(self, runner):
        user_input = random_string(len("foo"))
        result = run_session(runner, "unalias.session", user_input)
        # nonzero exit code becuase 'foo' is no longer aliased
        assert result.exit_code != 0
        assert "foobarbazquux" not in result.output

    def test_unset_envvar(self, runner):
        user_input = random_string(len("echo $MEANING"))
        result = run_session(runner, "unset.session", user_input)
        assert "fortytwo" not in result.output

    def test_export_sets_envvar(self, runner):
        user_input = "".join(
            [
                random_string(len("export NAME=Steve")),
                "\n",
                random_string(len("echo 'Hello' $NAME")),
            ]
        )
        result = run_session(runner, "export.session", user_input)
        assert "Hello Steve" in result.output

    def test_alias_sets_alias(self, runner):
        user_input = "".join(
            [
                random_string(len('alias foo="echo $((41+1))"')),
                "\n",
                random_string(len("foo")),
            ]
        )
        result = run_session(runner, "alias.session", user_input)
        assert "42" in result.output


def test_themes_list(runner):
    result1 = runner.invoke(cli, ["themes"])
    assert result1.exit_code == 0
    result2 = runner.invoke(cli, ["themes", "--list"])
    result3 = runner.invoke(cli, ["themes", "-l"])
    assert result1.output == result2.output == result3.output


def test_themes_preview(runner):
    result1 = runner.invoke(cli, ["themes", "--preview"])
    assert result1.exit_code == 0
    result2 = runner.invoke(cli, ["themes", "-p"])
    assert result2.exit_code == 0
    assert result1.output == result2.output


def test_completion(runner, monkeypatch):
    monkeypatch.setitem(os.environ, "SHELL", "/usr/local/bin/zsh")
    result = runner.invoke(cli, ["completion"])
    assert result.exit_code == 0


def test_completion_fails_if_SHELL_is_unset(runner, monkeypatch):
    if "SHELL" in os.environ:
        monkeypatch.delitem(os.environ, "SHELL")
    result = runner.invoke(cli, ["completion"])
    assert result.exit_code > 0
    msg = "Please ensure that the SHELL environment variable is set."
    assert msg in result.output


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert __version__ in result.output
    result2 = runner.invoke(cli, ["-v"])
    assert result.output == result2.output


def test_bad_format_prompt():
    with pytest.raises(doitlive.ConfigurationError):
        doitlive.format_prompt("{notfound}")


def test_did_you_mean(runner):
    result = runner.invoke(cli, ["the"])
    assert result.exit_code > 0
    assert "Did you mean" in result.output
    assert "themes" in result.output


@pytest.mark.skipif(not git_available, reason="Git is not available")
def test_get_git_branch(runner):
    with runner.isolated_filesystem():
        with open("junk.txt", "w") as fp:
            fp.write("doin it live")
        subprocess.call(["git", "init"])
        subprocess.call(["git", "add", "."])
        subprocess.call(["git", "commit", "-c", '"initial commit"'])
        branch = doitlive.get_current_git_branch()
        assert branch == "master"


class TestSessionState:
    @pytest.fixture
    def state(self):
        return doitlive.SessionState(
            shell="/bin/zsh", prompt_template="default", speed=1
        )

    def test_remove_alias(self, state):
        state.add_alias("g=git")
        assert "g=git" in state["aliases"]  # sanity check
        state.remove_alias("g")
        assert "g=git" not in state["aliases"]

    def test_remove_envvar(self, state):
        state.add_envvar("EDITOR=vim")
        assert "EDITOR=vim" in state["envvars"]
        state.remove_envvar("EDITOR")
        assert "EDITOR=vim" not in state["envvars"]

    def test_add_alias(self):
        state = doitlive.SessionState("/bin/zsh", "default", speed=1)
        assert len(state["aliases"]) == 0
        state.add_alias("g=git")
        assert "g=git" in state["aliases"]


@contextmanager
def recording_session(runner, commands=None, args=None):
    commands = commands or ['echo "foo"']
    args = args or []

    with runner.isolated_filesystem():
        user_input = recorder_input(commands)
        result = runner.invoke(cli, ["record"] + args, input=user_input)
        yield result


def recorder_input(commands):
    command_input = "\n".join(commands)
    user_input = "".join(["\n", command_input, "\nstop\n"])
    return user_input


class TestRecorder:
    def test_record_creates_session_file(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["record"], input='\necho "Hello"\nstop\n')
            assert result.exit_code == 0, result.output
            assert os.path.exists("session.sh")

    def test_custom_output_file(self, runner):
        with recording_session(runner, args=["mysession.sh"]):
            assert os.path.exists("mysession.sh")

    def test_record_content(self, runner):
        commands = ['echo "foo"', 'echo "bar"']
        with recording_session(runner, commands), open("session.sh") as fp:
            content = fp.read()
            assert 'echo "foo"\n' in content
            assert 'echo "bar"' in content

    def test_header_content(self, runner):
        with recording_session(runner, args=["--shell", "/bin/bash"]), open(
            "session.sh"
        ) as fp:
            content = fp.read()
            assert "#doitlive shell: /bin/bash" in content

    def test_custom_prompt(self, runner):
        with recording_session(runner, args=["-p", "sorin"]), open("session.sh") as fp:
            content = fp.read()
            assert "#doitlive prompt: sorin" in content

    def test_prompt_if_file_already_exists(self, runner):
        with runner.isolated_filesystem():
            # session.sh file already exists
            with open("session.sh", "w") as fp:
                fp.write("foo")
            # runs "record" and enters "n" at the prompt
            result = runner.invoke(cli, ["record"], input="n\n")
            assert result.exit_code == 1
            assert "Overwrite?" in result.output

    def test_cding(self, runner):
        with runner.isolated_filesystem():
            initial_dir = os.getcwd()
            cd_to = os.path.join(initial_dir, "mydir")
            os.mkdir(cd_to)
            user_input = recorder_input(["cd mydir", "pwd"])
            result = runner.invoke(cli, ["record"], input=user_input)
            assert result.exit_code == 0
            # cwd was reset
            assert os.getcwd() == initial_dir
            assert cd_to in result.output

    def test_session_file_cannot_be_a_directory(self, runner):
        with runner.isolated_filesystem():
            os.mkdir("mydir")
            result = runner.invoke(cli, ["record", "mydir"])
            assert result.exit_code > 0

    def test_preview_buffer(self, runner):
        with recording_session(runner, commands=["echo foo", "P"]) as result:
            assert "Current commands in buffer:\n\n  echo foo" in result.output

    def test_preview_buffer_empty(self, runner):
        with recording_session(runner, commands=["P"]) as result:
            assert "No commands in buffer." in result.output

    def test_undo_command(self, runner):
        with recording_session(runner, ["echo foo", "echo bar", "U\ny"]):
            with open("session.sh", "r") as fp:
                content = fp.read()
                assert "echo bar" not in content
                assert "echo foo" in content

    def test_aliases(self, runner):
        with recording_session(
            runner, ["e"], args=["--alias", 'e="echo foo"']
        ) as result:
            assert "foo" in result.output

    def test_aliases_are_written(self, runner):
        with recording_session(runner, args=["-a", "g=git", "-a", "c=clear"]):
            with open("session.sh", "r") as fp:
                content = fp.read()
                assert "#doitlive alias: g=git\n" in content
                assert "#doitlive alias: c=clear\n" in content

    def test_envvar(self, runner):
        with recording_session(runner, ["echo $NAME"], ["-e", "NAME=Steve"]) as result:
            assert "Steve" in result.output

    def test_envvars_are_written(self, runner):
        with recording_session(runner, args=["-e", "FIRST=Steve", "-e", "LAST=Loria"]):
            with open("session.sh", "r") as fp:
                content = fp.read()
                assert "#doitlive env: FIRST=Steve\n" in content
                assert "#doitlive env: LAST=Loria\n" in content

    def test_python_mode(self, runner):
        with recording_session(runner, ["python", 'print("hello")', "exit()"]):
            with open("session.sh", "r") as fp:
                content = fp.read()
                assert "```python\n" in content
                assert 'print("hello")\n' in content
