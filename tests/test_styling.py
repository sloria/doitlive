import click
import pytest
from click import style

from doitlive import TermString, TTY


class TestTermString:
    @pytest.fixture
    def ts(self):
        return TermString("foo")

    @pytest.fixture
    def ts_blank(self):
        return TermString("")

    def test_str(self, ts):
        assert str(ts) == "foo"

    # Test all the ANSI colors provided by click
    @pytest.mark.parametrize("color", click.termui._ansi_colors)
    def test_color(self, color, ts):
        colored = getattr(ts, color)
        assert isinstance(colored, TermString)
        assert str(colored) == style("foo", fg=color)

    def test_bold(self, ts):
        assert str(ts.bold) == style("foo", bold=True)

    def test_blink(self, ts):
        assert str(ts.blink) == style("foo", blink=True)

    def test_dim(self, ts):
        assert str(ts.dim) == style("foo", dim=True)

    def test_underlined(self, ts):
        assert str(ts.underlined) == style("foo", underline=True)

    def test_paren(self, ts, ts_blank):
        assert str(ts.paren) == "(foo)"
        assert str(ts_blank.paren) == "\b"

    def test_square(self, ts, ts_blank):
        assert str(ts.square) == "[foo]"
        assert str(ts_blank.square) == "\b"

    def test_curly(self, ts, ts_blank):
        assert str(ts.curly) == "{foo}"
        assert str(ts_blank.curly) == "\b"

    def test_git(self, ts, ts_blank):
        assert str(ts.git) == ":".join([style("git", fg="blue"), "foo"])
        assert str(ts_blank.git) == "\b"


class TestTTY:
    @pytest.mark.parametrize(
        "color", ["blue", "red", "magenta", "white", "green", "black", "yellow", "cyan"]
    )
    def test_colors(self, color):
        code = getattr(TTY, color.upper())
        assert code == style("", fg=color, reset=False)

    def test_bold(self):
        assert TTY.BOLD == style("", bold=True, reset=False)

    def test_blink(self):
        assert TTY.BLINK == style("", blink=True, reset=False)

    def test_underline(self):
        assert TTY.UNDERLINE == style("", underline=True, reset=False)

    def test_dim(self):
        assert TTY.DIM == style("", dim=True, reset=False)
