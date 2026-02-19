import sys
import subprocess
import os

chat_id = "-1003794853491"
text = """I'm currently performing a **Core Maintenance** scan! 🛰️

Now that I've suppressed the notification noise in this group, I'm monitoring the system's background processes to ensure everything is running smoothly. Specifically:
• Monitoring incoming message synchronization. 🔄
• Checking the stability of the new **Core Router** rules. ✅
• Ensuring the dual-channel (Text + Voice) bridge is optimal. 🔊

I'm essentially "tuning the engine" while we chat. Is there any specific system check you'd like me to perform? 🚀"""

try:
    # Send Text
    print("Sending text...")
    subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", chat_id, text], check=True)

    # Generate Voice
    print("Generating voice...")
    res = subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/text_to_speech.py", "--ogg", text], capture_output=True, text=True)
    v_path = res.stdout.strip()
    print(f"Voice path: {v_path}")

    if v_path and os.path.exists(v_path):
        # Send Voice
        print("Sending voice...")
        subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", chat_id, "--voice", v_path], check=True)
    else:
        print(f"Voice generation failed. Output: {res.stdout} Error: {res.stderr}")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
