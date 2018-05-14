========
doitlive
========

.. image:: https://img.shields.io/homebrew/v/doitlive.svg
  :alt: homebrew badge
  :target: https://github.com/Homebrew/homebrew-core/blob/master/Formula/doitlive.rb

.. image:: https://badge.fury.io/py/doitlive.svg
  :alt: pypi badge
  :target: http://badge.fury.io/py/doitlive

.. image:: https://travis-ci.org/sloria/doitlive.svg
  :alt: travis-ci status
  :target: https://travis-ci.org/sloria/doitlive


`doitlive` is a tool for live presentations in the terminal. It reads a file of shell commands and replays the commands in a fake terminal session as you type random characters.

.. image:: https://user-images.githubusercontent.com/2379650/31386572-2e2b9d14-ad95-11e7-9be5-fcc5ed09f0e8.gif
    :alt: Demo
    :target: http://doitlive.readthedocs.io


Get it now
----------

macOS with `Homebrew <http://brew.sh/>`_:
*****************************************

.. code-block:: bash

    $ brew update
    $ brew install doitlive

With pip:
*********

.. code-block:: bash

    $ pip install doitlive


Requires Python >= 2.7 or >= 3.5 with pip.

Quickstart
----------

1. Create a file called ``session.sh``. Fill it with bash commands.
2. Run ``doitlive play session.sh``.

.. code-block:: bash

    $ doitlive play session.sh


3. Type like a madman.


More at https://doitlive.readthedocs.io
---------------------------------------

Project Links
-------------

- Docs: https://doitlive.readthedocs.io/
- Changelog: https://doitlive.readthedocs.io/en/latest/changelog.html
- PyPI: https://pypi.python.org/pypi/doitlive
- Issues: https://github.com/sloria/doitlive/issues

Kudos
-----

- Idea came from Jordi Hermoso's `"Revsets" talk <https://www.youtube.com/watch?list=PLLj6w0Thbv02lEXIDVO46kotA_tv_8_us&feature=player_detailpage&v=NSLvERZQSok#t=978>`_  at PyCon 2014.
- Armin Ronacher's `click <http://click.pocoo.org/>`_ library  made this quick to implement.
- Themes inspired by Sorin Ionescu's `prezto <https://github.com/sorin-ionescu/prezto>`_ zsh themes.
- Hat tip to related projects `HackerTyper <http://hackertyper.com/>`_ and `PlayerPiano <http://i.wearpants.org/blog/playerpiano-amaze-your-friends/>`_


License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/sloria/doitlive/blob/master/LICENSE>`_ file for more details.
