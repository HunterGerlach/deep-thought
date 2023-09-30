API_VERSIONS = v1 v2
SERVER_URL = http://127.0.0.1:8000
SPEC_PATH = specs

.PHONY: test run test-api test-all $(API_VERSIONS)

venv/bin/activate: requirements-devel.txt
	python3 -m venv venv
	. venv/bin/activate
	pip install --upgrade pip setuptools wheel
	pip install -r requirements-devel.txt
	poetry install

clean-prereqs:
	rm -rf venv
.PHONY: clean-prereqs

prereqs: venv/bin/activate
# ifndef VIRTUAL_ENV
# 	$(error run: . venv/bin/activate)
# endif
.PHONY: prereqs

lint: prereqs
	. venv/bin/activate
	yamllint .
	black .
	poetry run pylint src
.PHONY: prereqs lint

run:
	@echo "Current virtualenv: $(VIRTUAL_ENV)"
	@uvicorn src.app:app --reload

install:
	poetry install

upgrade-dependencies:
	./src/scripts/upgrade-dependencies.sh

test-all: lint test test-api

test:
	poetry run pytest

test-api: $(API_VERSIONS)

$(API_VERSIONS):
	-poetry run python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$@/openapi.json --spec-file $(SPEC_PATH)/openapi-$@.json

test-api-%:
	poetry run python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$*/openapi.json --spec-file $(SPEC_PATH)/openapi-$*.json
