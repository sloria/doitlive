import importlib.metadata
import os
import sys

sys.path.append(os.path.abspath("_themes"))

extensions = ["sphinx_issues"]

issues_github_path = "sloria/doitlive"

templates_path = ["_templates"]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "doitlive"
copyright = "Steven Loria and contributors"

version = release = importlib.metadata.version("doitlive")

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
