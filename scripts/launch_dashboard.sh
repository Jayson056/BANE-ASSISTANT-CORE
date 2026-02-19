#!/bin/bash
# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# BANE - Dashboard Launch Script
# Created by Antigravity

# Cleanup old processes
pkill -f monitor_server.py
pkill -f localtunnel
pkill -f ngrok
sleep 1

# 1. Start the Monitor Server
cd /home/user/BANE_CORE/dashboard
nohup python3 monitor_server.py > monitor.log 2>&1 &
echo "⚡ BANE Monitor Server started in background."

# 2. Start ngrok (Dual Tunnel: Dashboard + Messenger)
nohup /home/son/Documents/jvps/ngrok start messenger dashboard > ngrok.log 2>&1 &
echo "🌐 ngrok started with dual tunnels (8081, 8082) in background."

# Wait for tunnels to stabilize
echo "⏳ Waiting for ngrok URLs..."
MAX_ATTEMPTS=15
ATTEMPT=0
DASHBOARD_URL=""
MESSENGER_URL=""

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    JSON_DATA=$(curl -s http://localhost:4040/api/tunnels)
    DASHBOARD_URL=$(echo $JSON_DATA | python3 -c "import sys, json; data=json.load(sys.stdin); print([t['public_url'] for t in data['tunnels'] if t['name']=='dashboard'][0]) if 'tunnels' in data else print('')" 2>/dev/null)
    MESSENGER_URL=$(echo $JSON_DATA | python3 -c "import sys, json; data=json.load(sys.stdin); print([t['public_url'] for t in data['tunnels'] if t['name']=='messenger'][0]) if 'tunnels' in data else print('')" 2>/dev/null)
    
    if [ ! -z "$DASHBOARD_URL" ] && [ ! -z "$MESSENGER_URL" ]; then
        break
    fi
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

# 3. Send Telegram Notification
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Load environment to get TELEGRAM_USER_ID
source /home/user/BANE_CORE/config/secrets.env 2>/dev/null

STARTUP_MSG="🦅 *BANE Multi-Channel Uplink Established*

🚀 *Dashboard (Port 8081)*
🏠 Local: http://${LOCAL_IP}:8081
🌐 Public: ${DASHBOARD_URL:-[Failed]}

💬 *Messenger Gateway (Port 8082)*
🌐 Public: ${MESSENGER_URL:-[Failed]}

*Action Required*: If the Messenger URL changed, please update the Callback URL in your Meta Developer Console to:
\`${MESSENGER_URL}/webhook\`"

/home/user/BANE_CORE/.venv/bin/python3 /home/user/BANE_CORE/utils/sender.py \
    --platform telegram \
    --recipient_id "${TELEGRAM_USER_ID}" \
    --text "${STARTUP_MSG}"

