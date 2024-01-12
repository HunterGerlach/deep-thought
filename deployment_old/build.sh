#!/bin/bash

# Exit in case of error
set -e

APP_MODULE="src.app:app"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Poetry could not be found, please install it first"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
#poetry install

# Run application
echo "Starting Deep Thought..."
#uvicorn $APP_MODULE --host 0.0.0.0 --port 8000
