#!/bin/bash
# Remove face auth from SDDM PAM config
# Restores the original backup if available

set -e

PAM_FILE="/etc/pam.d/sddm"
BACKUP_FILE="/etc/pam.d/sddm.backup"

if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run with sudo"
    echo "  sudo $0"
    exit 1
fi

if [ -f "$BACKUP_FILE" ]; then
    echo "Restoring from backup: $BACKUP_FILE"
    cp "$BACKUP_FILE" "$PAM_FILE"
    echo "✅ Restored original PAM config from backup"
elif [ -f "$PAM_FILE" ]; then
    echo "No backup found. Removing face auth line from $PAM_FILE..."
    sed -i '/face_auth.sh/d' "$PAM_FILE"
    echo "✅ Removed face auth line"
else
    echo "ERROR: $PAM_FILE not found"
    exit 1
fi

echo ""
echo "Face auth has been removed from SDDM."
echo "Password login still works."
