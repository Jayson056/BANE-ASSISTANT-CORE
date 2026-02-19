#!/bin/bash
# CLAWBOLT - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# Antigravity Auto-Launcher for CLAWBOLT

LOCKFILE="/tmp/antigravity_launch.lock"
LOGFILE="/tmp/antigravity_startup.log"

# CRITICAL: Export environment variables immediately
export DISPLAY=:0
export XAUTHORITY=/home/son/.Xauthority
export XDG_RUNTIME_DIR=/run/user/1000

echo "🔍 Checking Antigravity launch status..." | tee -a "$LOGFILE"

# Try to acquire lock (atomic check-and-set)
if ! mkdir "$LOCKFILE" 2>/dev/null; then
    echo "⚠️ Launch already in progress (lockfile exists). Exiting." | tee -a "$LOGFILE"
    exit 0
fi

# Ensure lockfile cleanup on exit
trap 'rmdir "$LOCKFILE" 2>/dev/null' EXIT

# Check if Antigravity is already running
if pgrep -x "antigravity" > /dev/null; then
    echo "✅ Antigravity is already running. Focusing window..." | tee -a "$LOGFILE"
    wmctrl -a "Antigravity" || wmctrl -a "CLAWBOLT"
    exit 0
fi

# Defensive cleanup: Kill any zombie/orphan processes
if pgrep -if "antigravity" > /dev/null 2>&1; then
    echo "🧹 Cleaning up orphan Antigravity processes..." | tee -a "$LOGFILE"
    pkill -if "antigravity"
    sleep 1
fi

echo "🚀 Launching Antigravity..." | tee -a "$LOGFILE"

# Launch Antigravity (single attempt)
/usr/bin/antigravity &>> "$LOGFILE" &
LAUNCH_PID=$!

# Wait for it to start (max 5 seconds)
for i in {1..5}; do
    sleep 1
    if pgrep -x "antigravity" > /dev/null; then
        echo "✅ Antigravity launched successfully (PID: $(pgrep -x antigravity))" | tee -a "$LOGFILE"
        # Ensure it has focus
        sleep 1
        wmctrl -a "Antigravity" 2>/dev/null
        exit 0
    fi
done

# If we get here, launch failed
echo "❌ Failed to launch Antigravity" | tee -a "$LOGFILE"
echo "Check logs: $LOGFILE"
exit 1

