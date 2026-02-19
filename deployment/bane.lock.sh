#!/bin/bash
# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# BANE Core Locking Script
# Inspired by BANE DOCUMENTATION FINAL PHASE 1.1 REFACTORING.pdf

echo "🔐 BANE Phase 1.1: Final Hardening"

# 1. Create dedicated system user
echo "👤 Creating dedicated system user 'bane'..."
sudo useradd -r -s /usr/sbin/nologin bane || echo "User 'bane' already exists."

# 2. Define Paths
BANE_CORE="/home/son/BANE"
BANE_WORKSPACES="/home/son/BANE_Workspaces"

# 3. Ownership and Permissions for Core
echo "🛡️  Locking BANE Core (read-only)..."
sudo chown -R root:root "$BANE_CORE"
sudo chmod -R 755 "$BANE_CORE"
sudo chmod -R a-w "$BANE_CORE"

# Allow specific core subdirectories to be writable by root (for maintenance)
# and ensure log/storage dirs are accessible if needed.
# However, the security policy says storage should be in ALLOWED_PATHS.
sudo chmod -R 777 "$BANE_CORE/storage" # Ensure storage is writable for the app
sudo chown -R bane:bane "$BANE_CORE/storage"
sudo chmod -R 777 "$BANE_CORE/Debug"
sudo chown -R bane:bane "$BANE_CORE/Debug"

# 4. Workspace Access Control
echo "📂 Setting up Workspace access for 'bane' user..."
sudo chown -R son:son "$BANE_WORKSPACES" # User 'son' owns workspaces
sudo chmod -R 775 "$BANE_WORKSPACES"
# Give bane user read-execute access to workspaces via ACL
sudo setfacl -R -m u:bane:rx "$BANE_WORKSPACES"

# 5. GUI Access (Crucial for Antigravity bridge)
echo "🖥️  Configuring GUI access for 'bane' user..."
sudo setfacl -m u:bane:r /home/son/.Xauthority
sudo setfacl -R -m u:bane:rwx /run/user/1000

# 6. Systemd Service Update
echo "🔄 Updating systemd service..."
SERVICE_FILE="/home/son/BANE/bane.service"
sudo sed -i 's/User=son/User=bane/' "$SERVICE_FILE"
sudo sed -i 's/Group=son/Group=bane/' "$SERVICE_FILE" || echo "Group already correct or not found."

echo "✅ Hardening complete!"
echo "🚀 Run 'sudo systemctl daemon-reload && sudo systemctl restart bane' to apply."
