
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """✅ **FIX APPLIED!**

You caught a bug in my memory system! 🐛
Previously, when I replied via script, I wasn't saving my own message ID. That's why your replies were showing `[Original message content lost]`.

I have now patched `utils/send_messenger.py` to automatically save every sent message ID to my history database.

**Try replying to THIS message.**
It should now show the correct context in my logs! 🕵️‍♂️"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Atlas for technical confirmation)
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "atlas"], capture_output=True, text=True)
    v_path = res.stdout.strip()

    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)
    else:
        print("Voice generation failed.")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
