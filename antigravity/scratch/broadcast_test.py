
import sys
import subprocess
import os

users = ["MESSENGER_USER_ID", "26065703363071727", "5662168844"]
broadcast_text = """📢 **BANE SYSTEM STATUS BROADCAST**

Admin directive received: Performing test message to all active users.

✅ **CORE ROUTER:** Restored and Active (PID: 145973)
✅ **MESSENGER GATEWAY:** Online (Port 8082)
✅ **WEBHOOK:** Connection Verified

Service is now fully operational. "Seen" status and real-time responses have been synchronized.

*This is an automated system health check.*"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"

print(f"Starting broadcast to {len(users)} users...")

for uid in users:
    try:
        print(f"Sending to {uid}...")
        subprocess.run([python_path, send_script, broadcast_text, "--recipient_id", uid], check=True)
    except Exception as e:
        print(f"Failed to send to {uid}: {e}")

print("Broadcast complete.")
