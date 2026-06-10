#!/bin/bash
# PAM-compatible face authentication script for IRIS
# Called by pam_exec.so with "sufficient" control flag
# On failure (exit 1), PAM falls through to password prompt

SCRIPT_DIR="/home/ashif_dev/Desktop/face-auth-system"
VENV_DIR="$SCRIPT_DIR/venv"
AUTH_SCRIPT="$SCRIPT_DIR/cli/auth.py"
LOG_FILE="$SCRIPT_DIR/logs/pam_auth.log"
EMERGENCY_FLAG="/tmp/face-auth-emergency-disable"
TIMEOUT=8

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Emergency disable check - create /tmp/face-auth-emergency-disable to bypass
if [ -f "$EMERGENCY_FLAG" ]; then
    echo "$TIMESTAMP - SKIPPED: emergency disable flag present" >> "$LOG_FILE"
    exit 1
fi

# Ensure IR emitter is on (PAM runs as root, so this works)
IR_TOOL="$SCRIPT_DIR/linux-enable-ir-emitter"
if [ -x "$IR_TOOL" ]; then
    "$IR_TOOL" --verbose run 2>> "$LOG_FILE" &
fi

# Pre-flight checks - fail fast to avoid hanging PAM
if [ ! -f "$AUTH_SCRIPT" ]; then
    echo "$TIMESTAMP - ERROR: auth.py not found" >> "$LOG_FILE"
    exit 1
fi

# Activate venv if present (dev setups), otherwise use system Python
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

cd "$SCRIPT_DIR" || exit 1

# Use timeout to prevent PAM hanging forever
# --kill-after=2 ensures processes are killed even if they ignore SIGTERM
timeout --kill-after=2 "$TIMEOUT" python3 "$AUTH_SCRIPT" "$@"
RESULT=$?

echo "$TIMESTAMP - RESULT: $RESULT" >> "$LOG_FILE"

exit $RESULT