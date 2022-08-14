# Contributing

## Setting up for development

- Create and activate a new virtual environment
- `pip install -e '.[dev]'`
- (Optional but recommended) Install the pre-commit hooks, which will
  format and lint your git staged files:

```
# The pre-commit CLI was installed above
pre-commit install
```

- To run tests:

```
pytest
```

- To run syntax checks:

```
tox -e lint
```

- To build the docs:

```
tox -e watch-docs
```

- (Optional) To run tests on all suported versions (must have each interpreter installed):

```
tox
```
