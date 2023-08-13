# Deep Thought API

The Deep Thought API is a REST API that provides access to the Deep Thought.

## Endpoint Details

### Find Sources

Description: Find sources for a given query

#### Hitting the endpoint

With curl:

```bash
curl    -X POST \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the capital of France?", "sources": ["wikipedia", "freebase", "dbpedia"]}' http://localhost:5000/find_sources
```

With Postman:

```bash
POST http://localhost:5000/find_sources
```

### LLM Fact

Description: Find the most likely fact for a given query

#### Hitting the endpoint

With curl:

```bash
curl    -X POST \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the capital of France?", "sources": ["wikipedia", "freebase", "dbpedia"]}' \
        http://localhost:5000/llm_fact
```

With Postman:

```bash
POST http://localhost:5000/llm_fact
```

### LLM Fact with context

Description: Find the most likely fact for a given query and context

#### Hitting the endpoint

With curl:

```bash
curl    -X POST \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the capital of France?", "sources": ["wikipedia", "freebase", "dbpedia"]}' \
        http://localhost:5000/ask
```

With Postman:

```bash
POST http://localhost:5000/ask
```

## OpenAPI (Swagger) Specification

The API is documented using OpenAPI. The OpenAPI UI can be accessed at `/docs`.

The OpenAPI specification can be found at `/spec`.

The OpenAPI spec is defined in `/spec/openapi.json' and is to be regarded as the source of truth for the API.
Both API developers and consumers should refer to this file for the API definition. Developers should update this file
prior to making changes to the API, keeping in mind that the API is versioned.

### Versioning

The API is versioned and endpoints will always be available under the version number (e.g. `/v1/`).

This API follows [Semantic Versioning](https://semver.org/), but only the major version number is included in the URL. Minor and patch versions can be found in the OpenAPI spec.
