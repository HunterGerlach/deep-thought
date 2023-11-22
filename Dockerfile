ARG POETRY_VERSION=1.7.1

FROM registry.access.redhat.com/ubi8/python-311:1-35 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

FROM base as builder

ARG POETRY_VERSION

USER root
WORKDIR /app

ENV YOUR_ENV=${YOUR_ENV} \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.path "/app/.venv" && \
    poetry install --no-interaction --no-ansi --no-root --verbose

COPY . /app

USER 1001

FROM base as final

COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY entrypoint.sh .

CMD ["./entrypoint.sh"]


# Local build command
# podman build -t deep-thought:latest -f Dockerfile .

# Local run command
# podman run -it --rm -p 8000:8000 deep-thought:latest
