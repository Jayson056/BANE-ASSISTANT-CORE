#!/bin/bash
# CLAWBOLT - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# CLAWBOLT System Refactoring Script
# This script implements the Phase 1.1 Refactoring based on the documentation.
# WARNING: This script requires sudo privileges.

set -e

CLAWBOLT_SRC="/home/user/BANE_CORE"
CLAWBOLT_DEST="/opt/bane"
WORKSPACE_DIR="/home/user/BANE_CORE/Projects" # Current workspace location
SERVICE_USER="bane"

echo "🚀 Starting CLAWBOLT Refactoring..."

# 1. Ensure target directory exists
if [ ! -d "$CLAWBOLT_DEST" ]; then
    echo "📂 Creating $CLAWBOLT_DEST..."
    sudo mkdir -p "$CLAWBOLT_DEST"
fi

# 2. Copy files to /opt/clawbolt
echo "📦 Copying files to $CLAWBOLT_DEST..."
sudo cp -r "$CLAWBOLT_SRC/." "$CLAWBOLT_DEST/"

# 3. Create dedicated system user if not exists
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "👤 Creating system user: $SERVICE_USER..."
    sudo useradd -r -s /usr/sbin/nologin "$SERVICE_USER"
fi

# 4. Set Workspace Permissions (ACLs)
echo "🛡️ Setting Workspace ACLs..."
sudo apt-get update && sudo apt-get install -y acl
sudo setfacl -R -m u:$SERVICE_USER:rx "$WORKSPACE_DIR"
# Allow writing to specific projects if needed (add as necessary)
# sudo setfacl -R -m u:$SERVICE_USER:rwx "$WORKSPACE_DIR/some_project"

# 5. Lock CLAWBOLT Core (Read-Only)
echo "🔒 Locking CLAWBOLT Core..."
sudo chown -R root:root "$CLAWBOLT_DEST"
sudo chmod -R 755 "$CLAWBOLT_DEST"
# Note: Keep storage/ writable for logs and screenshots if they are inside /opt
# Better yet, move storage to a mutable location like /var/lib/clawbolt
STORAGE_DIR="/var/lib/clawbolt"
sudo mkdir -p "$STORAGE_DIR"
sudo chown -R $SERVICE_USER:$SERVICE_USER "$STORAGE_DIR"
# Link storage inside /opt for compatibility (if code expects it there)
# sudo ln -s "$STORAGE_DIR" "$CLAWBOLT_DEST/storage"

# 6. Update Systemd Service
echo "⚙️ Updating systemd service..."
SERVICE_FILE="/etc/systemd/system/clawbolt.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=CLAWBOLT Control Agent
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$CLAWBOLT_DEST

# Use the virtual environment Python
ExecStart=$CLAWBOLT_DEST/.venv/bin/python3 $CLAWBOLT_DEST/main.py

# Restart on failure/crash
Restart=always
RestartSec=5

# Backend runs headless - no GUI dependencies needed at this layer
Environment="PYTHONUNBUFFERED=1"
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/son/.Xauthority"
Environment="XDG_RUNTIME_DIR=/run/user/1000"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "✅ Refactoring complete! Run 'sudo systemctl restart clawbolt' to apply changes."
echo "⚠️  Note: You are currently running from $CLAWBOLT_SRC. The system service will soon use $CLAWBOLT_DEST."
