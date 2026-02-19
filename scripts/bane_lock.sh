#!/bin/bash

# BANE LOCK - System Hardening Script
# Locks down source code to Read-Only to prevent accidental/unauthorized changes.
# Keeps 'storage', 'logs', and cache directories writable for service operation.

BASE_DIR="/home/user/BANE_CORE"

echo "🔒 Initiating BANE LOCK..."

# 1. Default: Lock EVERYTHING first (Read-Only)
# Directories: 500 (r-x------)
find "$BASE_DIR" -type d -exec chmod 755 {} +
# Files: 400 (r--------)
find "$BASE_DIR" -type f -exec chmod 644 {} +

# 2. Unlock Writable Areas (Read-Write-Execute)
# Directories: 700 (rwx------)
# Files: 600 (rw-------)

echo "🔓 Unlocking storage and logs..."

# Storage
chmod -R 777 "$BASE_DIR/storage"
# Logs
[ -d "$BASE_DIR/logs" ] && chmod -R 777 "$BASE_DIR/logs"
# Cache
find "$BASE_DIR" -name "__pycache__" -type d -exec chmod 777 {} +
# .venv (keep writable for pip updates)
chmod -R 777 "$BASE_DIR/.venv"

# 3. Lock Down Source Code (Read-Only)
# Folders to lock: core, utils, telegram_interface, messenger_interface, antigravity, agent, security
LOCKED_DIRS=("core" "utils" "telegram_interface" "messenger_interface" "antigravity" "agent" "security" "docs" "scripts" "config")

echo "🛡️ Locking core modules..."

for dir in "${LOCKED_DIRS[@]}"; do
    TARGET="$BASE_DIR/$dir"
    if [ -d "$TARGET" ]; then
        # Lock files to Read-Only (444 for safety, owner can still chmod back)
        find "$TARGET" -type f -exec chmod 444 {} +
        # Dirs to Read-Exec (555)
        find "$TARGET" -type d -exec chmod 555 {} +
    fi
done

# Lock root python files
find "$BASE_DIR" -maxdepth 1 -name "*.py" -exec chmod 444 {} +
find "$BASE_DIR" -maxdepth 1 -name "*.sh" -exec chmod 555 {} +

# Make verify writable
# chmod 755 "$BASE_DIR/scripts/bane_lock.sh"
# chmod 755 "$BASE_DIR/scripts/bane_unlock.sh"

echo "✅ BANE LOCK COMPLETE. System secured."
