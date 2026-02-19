#!/bin/bash
# BANE Sandbox Launcher
# Uses bubblewrap to run scripts in a hardened, isolated environment.

if [ "$#" -ne 1 ]; then
    echo "Usage: ./sandbox_run.sh <script.py>"
    exit 1
fi

SCRIPT_PATH=$(realpath "$1")
SANDBOX_DIR=$(dirname "$SCRIPT_PATH")

echo "--- 🛡️ LAUNCHING IN HARDENED SANDBOX ---"

bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --proc /proc \
  --dev /dev \
  --unshare-net \
  --dir /tmp \
  --bind "$SANDBOX_DIR" /sandbox \
  --chdir /sandbox \
  python3 "$(basename "$SCRIPT_PATH")"

echo "--- 🛡️ SANDBOX CLOSED ---"
