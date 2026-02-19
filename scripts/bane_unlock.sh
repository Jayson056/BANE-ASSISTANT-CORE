#!/bin/bash

# BANE UNLOCK - Restore Permissions
# Unlocks all files for editing/updates.

BASE_DIR="/home/user/BANE_CORE"

echo "🔓 Initiating BANE UNLOCK..."

# 1. Restore Default Permissions (Read-Write-Exec for owner)
# Directories: 755 (rwxr-xr-x)
# Files: 644 (rw-r--r--)

find "$BASE_DIR" -type d -exec chmod 755 {} +
find "$BASE_DIR" -type f -exec chmod 644 {} +

# Logs and Storage should already be open, no change needed.

echo "✅ BANE UNLOCKED. Permissions restored."
