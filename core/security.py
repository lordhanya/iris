import os
import glob
import logging

from core.logger import get_logger
log = get_logger(__name__)


def is_lid_closed():
    try:
        for path in glob.glob("/proc/acpi/button/lid/*/state"):
            with open(path) as f:
                state = f.read().strip()
            if "closed" in state:
                return True
    except Exception as e:
        log.debug(f"Could not read lid state: {e}")
    return False


def is_ssh_session():
    for env_var in ["SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY", "SSHD_OPTS"]:
        if os.environ.get(env_var):
            return True
    return False


def check_environment():
    checks = []

    if is_ssh_session():
        checks.append(("SSH", "SSH session detected, skipping face auth"))

    if is_lid_closed():
        checks.append(("LID", "Lid is closed, skipping face auth"))

    return checks
