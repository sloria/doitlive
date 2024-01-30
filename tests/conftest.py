import pytest
from click.testing import CliRunner

import doitlive


@pytest.fixture(scope="session")
def runner():
    doitlive.cli.TESTING = True
    return CliRunner()
