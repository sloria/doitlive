import os
import shlex
import signal
import subprocess
from tempfile import NamedTemporaryFile

import click
from click import getchar

from doitlive.styling import echo, echo_prompt
from doitlive.termutils import get_default_shell, raw_mode

env = os.environ

ESC = "\x1b"
BACKSPACE = "\x7f"
CTRLC = "\x03"
CTRLL = "\x0C"
CTRLZ = "\x1a"
TAB = "\x09"
RETURNS = {"\r", "\n"}


def wait_for(chars):
    while True:
        in_char = getchar()
        if in_char in {ESC, CTRLC}:
            echo(carriage_return=True)
            raise click.Abort()
        if in_char in chars:
            echo()
            return in_char


def magictype(text, prompt_template="default", speed=1):
    """Echo each character in ``text`` as keyboard characters are pressed.
    Characters are echo'd ``speed`` characters at a time.
    """
    echo_prompt(prompt_template)
    cursor_position = 0
    return_to_regular_type = False
    with raw_mode():
        while True:
            char = text[cursor_position : cursor_position + speed]
            in_char = getchar()
            if in_char in {ESC, CTRLC}:
                echo(carriage_return=True)
                raise click.Abort()
            elif in_char == CTRLL:
                click.clear()
                echo_prompt(prompt_template)
                cursor_position = 0
                continue
            elif in_char == TAB:
                return_to_regular_type = True
                break
            elif in_char == BACKSPACE:
                if cursor_position > 0:
                    echo("\b \b", nl=False)
                    cursor_position -= 1
            elif in_char in RETURNS:
                # Only return at end of command
                if cursor_position >= len(text):
                    echo("\r", nl=True)
                    break
            elif in_char == CTRLZ and hasattr(signal, "SIGTSTP"):
                # Background process
                os.kill(0, signal.SIGTSTP)
                # When doitlive is back in foreground, clear the terminal
                # and resume where we left off
                click.clear()
                echo_prompt(prompt_template)
                echo(text[:cursor_position], nl=False)
            else:
                if cursor_position < len(text):
                    echo(char, nl=False)
                    increment = min([speed, len(text) - cursor_position])
                    cursor_position += increment
    return return_to_regular_type


def write_commands(fp, command, args):
    if args:
        for arg in args:
            line = f"{command} {arg}\n"
            fp.write(line)
    return None


def run_command(
    cmd, shell=None, aliases=None, envvars=None, extra_commands=None, test_mode=False
):
    shell = shell or get_default_shell()
    command_as_list = shlex.split(cmd)
    if len(command_as_list) and command_as_list[0] == "cd":
        cwd = os.getcwd()  # Save cwd
        directory = cmd.split()[1].strip()
        if directory == "-":  # Go back to $OLDPWD
            directory = os.environ.get("OLDPWD", directory)
        try:
            os.chdir(os.path.expandvars(os.path.expanduser(directory)))
        except OSError:
            echo(f"No such file or directory: {directory}")
        else:
            os.environ["OLDPWD"] = cwd

    else:
        # Need to make a temporary command file so that $ENV are used correctly
        # and that shell built-ins, e.g. "source" work
        with NamedTemporaryFile("w") as fp:
            fp.write(f"#!{shell}\n")
            fp.write("# -*- coding: utf-8 -*-\n")
            # Make aliases work in bash:
            if "bash" in shell:
                fp.write("shopt -s expand_aliases\n")

            # Write envvars and aliases
            write_commands(fp, "export", envvars)
            write_commands(fp, "alias", aliases)
            if extra_commands:
                for command in extra_commands:
                    line = f"{command}\n"
                    fp.write(line)

            cmd_line = cmd + "\n"
            fp.write(cmd_line)
            fp.flush()
            try:
                if test_mode:
                    output = subprocess.check_output([shell, fp.name])
                    echo(output)
                else:
                    return subprocess.call([shell, fp.name])
            except KeyboardInterrupt:
                pass


def regulartype(prompt_template="default"):
    """Echo each character typed. Unlike magictype, this echos the characters the
    user is pressing.

    Returns: command_string |  The command to be passed to the shell to run. This is
                            |  typed by the user.
    """
    echo_prompt(prompt_template)
    command_string = ""
    cursor_position = 0
    with raw_mode():
        while True:
            in_char = getchar()
            if in_char in {ESC, CTRLC}:
                echo(carriage_return=True)
                raise click.Abort()
            elif in_char == CTRLL:
                click.clear()
                echo_prompt(prompt_template)
                cursor_position = 0
                continue
            elif in_char == TAB:
                echo("\r", nl=True)
                return in_char
            elif in_char == BACKSPACE:
                if cursor_position > 0:
                    echo("\b \b", nl=False)
                    command_string = command_string[:-1]
                    cursor_position -= 1
            elif in_char in RETURNS:
                echo("\r", nl=True)
                return command_string
            elif in_char == CTRLZ and hasattr(signal, "SIGTSTP"):
                # Background process
                os.kill(0, signal.SIGTSTP)
                # When doitlive is back in foreground, clear the terminal
                # and resume where we left off
                click.clear()
                echo_prompt(prompt_template)
            else:
                echo(in_char, nl=False)
                command_string += in_char
                cursor_position += 1


def regularrun(
    shell,
    prompt_template="default",
    aliases=None,
    envvars=None,
    extra_commands=None,
    speed=1,
    test_mode=False,
    commentecho=False,
):
    """Allow user to run their own live commands until CTRL-Z is pressed again."""
    loop_again = True
    command_string = regulartype(prompt_template)
    if command_string == TAB:
        loop_again = False
        return loop_again
    run_command(
        command_string,
        shell,
        aliases=aliases,
        envvars=envvars,
        extra_commands=extra_commands,
        test_mode=test_mode,
    )
    return loop_again


def magicrun(
    text,
    shell,
    prompt_template="default",
    aliases=None,
    envvars=None,
    extra_commands=None,
    speed=1,
    test_mode=False,
    commentecho=False,
):
    """Echo out each character in ``text`` as keyboard characters are pressed,
    wait for a RETURN keypress, then run the ``text`` in a shell context.
    """
    goto_regulartype = magictype(text, prompt_template, speed)
    if goto_regulartype:
        return goto_regulartype
    run_command(
        text,
        shell,
        aliases=aliases,
        envvars=envvars,
        extra_commands=extra_commands,
        test_mode=test_mode,
    )
    return goto_regulartype
