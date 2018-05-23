Changelog
---------

4.0.1 (2018-05-22)
******************

Bug fixes:

* Ctrl-Z suspends doitlive (:issue:`44`). Thanks :user:`emanuelhouse`
  for reporting.
* Fix help text for ``--shell`` option (:issue:`43`).

4.0.0.post0 (2018-05-14)
************************

* Distribute a universal wheel.
* Minor docs updates.

4.0.0 (2018-05-13)
******************

Features:

* Add shell completion for bash, zsh, and fish (:issue:`3`).
* Add "Did you mean" suggestions.
* Support setting environment variables with ``export`` commands
  (:issue:`32`). Thanks :user:`asmacdo` for the suggestion.
* Support setting aliases with ``alias`` commands (:issue:`40`).

Bug fixes:

* Fix exiting a command such as ``watch`` with ``ctrl-c`` during a
  session (:issue:`29`). Thanks :user:`zigarn` for the catch and patch.

Other changes:

* Drop official support for Python 3.3 and 3.4. Python 2.7 and >=3.5 are supported.
* Lots of internal re-organization of modules.

3.0.3 (2017-11-08)
******************

Bug fixes:

- `--quiet` options supresses ending message (:issue:`26`). Thanks
  :user:`technovangelist` for reporting and thanks :user:`PandaWhoCodes` for the PR.
- Fix installation issue on Windows (:issue:`4`). Thanks :user:`eXigentCoder` for reporting.

3.0.2 (2017-10-17)
******************

Bug fixes:

- Fix 'cd-ing' to paths with an envvar (:issue:`24`). Thanks :user:`utdrmac` for
  reporting.
- Fix behavior of ``cd -``
- Fix behavior of ``Ctrl-C`` after all commands have finished.

3.0.1 (2017-10-16)
******************

Bug fixes:

- Fix behavior of Backspace key when speed > 1.
- Handle KeyError when ``$HOME`` is unset (:issue:`10`). Thanks :user:`Stefan-Code` for reporting.

3.0.0 (2017-10-15)
******************

- Support IPython>=5.0 (:issue:`20`). Drop support for IPython<5.0. Thanks :user:`rplevka` for
  reporting.
- Use ``$SHELL`` as the default interpreter for commands if not explicitly
  specified.
- Remove invalid import in ``ipython`` module. Thanks :user:`axocomm`.
- Fix exiting a session with Ctrl-C in Python 3.

2.8.0 (2017-10-08)
******************

Bug fixes:

- Don't allow passing a `--speed` that is < 1 (:issue:`17`). Thanks
  :user:`mblhaunted` for reporting and thanks :user:`Stefan-Code` for
  the implementation suggestion.

2.7.0 (2017-03-07)
******************

Features:

- Add ``stev``, ``damoekri``, and ``smiley`` themes.
- Modify ``sorin`` theme to be more like the original prezto theme.

Bug fixes:

- Prevent extra spacing when using ``{vcs_branch}``, ``{git_branch}``, or ``{hg_branch}`` in a custom prompt.

2.6.0 (2017-01-07)
******************

Features:

- Prompt template variables can be styled with ``.inverse``, e.g. ``{user.inverse}``.
- Prompt templates can include ``{nl}`` for displaying new-lines. Thanks :user:`andredias`.

Other changes:

- Test against Python 3.6.

2.5.0 (2016-05-02)
******************

Features

- Add ipython mode (:issue:`8`).

2.4.0 (2015-10-18)
******************

Features:

- Backspace key works during playback.

Bug fixes:

- Prevent unicode_literals import warning from click on Python 2 (:issue:`12`, :issue:`13`).
- Fix bug that caused some keystrokes to get echoed instead of swallowed (:issue:`6`). Thanks :user:`jordigh` for reporting.

Other changes:

- Reorganized as a package. Added ``termutils`` and ``version_control`` modules.

Big thanks to :user:`Stefan-Code` for implementing these changes.

2.3.1 (2015-02-08)
******************

- Fix bug that showed the incorrect prompt on the last slide if the theme was set using the ``#doitlive prompt:`` directive.

2.3.0 (2014-11-16)
******************

- Add support for displaying Mercurial VCS info (current branch, bookmark)
- Add ``commentecho`` CLI option and magic comment.
- Add ``--quiet`` CLI option for suppressing the startup message.

2.2.1 (2014-08-02)
******************

- Fix display of git branches on Python 3 (don't show ``b`` prefix).

2.2.0 (2014-07-13)
******************

- Add ``{TTY}`` prompt variable that contains named constants for ANSI escape sequences.
- Add "giddie" theme.
- Add ``help/H`` command to the recorder console.

2.1.0 (2014-06-25)
******************

- Python mode: Fenced code blocks can be played back in a fake Python console.
- Added ability to preview and undo commands during a recorder session.
- Current datetime (``{now}``) can be included in prompt.
- Added 'pws' theme.
- Added ``--envvar`` and ``--alias`` options to ``record`` command.
- Added ``unalias`` and ``unset`` comment directives.


2.0 (2014-06-21)
****************

- Added session recorder (``doitlive record``).
- Improved interface.
- Sessions are played with ``doitlive play <session_file>``.
- Deprecated ``doitlive-demo``. Run ``doitlive demo`` instead.
- Deprecated ``doitlive --themes`` and ``doitlive --themes-preview``. Run ``doitlive themes`` and ``doitlive themes --preview`` instead.
- Fix bug that raised an error when cd'ing into a non-existent directory.
- Remove extra spacing in prompt when not in a git directory.
- Added 'robbyrussell' theme.


1.0 (2014-06-18)
****************

- Added themes!
- Prompt variables can have ANSI colors and styles.
- ``{hostname}`` can be included in prompt.
- ``{git_branch}`` can be included in prompt.
- Prompt variable ``{full_cwd}`` renamed to ``{cwd}``.
- Prompt variable ``{cwd}`` renamed to ``{dir}``.
- Short option for ``--speed`` is now ``-s``.
- Short option for ``--shell`` is now ``-S``.
- Changed default prompt.
- ``run`` and ``magictype`` receive prompt_template instead of a prompt function.
- Remove unnecessary ``PromptState`` class.

0.2.0 (2014-06-16)
******************

- Add "speed" config option.
- Fix short option for "--shell".
- Custom prompts are colored.
- Remove unnecessary --check-output option, which was only used for testing.
- Fix bug where cwd would not update in custom prompts.

0.1.0 (2014-06-15)
******************

- Initial release.
