# Contributing

## Setting up for development

* Create and activate a new virtual environment
* `pip install -e '.[dev]'`
* (Optional but recommended) If you're using a Python 3.6 virtual
    environment, install the pre-commit hooks, which will
    format and lint your git staged files:


```
# The pre-commit CLI was installed above
pre-commit install
```

* To run tests:

```
pytest
```

* To run syntax checks:

```
tox -e lint
```

* To build the docs:

```
tox -e watch-docs
```

* (Optional) To run tests on Python 2.7, 3.5, 3.6, and 3.7 virtual environments (must have each interpreter installed):

```
tox
```
