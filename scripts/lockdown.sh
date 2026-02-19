#!/bin/bash

# BANE PARTIAL LOCKDOWN PROTOCOL
# Secure core system files while keeping operational directories writable.

echo "🔒 Initiating BANE Partial Lockdown..."

# 1. Base Permissions: Restricted by default
# Convert all files to read-only for group/others, owner write only where needed
# chmod -R 755 .  <-- Too broad, let's be specific

# --- LOCKDOWN CORE (Read-Only) ---
echo "🛡️ Locking Core System..."
chmod 555 core/
chmod 444 core/*.py

chmod 555 antigravity/
chmod 444 antigravity/*.py

chmod 555 utils/
chmod 444 utils/*.py

chmod 555 telegram_interface/
chmod 444 telegram_interface/*.py

chmod 555 messenger_interface/
chmod 444 messenger_interface/*.py

chmod 444 main.py
chmod 444 requirements.txt

# --- CRITICAL SECRETS (Owner Read/Write Only) ---
echo "🔑 Securing Secrets..."
chmod 700 config/
touch config/secrets.env
chmod 600 config/secrets.env

# --- OPERATIONAL ZONES (Writable) ---
echo "🔓 Opening Operational Zones..."
# Logs must be writable
chmod 775 logs/
chmod 666 logs/*.log 2>/dev/null

# Storage (User data, images, history) must be writable
chmod -R 775 storage/

# Debug folder
chmod -R 775 Debug/

# Temporary files might need to be written to
touch temp_schedule.csv
chmod 666 temp_schedule.csv
chmod 666 temp_reply_reactions.txt 2>/dev/null
chmod 666 temp_reply_voice.txt 2>/dev/null

# Message history needs write access
chmod 666 storage/message_id_map.json 2>/dev/null

echo "✅ BANE Lockdown Complete."
echo "   - Core/Logic: READ-ONLY (Safe)"
echo "   - Storage/Logs: WRITABLE (Operational)"
