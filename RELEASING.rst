=========
Releasing
=========

* Bump version in ``doitlive/__init__.py``.
* Update ``CHANGELOG.rst``.
* Commit: ``git add . && git commit -m "Bump version and update changelog"``
* Tag: ``git tag x.y.z``
* Push (this will trigger a release to PyPI): ``git push origin dev && git push origin dev --tags``
* Merge ``dev`` into ``pypi``: ``git checkout pypi && git merge dev``
* Push: ``git push origin pypi``
* Run homebrew release script to send PR to homebrew-core:
  ``./release_homebrew.sh https://files.pythonhosted.org/packages/8c/41/b08e2883c256d52f63f00f622cf8a33d3bf36bb5714af337e67476f8b3fe/doitlive-x.y.z.tar.gz``
