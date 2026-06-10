#!/bin/bash

PROJECT_DIR="$HOME/Desktop/face-auth-system"

echo "Attempting face unlock..."

source "$PROJECT_DIR/venv/bin/activate"

python "$PROJECT_DIR/cli/auth.py"
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "Face authenticated! Unlocking screen..."
    loginctl unlock-session
else
    echo "Face auth failed - keeping screen locked"
    exit 1
fi