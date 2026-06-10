#!/bin/bash
# Re-enable face auth after emergency disable
FLAG="/tmp/face-auth-emergency-disable"
if [ -f "$FLAG" ]; then
    rm "$FLAG"
    echo "Face auth RE-ENABLED"
else
    echo "Face auth was not disabled. Nothing to do."
fi
