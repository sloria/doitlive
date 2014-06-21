Changelog
---------

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
- Prompt variable ``{{full_cwd}}`` renamed to ``{{cwd}}``.
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
