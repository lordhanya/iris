# IRIS — SDDM PAM Integration Guide

## ⚠️ CRITICAL SAFETY RULES ⚠️

1. **NEVER use `required`** — always use `sufficient`. With `sufficient`, IRIS face auth is tried first, but if it fails, the password prompt still works.
2. **Always backup** before editing PAM files.
3. **Keep the backup** — if you get locked out, restore it.
4. **Emergency disable** works even if the PAM script crashes → use `touch /tmp/face-auth-emergency-disable`

## Quick Install (Recommended)

```bash
sudo ./scripts/install-pam.sh
```

This does everything: backup, install, and prints failsafe instructions.

## Manual Install

```bash
# Backup first
sudo cp /etc/pam.d/sddm /etc/pam.d/sddm.backup

# Add IRIS as first auth method (BEFORE system-login)
sudo nano /etc/pam.d/sddm
```

Add this line **before** `auth include system-login`:
```
auth sufficient pam_exec.so quiet /home/ashif_dev/Desktop/face-auth-system/scripts/face_auth.sh
```

Result should look like:
```
#%PAM-1.0
auth        sufficient   pam_exec.so quiet /home/ashif_dev/Desktop/face-auth-system/scripts/face_auth.sh
auth        include      system-login
...
```

## Remove / Uninstall

```bash
sudo ./scripts/uninstall-pam.sh
```

## Emergency Disable (No Password Needed)

If IRIS face auth is broken and you need password-only login immediately:

```bash
# Quick disable (creates a flag file):
~/Desktop/face-auth-system/scripts/emergency-disable.sh

# Or disable via config:
~/Desktop/face-auth-system/scripts/toggle-disable.sh

# To re-enable:
rm /tmp/face-auth-emergency-disable
```

## If Locked Out Completely

1. Switch to TTY: `Ctrl+Alt+F3`
2. Login with your username and password
3. Restore PAM backup: `sudo cp /etc/pam.d/sddm.backup /etc/pam.d/sddm`
4. Switch back: `Ctrl+Alt+F1` (or F7)

## Testing (Without Locking Yourself Out)

```bash
# Test face auth directly (safe - doesn't affect PAM):
python ~/Desktop/face-auth-system/cli/auth.py

# Test PAM script (safe - just checks exit code):
~/Desktop/face-auth-system/scripts/face_auth.sh

# Manual unlock (after screen is locked):
~/Desktop/face-auth-system/scripts/screen_unlock.sh
```

## IR Emitter Setup

The T470 IR camera needs the IR illuminator turned on via a proprietary UVC control. Install and configure:

```bash
# One-time setup (already done if auth works):
sudo /home/ashif_dev/Desktop/face-auth-system/linux-enable-ir-emitter -d /dev/video0 configure

# Enable automatic startup at boot and after resume:
sudo systemctl enable --now linux-enable-ir-emitter
```

The `face_auth.sh` script also calls the emitter tool as a fallback before each auth attempt.

## How It Works

| Layer | Mechanism |
|-------|-----------|
| **Timeout** | `timeout --kill-after=2` prevents hanging |
| **PAM flag** | `sufficient` = try face first, fallback to password |
| **Emergency** | Flag file `/tmp/face-auth-emergency-disable` |
| **Config** | `disabled = true` in config.ini |
| **Environment** | Lid close + SSH detection abort face auth |
| **Logging** | All attempts logged to `logs/pam_auth.log` and syslog |