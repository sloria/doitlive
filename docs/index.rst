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

Requires Python >= 2.7 or >= 3.3 with pip.

Usage
=====

1. Create a file called ``session.sh``. Fill it with bash commands.
2. Run ``doitlive session.sh``

.. code-block:: bash

    $ doitlive session.sh


3. Type like a madman.


Comment magic (configuration)
=============================

Any line that begins with  ``#`` is a comment. Comments are ignored unless they begin with ``#doitlive``, in which case they are used to configure the session.

The following options can be included at the top of your session file (all are optional).

#doitlive speed: <int>
----------------------

configures "typing" speed. Defaults to 1.

Example: ``#doitlive speed: 3``

#doitlive prompt: <theme_name_or_template>
------------------------------------------

configures the prompt. Can be any of the built-in themes or a custom prompt template. To preview a list of available themes, run ``doitlive --themes``.

**Using a custom template**:

To include the user, hostname, current directory, current path to working directory, or git branch, use ``{user}``, ``{hostname}``, ``{dir}``, ``{cwd}``, and ``{git_branch}``, respectively.

Example: ``#doitlive prompt: {user} is at {cwd} $``

Any of the prompt variables can be formatted with ANSI styles through special attribute access.


Example: ``#doitlive prompt: {user.cyan}@{hostname.green}:{dir.bold.magenta} $``


#doitlive shell: <shell>
-------------------------

configures which shell is used to run subsequent commands.


Example: ``#doitlive shell: /bin/zsh``


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

