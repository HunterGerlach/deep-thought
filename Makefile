API_VERSIONS = v1 v2

.PHONY: test run test-api test-all $(API_VERSIONS)

run:
	uvicorn src.app:app --reload

lint:
	python3 -m pylint src

test-all: lint test test-api

test:
	python3 -m unittest discover

test-api: $(API_VERSIONS)

$(API_VERSIONS):
	-python3 src/scripts/run_api_spec_validator.py --server-url http://127.0.0.1:8000/$@/openapi.json --spec-file specs/openapi-$@.json

test-api-%:
	python3 src/scripts/run_api_spec_validator.py --server-url http://127.0.0.1:8000/$*/openapi.json --spec-file specs/openapi-$*.json
