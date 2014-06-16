**********
$ doitlive
**********

..

   Because sometimes you need to do it live


`doitlive` is a tool for live presentations in the terminal. It reads a file of shell commands and replays the commands in a fake terminal session as you type random characters.

Get it now
==========

.. code-block:: bash

    $ pip install doitlive


Usage
=====

1. Create a file called ``session.sh``. Fill it with some bash commands.
2. Run ``doitlive session.sh``

.. code-block:: bash

    $ doitlive session.sh


3. Type like a madman.


Comment magic (configuration)
=============================

Any line that begins with  ``#`` is a comment. Comments are ignored unless they begin with ``#doitlive``, in which case they are used to configure the session.

The following options can be included at the top of your session file.

#doitlive prompt: <prompt>
--------------------------

configures the prompt. To include the user, current working directory, or the absolute path to the current directory, use `{user}`, `{cwd}`, and `{full_cwd}`, respectively.

Example: ``#doitlive prompt: {user} is at {cwd} $``


#doitlive interpreter: <interpreter>
------------------------------------

configures which interpreter is used to run subsequent commands.


Example: ``#doitlive interpreter: /bin/zsh``


#doitlive alias: <name>=<command>
---------------------------------

adds an alias to the session.

Example: ``#doitlive alias: du="du -ach | sort -h"``

#doitlive env: <envvar>=<value>
-------------------------------

sets an environment variable.

Example: ``#doitlive env: EDITOR=vim``


Project info
============

.. toctree::
   :maxdepth: 1

   changelog
   license
   kudos

