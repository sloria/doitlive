import pytest
from click.testing import CliRunner

import doitlive
import doitlive.ipython


@pytest.fixture(scope="session")
def runner():
    doitlive.cli.TESTING = True
    return CliRunner()


def pytest_ignore_collect(path, config):
    if doitlive.ipython.is_modern_ipython():
        return path.basename == "test_ipython_legacy.py"

    return path.basename == "test_ipython.py"
