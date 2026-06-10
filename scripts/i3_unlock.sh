#!/bin/bash

PROJECT_DIR="$HOME/Desktop/face-auth-system"
LOCK_FILE="/tmp/i3lock_active"

if [ -f "$LOCK_FILE" ]; then
    echo "Screen is locked - attempting unlock"
    
    source "$PROJECT_DIR/venv/bin/activate"
    
    python "$PROJECT_DIR/cli/auth.py"
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        rm -f "$LOCK_FILE"
        echo "Unlocked!"
        exit 0
    else
        echo "Auth failed - screen remains locked"
        exit 1
    fi
else
    echo "Locking screen..."
    touch "$LOCK_FILE"
    loginctl lock-session
    exit 0
fi