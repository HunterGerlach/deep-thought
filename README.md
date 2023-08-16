# deep-thought

## Setup instructions

Setup local Python environment

```bash
python3 -m venv .venv_deep-thought
source .venv_deep-thought/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
```

Installs the following (along with dependencies):

- httpx (for unit testing)
- openai
- pgvector
- psycopg2-binary
- sentence_transformers

Create .env.config, .env.secrets from .env.config.example, .env.secrets.example under /src. The MODEL_PROVIDER config variable can be changed as per requirement
Create spend.log empty file under deep-thought

## Run the code

```bash
uvicorn src.app:app --reload
```

## Run the tests

```bash
python -m unittest discover
```

## API Details

Information about the API can be found in the [API documentation](API.md).

## Deployment to OpenShift

Add the following to the `spec` section of the `Deployment` resource:

```yaml
spec:
    template:
        spec:
            containers:
                env:
                    - name: APP_FILE
                    value: src/app.py
                    - name: PYTHONPATH
                    value: /
```
