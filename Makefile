API_VERSIONS = v1 v2
SERVER_URL = http://127.0.0.1:8000
SPEC_PATH = specs

.PHONY: test run test-api test-all $(API_VERSIONS)

run:
	@echo "Current virtualenv: $(VIRTUAL_ENV)"
	@echo "Is guardrails-ai dependency installed? $(shell pip3 list | grep guardrails-ai)"
	@uvicorn src.app:app --reload

install:
	pip3 install -r requirements.txt

upgrade-dependencies:
	./src/scripts/upgrade-dependencies.sh

lint:
	python3 -m pylint src

test-all: lint test test-api

test:
	python3 -m unittest discover

test-api: $(API_VERSIONS)

$(API_VERSIONS):
	-python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$@/openapi.json --spec-file $(SPEC_PATH)/openapi-$@.json

test-api-%:
	python3 src/scripts/run_api_spec_validator.py --server-url $(SERVER_URL)/$*/openapi.json --spec-file $(SPEC_PATH)/openapi-$*.json
