# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import random
import getpass

import pytest
from click.testing import CliRunner

import doitlive
from doitlive import cli

random.seed(42)
HERE = os.path.abspath(os.path.dirname(__file__))

def random_string(n, alphabet='abcdefghijklmnopqrstuvwxyz1234567890;\'\\][=-+_`'):
    return ''.join([random.choice(alphabet) for _ in range(n)])

@pytest.fixture(scope='session')
def runner():
    return CliRunner()

def run_session(runner, filename, user_input):
    session = os.path.join(HERE, filename)
    # Press ENTER at beginning of session and ENTER twice at end
    user_in = ''.join(['\r', user_input, '\r\r'])
    return runner.invoke(cli, [session, '--check-output'], input=user_in)


def test_basic_session(runner):
    user_input = random_string(len('echo "Hello"'))
    result = run_session(runner, 'basic.session', user_input)

    assert result.exit_code == 0
    assert 'echo "Hello"' in result.output

def test_session_with_unicode(runner):
    user_input = random_string(len(u'echo "H´l¬ø ∑ø®ld"'))
    result = run_session(runner, 'unicode.session', user_input)
    assert result.exit_code == 0

def test_session_with_envvar(runner):
    user_input = random_string(len('echo $HOME'))

    result = run_session(runner, 'env.session', user_input)
    assert result.exit_code == 0
    assert os.environ['HOME'] in result.output

def test_session_with_comment(runner):
    user_input = random_string(len('echo foo'))
    result = run_session(runner, 'comment.session', user_input)
    assert result.exit_code == 0
    assert 'foo' not in result.output, 'comment was not skipped'
    assert 'bar' in result.output

def test_esc_key_aborts(runner):
    result = run_session(runner, 'basic.session', 'echo' + doitlive.ESC)
    assert result.exit_code > 0

def test_pwd(runner):
    user_input = random_string(3)
    result = run_session(runner, 'pwd.session', user_input)
    assert os.getcwd() in result.output

def test_custom_prompt(runner):
    user_input = random_string(len('echo'))
    result = run_session(runner, 'prompt.session', user_input)
    assert getpass.getuser() in result.output

def test_custom_var(runner):
    user_input = random_string(len('echo $MEANING'))
    result = run_session(runner, 'envvar.session', user_input)
    assert '42' in result.output

def test_custom_speed(runner):
    user_input = random_string(3)
    result = run_session(runner, 'speed.session', user_input)
    assert '123456789' in result.output
