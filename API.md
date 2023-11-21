# Deep Thought API

The Deep Thought API is a REST API that provides access to the Deep Thought.

## Endpoint Details

Endpoint specifications are defined in the OpenAPI spec. Each version of the API has its own spec. The specs can be found in the `/specs` directory.

- [v1](./specs/openapi-v1.json)
- [v2](./specs/openapi-v2.json)

### Find Sources

Description: Find sources for a given query

#### Hitting the endpoint

With curl:

```bash
curl -X 'POST' 'http://0.0.0.0:8000/v1/find_sources' -H 'Content-Type: application/json' -d '{"query": "test_query", "num_results": 2}'
```

<!-- With Postman:

```bash
POST http://localhost:5000/find_sources
``` -->

### LLM Fact

Description: Find the most likely fact for a given query

#### Hitting the endpoint

With curl:

```bash
curl -X 'POST' 'http://0.0.0.0:8000/v1/' -H 'Content-Type: application/json' -d '{"user_input": "whats for dinner"}'
```

<!-- With Postman:

```bash
POST http://localhost:5000/llm_fact
``` -->

### Ask Endpoint

Description: Ask a question and get an answer with links to sources

#### Hitting the endpoint

With curl:

```bash
curl -X 'POST' 'http://0.0.0.0:8000/v1/ask' -H 'Content-Type: application/json' -d '{"query": "step by step instructions to install a new operator", "num_results": 1}'
```

<!-- With Postman:

```bash
POST http://localhost:8000/v1/synthesize_response
``` -->

## OpenAPI (Swagger) Specification

The API is documented using OpenAPI. The OpenAPI UI can be accessed at `/docs`.

The OpenAPI specification can be found at `/spec`.

The OpenAPI spec is defined in `/spec/openapi.json' and is to be regarded as the source of truth for the API.
Both API developers and consumers should refer to this file for the API definition. Developers should update this file
prior to making changes to the API, keeping in mind that the API is versioned.

## Versioning

The API is versioned and endpoints will always be available under the version number (e.g. `/v1/`).

This API follows [Semantic Versioning](https://semver.org/), but only the major version number is included in the URL. Minor and patch versions can be found in the OpenAPI spec.

#### Testing Versioning

To test versioning, you can hit two separate endpoints:

```bash
curl -X 'GET' 'http://0.0.0.0:8000/v1/items/' -H 'Content-Type: application/json' -d '{"query": "test_query", "num_results": 2}'
```

Which should return:

```json
[
  {
    "version": "V1"
  }
]
```

And then:

```bash
curl -X 'GET' 'http://0.0.0.0:8000/v2/api_version_test/' -H 'Content-Type: application/json' -d '{"query": "test_query", "num_results": 2}'
```

Which should return:

```json
[
  {
    "version": "V2"
  }
]
```
