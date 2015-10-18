# -*- coding: utf-8 -*-
import os
import sys
import webbrowser

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')

@task
def test(tox=False, last_failing=False):
    """Run the tests.

    Note: --watch requires pytest-xdist to be installed.
    """
    if tox:
        run('tox')
    else:
        import pytest
        flake()
        args = []
        if last_failing:
            args.append('--lf')
        retcode = pytest.main(args)
        sys.exit(retcode)

@task
def flake():
    """Run flake8 on codebase."""
    run('flake8 .', echo=True)

@task
def readme(browse=False):
    run('rst2html.py README.rst > README.html')
    if browse:
        webbrowser.open_new_tab('README.html')

@task
def clean():
    run("rm -rf build")
    run("rm -rf dist")
    run("rm -rf doitlive.egg-info")
    clean_docs()
    print("Cleaned up.")

@task
def publish(test=False):
    """Publish to the cheeseshop."""
    clean()
    if test:
        run('python setup.py register -r test sdist', echo=True)
        run('twine upload dist/* -r test', echo=True)
    else:
        run('python setup.py register sdist', echo=True)
        run('twine upload dist/*', echo=True)


@task
def clean_docs():
    run("rm -rf %s" % build_dir)

@task
def browse_docs():
    run("open %s" % os.path.join(build_dir, 'index.html'))

@task
def docs(clean=False, browse=False):
    if clean:
        clean_docs()
    run("sphinx-build %s %s" % (docs_dir, build_dir), pty=True)
    if browse:
        browse_docs()
