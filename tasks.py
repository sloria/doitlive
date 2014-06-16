# -*- coding: utf-8 -*-
import os

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')

@task
def test(tox=False):
    if tox:
        run('tox', pty=True)
    else:
        run('python setup.py test', pty=True)

@task
def readme(browse=False):
    run('rst2html.py README.rst > README.html')

@task
def publish(test=False):
    """Publish to the cheeseshop."""
    if test:
        run('python setup.py register -r test sdist upload -r test')
    else:
        run("python setup.py register sdist upload")


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
