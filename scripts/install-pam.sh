#!/bin/bash
# SAFE PAM integration for SDDM
# Creates a backup and adds face auth BEFORE password (sufficient)
# If something goes wrong: sudo cp /etc/pam.d/sddm.backup /etc/pam.d/sddm

set -e

PAM_FILE="/etc/pam.d/sddm"
BACKUP_FILE="/etc/pam.d/sddm.backup"
USER_HOME="/home/ashif_dev"
AUTH_SCRIPT="$USER_HOME/Desktop/face-auth-system/scripts/face_auth.sh"

echo "=== SDDM Face Auth Installer ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run with sudo"
    echo "  sudo $0"
    exit 1
fi

# Check if PAM file exists
if [ ! -f "$PAM_FILE" ]; then
    echo "ERROR: $PAM_FILE not found. Is SDDM installed?"
    exit 1
fi

# Check if already installed
if grep -q "face_auth.sh" "$PAM_FILE" 2>/dev/null; then
    echo "Face auth is already installed in $PAM_FILE"
    echo "Run uninstall-pam.sh first if you want to reinstall."
    exit 0
fi

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp "$PAM_FILE" "$BACKUP_FILE"
echo "✅ Backup saved"

# Add face auth line BEFORE the first 'auth' line (runs before password check)
echo "Adding face auth to $PAM_FILE..."
sed -i '0,/^auth/s|^auth|auth sufficient pam_exec.so quiet '"$AUTH_SCRIPT"'\n&|' "$PAM_FILE"

echo "✅ Face auth installed successfully!"
echo ""
echo "What was done:"
echo "  - Backed up $PAM_FILE to $BACKUP_FILE"
echo "  - Added: auth sufficient pam_exec.so quiet $AUTH_SCRIPT"
echo "  - Face auth runs BEFORE password"
echo "  - If face fails, password still works"
echo ""
echo "=== TESTING ==="
echo "Run this to test (without locking yourself out):"
echo "  $AUTH_SCRIPT"
echo ""
echo "=== FAILSAFE ==="
echo "If locked out: Ctrl+Alt+F3, login, then:"
echo "  sudo cp $BACKUP_FILE $PAM_FILE"
echo "Or just disable face auth temporarily:" 
echo "  $USER_HOME/Desktop/face-auth-system/scripts/emergency-disable.sh"
