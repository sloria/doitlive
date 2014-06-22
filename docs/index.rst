**********
$ doitlive
**********

..

   Because sometimes you need to do it live


Current version: v\ |version|.

`doitlive` is a tool for live presentations in the terminal. It reads a file of shell commands and replays the commands in a fake terminal session as you type random characters.

Get it now
==========

.. code-block:: bash

    $ pip install doitlive

Requires Python >= 2.7 or >= 3.3 with pip.

Quickstart
==========

1. Create a file called ``session.sh``. Fill it with bash commands.
2. Run ``doitlive play session.sh``.

.. code-block:: bash

    $ doitlive play session.sh


3. Type like a madman.


Examples
========

.. code-block:: bash

    # Use the "sorin" prompt theme
    $ doitlive play session.sh -p sorin

    # Increase speed
    $ doitlive play session.sh -s 3

    # Use zsh
    $ doitlive play session.sh --shell /bin/zsh

Using the recorder
==================

You can record session files using the built-in recorder command.

.. code-block:: bash

    $ doitlive record

This will start a recording session. When you are finished recording, run the ``stop`` command. All commands will be written to a ``session.sh`` file.

Themes
======

doitlive comes with many prompt themes. To use a theme:

.. code-block:: bash

    $ doitlive play session.sh -p <theme_name>


To view a list of available themes, run ``doitlive themes`` or ``doitlive themes --preview``.


Comment magic (configuration)
=============================

Any line in a session file that begins with  ``#`` is a comment. Comments are ignored unless they begin with ``#doitlive``, in which case they are used to configure the session.

The following options can be included at the top of your session file (all are optional).

#doitlive speed: <int>
----------------------

configures "typing" speed. Defaults to 1.

Example: ``#doitlive speed: 3``

#doitlive prompt: <theme_name_or_template>
------------------------------------------

configures the prompt. Can be any of the built-in themes or a custom prompt template.

**Using a custom template**:

You can provide the ``prompt`` option with a custom template. To include the user, hostname, current directory, current path to working directory, or git branch, use ``{user}``, ``{hostname}``, ``{dir}``, ``{cwd}``, and ``{git_branch}``, respectively.

Example: ``#doitlive prompt: {user} is at {cwd} $``

Any of the prompt variables can be formatted with ANSI styles, like so:


Example: ``#doitlive prompt: {user.cyan}@{hostname.green}:{dir.bold.magenta} $``


Available styles: blue, magenta, red, white, green, black, yellow, cyan, bold, blink, underlined, dim, paren, square, curly.


#doitlive shell: <shell>
-------------------------

configures which shell is use.


Example: ``#doitlive shell: /bin/zsh``


#doitlive alias: <name>=<command>
---------------------------------

adds an alias to the session.

Example: ``#doitlive alias: du="du -ach | sort -h"``

#doitlive env: <envvar>=<value>
-------------------------------

sets an environment variable.

Example: ``#doitlive env: EDITOR=vim``


Bash completion
===============

To enable bash completion, add the following to your ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    eval "$(_DOITLIVE_COMPLETE=source doitlive)"


Completion is currently only supported for ``bash``.


More
====

For more options, run

.. code-block:: bash

    $ doitlive --help


You can also get help with subcommands.

.. code-block:: bash

    $ doitlive play --help


Project info
============

.. toctree::
   :maxdepth: 1

   changelog
   license
   authors
   kudos

