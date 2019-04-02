# -*- coding: utf-8 -*-
import codecs
import re
import sys
from setuptools import setup


INSTALL_REQUIRES = ["click>=4.0", "click-completion>=0.3.1", "click-didyoumean>=0.0.3"]

if "win32" in str(sys.platform).lower():
    # Terminal colors for Windows
    INSTALL_REQUIRES.append("colorama>=0.2.4")

EXTRAS_REQUIRE = {
    "tests": [
        "pytest",
        'IPython<6; python_version < "3"',
        'IPython==6.5.0; python_version >= "3"',
    ],
    "lint": [
        "flake8==3.7.7",
        'flake8-bugbear==18.8.0; python_version >= "3.5"',
        "pre-commit==1.15.1",
    ],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + ["tox"]


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with codecs.open(fname, "r", encoding="utf-8") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with codecs.open(fname, "r", encoding="utf-8") as fp:
        content = fp.read()
    return content


setup(
    name="doitlive",
    version=find_version("doitlive/__version__.py"),
    description="Because sometimes you need to do it live.",
    long_description=read("README.rst"),
    author="Steven Loria",
    author_email="sloria1@gmail.com",
    url="https://github.com/sloria/doitlive",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    license="MIT",
    zip_safe=False,
    keywords="doitlive cli live coding presentations shell",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
    ],
    packages=["doitlive"],
    entry_points={"console_scripts": ["doitlive = doitlive.cli:cli"]},
    tests_require=["pytest"],
    project_urls={
        "Bug Reports": "https://github.com/sloria/doitlive/issues",
        "Source": "https://github.com/sloria/doitlive/",
    },
)
