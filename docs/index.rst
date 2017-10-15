========
doitlive
========
..

   Because sometimes you need to do it live

Current version: v\ |version|.

.. image:: https://user-images.githubusercontent.com/2379650/31386572-2e2b9d14-ad95-11e7-9be5-fcc5ed09f0e8.gif
    :alt: Demo
    :target: http://doitlive.readthedocs.io

`doitlive` is a tool for live presentations in the terminal. It reads a file of shell commands and replays the commands in a fake terminal session as you type random characters.

.. contents::
   :local:
   :depth: 1


Get it now
----------

MacOSX with `Homebrew <http://brew.sh/>`_:
******************************************

.. code-block:: bash

    $ brew update
    $ brew install doitlive

With pip:
*********

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


Examples
--------

.. code-block:: bash

    # Use the "sorin" prompt theme
    $ doitlive play session.sh -p sorin

    # Increase speed
    $ doitlive play session.sh -s 3

    # Use zsh
    $ doitlive play session.sh --shell /bin/zsh

Using the recorder
------------------

You can record session files using the built-in recorder command.

.. code-block:: bash

    $ doitlive record

This will start a recording session. When you are finished recording, run the ``stop`` command. All commands will be written to a ``session.sh`` file.

Themes
------

.. image:: https://user-images.githubusercontent.com/2379650/31581943-6f763608-b13c-11e7-8bc1-6e0403f7d3b4.png
    :alt: Themes preview

doitlive comes with many prompt themes. To use a theme:

.. code-block:: bash

    $ doitlive play session.sh -p <theme_name>


You can also change a session's theme by using a comment directive (see :ref:`Comment magic <comment_magic>` below).

To view a list of available themes, run ``doitlive themes`` or ``doitlive themes --preview``.


.. _comment_magic:

Comment magic (configuration)
-----------------------------

Any line in a session file that begins with  ``#`` is a comment. Comments are ignored unless they begin with ``#doitlive``, in which case they are used to configure the session.

The following options can be included at the top of your session file (all are optional).

#doitlive speed: <int>
**********************

configures "typing" speed. Defaults to 1.

Example: ``#doitlive speed: 3``

#doitlive prompt: <theme_name_or_template>
******************************************

configures the prompt. Can be any of the built-in themes or a custom prompt template.

**Using a custom template**:

You can provide the ``prompt`` option with a custom template. To include the user, hostname, current directory, current path to working directory, current datetime, or vcs branch (git or Mercurial), use ``{user}``, ``{hostname}``, ``{dir}``, ``{cwd}``, ``{now}``, and ``{vcs_branch}``, respectively.

For git, ``{vcs_branch}`` just shows the branch. For Mercurial, this shows the branch name + the bookmark, except it omits the default branch name if there is a bookmark. This is equivalent to ``{git_branch}{hg_id}``. There are also specialised ``{hg_branch}``, and ``{hg_bookmark}`` keywords that only show that information, without the combined logic of ``{hg_id}``.

Example: ``#doitlive prompt: {user} is at {cwd} $``

Any of the prompt variables can be formatted with ANSI styles, like so:


Example: ``#doitlive prompt: {user.cyan}@{hostname.green}:{dir.bold.magenta} $``

Newlines can be included in prompts using ``{nl}``.

Example: ``#doitlive prompt: {user}:{dir}{nl}$``

Available styles: blue, magenta, red, white, green, black, yellow, cyan, bold, blink, underlined, dim, paren, square, curly, inverse, git, and hg.


#doitlive shell: <shell>
************************

configures which shell is use. Default is ``/bin/bash``.


Example: ``#doitlive shell: /bin/zsh``


#doitlive alias: <alias>=<command>
**********************************

adds an alias to the session.

Example: ``#doitlive alias: du="du -ach | sort -h"``


#doitlive env: <envvar>=<value>
*******************************

sets an environment variable.

Example: ``#doitlive env: EDITOR=vim``

#doitlive unalias: <alias>
**************************

removes an alias.

#doitlive unset: <envvar>
*************************

unsets an environment variable.

#doitlive commentecho: [true|false]
************************************

Whether to echo comments or not. If enabled, non-magic comments will be echoed back in bold yellow before each prompt. This can be useful for providing some annotations for yourself and the audience.


Python mode
-----------

doitlive supports autotyping in a Python console. You can enter Python mode in a session by enclosing Python code in triple-backticks, like so:

.. code-block:: bash

    # in session.sh

    echo "And now for something completely different"

    ```python
    list = [2, 4, 6, 8]
    sum = 0
    for num in list:
        sum = sum + num

    print("The sum is: {sum}".format(sum=sum))
    ```

IPython mode
------------

If you have `IPython <https://ipython.org/>`_ installed, you can run doitlive in ``ipython`` mode. Just enclose your Python code in triple-backticks, like so:

.. code-block:: bash

   # in session.sh

   ```ipython
   def fib(n):
      a, b = 0, 1
      while a < n:
         print(a, end=' ')
         a, b = b, a+b
      print()

   # Magic!
   %time fib(100)

   ```

.. note::

   Only IPython>=5.0 is supported.


Bash completion
---------------

To enable bash completion, add the following to your ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    eval "$(_DOITLIVE_COMPLETE=source doitlive)"


Completion is currently only supported for ``bash``.


More
----

For more options, run

.. code-block:: bash

    $ doitlive --help


You can also get help with subcommands.

.. code-block:: bash

    $ doitlive play --help


Project info
------------

.. toctree::
   :maxdepth: 1

   changelog
   license
   authors
   kudos

