# -*- coding: utf-8 -*-
import sys
import os
import datetime as dt

sys.path.insert(0, os.path.abspath(".."))
import doitlive  # noqa: E402

sys.path.append(os.path.abspath("_themes"))

extensions = ["sphinx_issues"]

issues_github_path = "sloria/doitlive"

templates_path = ["_templates"]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = u"doitlive"
copyright = u"2014-{0:%Y}".format(dt.datetime.utcnow())

version = release = doitlive.__version__

exclude_patterns = ["_build"]
pygments_style = "flask_theme_support.FlaskyStyle"
html_theme = "kr_small"

html_theme_options = {
    "index_logo": "doitlive-logo.png",
    "index_logo_height": "200px",
    "github_fork": "sloria/doitlive",
}

html_theme_path = ["_themes"]
html_static_path = ["_static"]
