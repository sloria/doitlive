========
doitlive
========

.. image:: https://badge.fury.io/py/doitlive.png
  :target: http://badge.fury.io/py/doitlive

.. image:: https://travis-ci.org/sloria/doitlive.png?branch=master
  :target: https://travis-ci.org/sloria/doitlive


`doitlive` is a tool for live presentations in the terminal. It reads a file of shell commands and replays the commands in a fake terminal session as you type random characters.


Get it now
----------

.. code-block:: bash

    $ pip install doitlive

Requires Python >= 2.7 or >= 3.3 with pip.

Quickstart
----------

1. Create a file called ``session.sh``. Fill it with bash commands.
2. Run ``doitlive play session.sh``.

.. code-block:: bash

    $ doitlive play session.sh


3. Type like a madman.


More at http://doitlive.rtfd.org
--------------------------------


Kudos
-----

- Idea came from Jordi Hermoso's `"Revsets" talk <https://www.youtube.com/watch?list=PLLj6w0Thbv02lEXIDVO46kotA_tv_8_us&feature=player_detailpage&v=NSLvERZQSok#t=978>`_  at PyCon 2014.
- Armin Ronacher's `click <http://click.pocoo.org/>`_ library  made this quick to implement.
- Themes inspired by Sorin Ionescu's `prezto <https://github.com/sorin-ionescu/prezto>`_ zsh themes.


License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/sloria/doitlive/blob/master/LICENSE>`_ file for more details.
