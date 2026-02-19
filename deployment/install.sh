#!/bin/bash
# CLAWBOLT - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
set -e

echo "🦅 Installing CLAWBOLT..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (use sudo)"
  exit 1
fi

# Determine script location and set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_SRC="$SCRIPT_DIR/clawbolt.service"
SUDOERS_SRC="$SCRIPT_DIR/clawbolt_sudoers"
AUTOSTART_SRC="$SCRIPT_DIR/antigravity.desktop"

SERVICE_DEST="/etc/systemd/system/clawbolt.service"
SUDOERS_DEST="/etc/sudoers.d/clawbolt"

if [ -f "$SERVICE_SRC" ]; then
    echo "Installing service to $SERVICE_DEST..."
    cp "$SERVICE_SRC" "$SERVICE_DEST"
    chmod 644 "$SERVICE_DEST"
else
    echo "Error: $SERVICE_SRC not found!"
    exit 1
fi

if [ -f "$SUDOERS_SRC" ]; then
    echo "Installing sudoers to $SUDOERS_DEST..."
    cp "$SUDOERS_SRC" "$SUDOERS_DEST"
    chmod 440 "$SUDOERS_DEST"
else
    echo "Warning: $SUDOERS_SRC not found, skipping sudoers install."
fi

# Install user autostart for Antigravity (as the actual user, not root)
if [ -f "$AUTOSTART_SRC" ]; then
    REAL_USER="${SUDO_USER:-$USER}"
    AUTOSTART_DEST="/home/$REAL_USER/.config/autostart/antigravity.desktop"
    echo "Installing Antigravity autostart to $AUTOSTART_DEST..."
    mkdir -p "/home/$REAL_USER/.config/autostart"
    cp "$AUTOSTART_SRC" "$AUTOSTART_DEST"
    chown "$REAL_USER:$REAL_USER" "$AUTOSTART_DEST"
    chmod 644 "$AUTOSTART_DEST"
fi

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling clawbolt service..."
systemctl enable clawbolt

echo "Starting clawbolt service..."
systemctl start clawbolt

echo "✅ CLAWBOLT Installed Successfully!"
echo ""
echo "📋 Post-Install:"
echo "  - CLAWBOLT backend: systemctl status clawbolt"
echo "  - Antigravity will auto-launch on next login"
echo "  - Test with: Reboot and check Telegram"
