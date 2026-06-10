#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
AUTH_SCRIPT="$PROJECT_DIR/cli/auth.py"

if [ ! -f "$AUTH_SCRIPT" ]; then
    echo "Error: auth.py not found"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: virtual environment not found"
    exit 1
fi

source "$VENV_DIR/bin/activate"

python "$AUTH_SCRIPT" "$@"
exit_code=$?

exit $exit_code