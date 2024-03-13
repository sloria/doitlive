"""
doitlive
~~~~~~~~

A tool for "live" presentations in the terminal.
"""

from .cli import SessionState
from .exceptions import ConfigurationError, DoItLiveError, SessionError
from .keyboard import BACKSPACE, CTRLC, ESC, RETURNS, magicrun, magictype, wait_for
from .python_consoles import PythonPlayerConsole, PythonRecorderConsole
from .styling import THEMES, TTY, Style, TermString, echo, echo_prompt, format_prompt
from .version_control import (
    get_current_git_branch,
    get_current_hg_branch,
    get_current_vcs_branch,
)

__all__ = [
    "SessionState",
    "PythonRecorderConsole",
    "PythonPlayerConsole",
    "THEMES",
    "Style",
    "TermString",
    "TTY",
    "echo",
    "echo_prompt",
    "format_prompt",
    "wait_for",
    "magictype",
    "magicrun",
    "ESC",
    "BACKSPACE",
    "CTRLC",
    "RETURNS",
    "get_current_git_branch",
    "get_current_hg_branch",
    "get_current_vcs_branch",
    "DoItLiveError",
    "ConfigurationError",
    "SessionError",
]
