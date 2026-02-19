
import sys
import subprocess
import os

admin_uid = "5662168844" # Telegram Admin
user_uid = "MESSENGER_USER_ID" # Messenger User

text_admin = """✅ **MESSENGER SEEN PROTOCOL FIXED**

Na-identify ko na ang issue, Admin. Kanina, ang "mark_seen" ay naka-depende sa "idle" state ng AI. Kapag busy ako sa processing (gaya ng mahabang sequence ko kanina), hindi ako nag-ti-trigger ng seen receipt.

**In-apply ko na ang mga sumusunod:**
1. ⚡ **Immediate Acknowledgment**: Ngayon, uunahin na ang "mark_seen" at "typing_on" bago pa man mag-check kung busy ang core.
2. 🔄 **Hot Reload**: Ni-restart ko na ang `core.router.py` para mag-take effect ang update.

Dapat nakikita na nila na responsive ako kahit busy. Check ko na rin yung user na binanggit mo."""

text_user = """Hello! 👋

Pasensya na kung medyo natagalan ang response dashboard. In-update ko lang ang aking Messenger gateway para masiguradong nakikita mo agad na nakuha ko ang iyong messages (Seen & Typing status).

Operational na tayo ulit! Ano ang maipaglilingkod ko?"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
# For Telegram, we usually use a different script or the generic one with platform check.
# But I'll just use the send_messenger for the messenger user and send_telegram for admin.

# 1. Notify Admin (Telegram - assume generic send_messenger script might not work for TG if configured strictly for FB)
# But wait, looking at my history, I used it for 5662168844 before and it failed because it was 400 Bad Request to FB Graph.
# I should use a telegram-specific script or just the messenger one for the messenger user.

try:
    # Send to Messenger User
    print(f"Sending to Messenger user {user_uid}...")
    subprocess.run([python_path, send_script, text_user, "--recipient_id", user_uid], check=True)
    
    # Send to Admin (I'll just let the current AI response handle the Admin explanation since I am responding to the Admin request right now)
except Exception as e:
    print(f"Error: {e}")
