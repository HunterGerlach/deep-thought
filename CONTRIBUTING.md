# Deep Thought Contributing Guide

Documentation for contributing to Deep Thought.

## Install Poetry

Setup local Python environment for Deep Thought using Poetry for dependency management.

It is assumed that you have already installed Poetry on your local machine. If not, please follow the instructions [here](https://python-poetry.org/docs/#installation).

```bash
poetry install # initial installation of dependencies
poetry shell # activate the virtual environment
export PYTHONPATH=$(pwd) # add the current directory to the PYTHONPATH
```

### Update dependencies

```bash
poetry update # update dependencies
```

### Add a new dependency

```bash
poetry add <package-name> # add a new dependency
```

### Remove a dependency

```bash
poetry remove <package-name> # remove a dependency
```

## Common Developer Tasks

Most of these tasks are automated in the Makefile that lives in the root of the project.

### Run the code

```bash
make run # which runs: uvicorn src.app:app --reload
```

### Lint the code

```bash
make lint # which runs: pylint src
```

### Run the unit tests

```bash
make test # which runs: python -m unittest discover
```

### Run the API spec validation tests

```bash
make test-api # which runs a custom script that validates the API spec for all available versions
```

### Run the API spec validation tests for a specific version

```bash
make v1 # which runs a custom script that validates the API spec for version 1
# or
make v2 # which runs a custom script that validates the API spec for version 2
```

### Run ALL available tests

```bash
make test-all # which runs: make lint, make test, and make test-api
```

### Update all dependencies

```bash
make update # which runs a script that updates all dependencies
```

### To see the dependencies that need to be updated

```bash
pip list --outdated
```

## API Details

Information about the API can be found in the [API documentation](API.md).
