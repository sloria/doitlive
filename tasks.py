# -*- coding: utf-8 -*-
import os
import sys
import webbrowser

from invoke import task

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')

@task
def test(ctx, tox=False, lint=True, last_failing=False):
    """Run the tests.

    Note: --watch requires pytest-xdist to be installed.
    """
    if tox:
        ctx.run('tox')
    else:
        import pytest
        if lint:
            flake(ctx)
        args = ['-s']
        if last_failing:
            args.append('--lf')
        retcode = pytest.main(args)
        sys.exit(retcode)

@task(aliases=['lint', 'flake8'])
def flake(ctx):
    """Run flake8 on codebase."""
    ctx.run('flake8 .', echo=True)

@task
def readme(ctx, browse=False):
    ctx.run('rst2html.py README.rst > README.html', echo=True)
    if browse:
        webbrowser.open_new_tab('README.html')

@task
def clean(ctx):
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf doitlive.egg-info")
    clean_docs(ctx)
    print("Cleaned up.")

@task
def clean_docs(ctx):
    ctx.run("rm -rf %s" % build_dir)

@task
def browse_docs(ctx):
    ctx.run("open %s" % os.path.join(build_dir, 'index.html'))

@task
def docs(ctx, clean=False, browse=False):
    if clean:
        clean_docs(ctx)
    ctx.run("sphinx-build %s %s" % (docs_dir, build_dir), pty=True)
    if browse:
        browse_docs(ctx)
