#!/bin/bash
# ═══════════════════════════════════════════════════
# CLAWBOLT - Messenger Gateway Deployment Script
# Phase 4: Robust Hosting
# ═══════════════════════════════════════════════════
set -e

DEPLOY_DIR="/home/user/BANE_CORE/deployment"
VENV="/home/user/BANE_CORE/.venv"
SECRETS="/home/user/BANE_CORE/config/secrets.env"
LOG_DIR="/home/user/BANE_CORE/Debug/Console"

echo "═══════════════════════════════════════════════"
echo "  BANE Messenger Gateway - Deployment"
echo "═══════════════════════════════════════════════"
echo ""

# --- Pre-flight Checks ---
echo "[1/6] Running pre-flight checks..."

# Check virtual environment
if [ ! -f "$VENV/bin/python3" ]; then
    echo "  ❌ Virtual environment not found at $VENV"
    exit 1
fi
echo "  ✅ Virtual environment OK"

# Check secrets file
if [ ! -f "$SECRETS" ]; then
    echo "  ❌ Secrets file not found at $SECRETS"
    exit 1
fi

# Verify Messenger tokens are configured
if grep -q "YOUR_PAGE_ACCESS_TOKEN" "$SECRETS" 2>/dev/null; then
    echo "  ⚠️  WARNING: MESSENGER_PAGE_ACCESS_TOKEN is still placeholder!"
    echo "     Edit $SECRETS before going live."
fi
if grep -q "YOUR_CHOSEN_VERIFY_TOKEN" "$SECRETS" 2>/dev/null; then
    echo "  ⚠️  WARNING: MESSENGER_VERIFY_TOKEN is still placeholder!"
    echo "     Edit $SECRETS before going live."
fi
echo "  ✅ Secrets file exists"

# Check Flask app
if [ ! -f "/home/user/BANE_CORE/messenger_interface/app.py" ]; then
    echo "  ❌ Messenger app.py not found"
    exit 1
fi
echo "  ✅ Messenger app.py OK"

# --- Install Dependencies ---
echo ""
echo "[2/6] Checking Python dependencies..."
"$VENV/bin/pip" install --quiet gunicorn flask python-dotenv requests 2>/dev/null
echo "  ✅ Dependencies installed"

# --- Create Log Directory ---
echo ""
echo "[3/6] Preparing log directory..."
mkdir -p "$LOG_DIR"
echo "  ✅ Log directory ready: $LOG_DIR"

# --- Install Systemd Services ---
echo ""
echo "[4/6] Installing systemd services..."

# Copy service files
sudo cp "$DEPLOY_DIR/clawbolt-messenger.service" /etc/systemd/system/
sudo cp "$DEPLOY_DIR/clawbolt-messenger-health.service" /etc/systemd/system/
echo "  ✅ Service files copied"

# Reload systemd daemon
sudo systemctl daemon-reload
echo "  ✅ Systemd daemon reloaded"

# --- Enable Services ---
echo ""
echo "[5/6] Enabling services for auto-start..."
sudo systemctl enable clawbolt-messenger.service
sudo systemctl enable clawbolt-messenger-health.service
echo "  ✅ Services enabled (will auto-start on boot)"

# --- Start Services ---
echo ""
echo "[6/6] Starting services..."
sudo systemctl start clawbolt-messenger.service
sleep 3

# Verify gateway is running
if systemctl is-active --quiet clawbolt-messenger.service; then
    echo "  ✅ Messenger Gateway is RUNNING on port 8082"
else
    echo "  ❌ Gateway failed to start. Check logs:"
    echo "     sudo journalctl -u clawbolt-messenger -n 20"
    exit 1
fi

# Start health monitor
sudo systemctl start clawbolt-messenger-health.service
if systemctl is-active --quiet clawbolt-messenger-health.service; then
    echo "  ✅ Health Monitor is RUNNING"
else
    echo "  ⚠️  Health Monitor failed to start (non-critical)"
fi

# --- Summary ---
echo ""
echo "═══════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE"
echo "═══════════════════════════════════════════════"
echo ""
echo "  Services:"
echo "    • clawbolt-messenger      → Gunicorn on :8082"
echo "    • clawbolt-messenger-health → Auto-heal monitor"
echo ""
echo "  Manage with:"
echo "    sudo systemctl status clawbolt-messenger"
echo "    sudo systemctl restart clawbolt-messenger"
echo "    sudo journalctl -u clawbolt-messenger -f"
echo ""
echo "  Public Exposure (run separately):"
echo "    ngrok http 8082"
echo ""
echo "  Then configure in Meta Developer Console:"
echo "    • Callback URL: https://<ngrok-url>/webhook"
echo "    • Privacy URL:  https://<ngrok-url>/privacy"
echo "    • Terms URL:    https://<ngrok-url>/terms"
echo ""
echo "═══════════════════════════════════════════════"
