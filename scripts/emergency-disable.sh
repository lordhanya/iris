#!/bin/bash
# Emergency disable - creates a flag that bypasses face auth immediately
# Safe to run anytime, no root needed
FLAG="/tmp/face-auth-emergency-disable"
touch "$FLAG"
echo "IRIS FACE AUTH DISABLED (emergency)"
echo "To re-enable: rm $FLAG"
echo ""
echo "Your password is still working. Face auth is now skipped."
