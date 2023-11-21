API_VERSIONS = v1 v2
SERVER_URL = http://0.0.0.0:8000
SPEC_PATH = specs

.PHONY: test run test-api test-all $(API_VERSIONS)

run:
	@echo "Current virtualenv: $(VIRTUAL_ENV)"
	@poetry run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

install:
	poetry install

upgrade-dependencies:
	./src/scripts/upgrade-dependencies.sh

lint:
	poetry run pylint src

test-all: lint test test-api

test:
	poetry run pytest

test-api: $(API_VERSIONS)

$(API_VERSIONS):
	-poetry run python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$@/openapi.json --spec-file $(SPEC_PATH)/openapi-$@.json

test-api-%:
	poetry run python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$*/openapi.json --spec-file $(SPEC_PATH)/openapi-$*.json
