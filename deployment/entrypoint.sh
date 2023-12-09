#!/bin/sh

set -e

VENV_PATH=$(find /app/.venv -name 'activate' | grep -m 1 'bin/activate')
source $VENV_PATH

export PYTHONPATH=$(pwd)

uvicorn src.app:app --host 0.0.0.0 --port 8000
