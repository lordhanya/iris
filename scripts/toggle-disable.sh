#!/bin/bash
# Toggle IRIS face auth on/off by modifying config.ini
# Safe to run anytime, requires write access to config.ini

CONFIG="$HOME/Desktop/face-auth-system/config.ini"

if [ ! -f "$CONFIG" ]; then
    echo "Error: config.ini not found at $CONFIG"
    exit 1
fi

CURRENT=$(grep -c "^disabled = true" "$CONFIG")

if [ "$CURRENT" -gt 0 ]; then
    sed -i 's/^disabled = true/disabled = false/' "$CONFIG"
    echo "✅ Face auth ENABLED"
else
    sed -i 's/^disabled = false/disabled = true/' "$CONFIG"
    echo "✅ Face auth DISABLED"
    echo ""
    echo "Your password login still works."
    echo "Run this script again to re-enable."
fi
