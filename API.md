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
