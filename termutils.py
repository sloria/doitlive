import tty
import termios
import sys
from contextlib import contextmanager

def isatty(stream):
    """
    Shamelessly stolen from https://github.com/mitsuhiko/click/
    """
    try:
        return stream.isatty()
    except Exception:
        return False

@contextmanager
def raw_mode():
    """
    Enables terminal raw mode during the context.
    For now this only works for Linux.
    Usage:
    with raw_mode():
        do_some_stuff()
    """
    if not isatty(sys.stdin):
        f = open('/dev/tty')
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
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # sys.stdout.flush()  # not needed I think.
            if f is not None:
                f.close()
        except termios.error:
            pass
