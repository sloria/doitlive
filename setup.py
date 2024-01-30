import codecs
import re

from setuptools import setup

INSTALL_REQUIRES = [
    "click>=8.0,<9",
    "click-completion>=0.3.1",
    "click-didyoumean>=0.0.3",
]

EXTRAS_REQUIRE = {
    "tests": ["pytest", "IPython"],
    "lint": [
        "flake8==7.0.0",
        "flake8-bugbear==23.12.2",
        "pre-commit~=3.5",
    ],
    "docs": [
        "sphinx==7.2.6",
        "sphinx-issues==4.0.0",
    ],
}
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + EXTRAS_REQUIRE["docs"] + ["tox"]
)


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
    python_requires=">=3.8",
    license="MIT",
    zip_safe=False,
    keywords="doitlive cli live coding presentations shell",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
