#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
doitlive
~~~~~~~~

A tool for "live" presentations in the terminal.
"""
from .cli import SessionState
from .python_consoles import PythonRecorderConsole, PythonPlayerConsole
from .styling import THEMES, Style, TermString, TTY, echo, echo_prompt, format_prompt
from .keyboard import wait_for, magictype, magicrun, ESC, BACKSPACE, CTRLC, RETURNS
from .version_control import get_current_git_branch, get_current_hg_branch, get_current_vcs_branch
from .exceptions import DoItLiveError, ConfigurationError, SessionError
from .__version__ import __version__

__author__ = 'Steven Loria'
__license__ = 'MIT'
__version__ = __version__
__all__ = [
    'SessionState',
    'PythonRecorderConsole',
    'PythonPlayerConsole',
    'THEMES',
    'Style',
    'TermString',
    'TTY',
    'echo',
    'echo_prompt',
    'format_prompt',
    'wait_for',
    'magictype',
    'magicrun',
    'ESC',
    'BACKSPACE',
    'CTRLC',
    'RETURNS',
    'get_current_git_branch',
    'get_current_hg_branch',
    'get_current_vcs_branch',
    'DoItLiveError',
    'ConfigurationError',
    'SessionError',
]
