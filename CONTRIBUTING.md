## Setup

Setup local Python environment

```bash
poetry install
poetry shell
export PYTHONPATH=$(pwd)
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
