import os
import sys
from contextlib import contextmanager

from click._compat import isatty

WIN = sys.platform.startswith("win")
CI = "CI" in os.environ

env = os.environ


@contextmanager
def raw_mode():
    """
    Enables terminal raw mode during the context.

    Note: Currently noop for Windows systems.

    Usage: ::

        with raw_mode():
            do_some_stuff()
    """
    if WIN or CI:
        # No implementation for windows yet.
        yield  # needed for the empty context manager to work
    else:
        #  imports are placed here because this will fail under Windows
        import tty
        import termios

        if not isatty(sys.stdin):
            f = open("/dev/tty")
            fd = f.fileno()
        else:
            fd = sys.stdin.fileno()
            f = None
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except termios.error:
            pass
        try:
            yield
        finally:
            # this block sets the terminal to sane mode again,
            # also in case an exception occurred in the context manager
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                # sys.stdout.flush()  # not needed I think.
                if f is not None:
                    f.close()
            except termios.error:
                pass


def get_default_shell():
    return env.get("DOITLIVE_INTERPRETER") or env.get("SHELL") or "/bin/bash"
