import sys
import subprocess
import os

user_id = "5662168844"
text = """Based on our system logs, **Ferd Apable** is a recognized member of this **AI test** group chat. 👤

Per our configuration:
• He is a distinct user with his own isolated data environment. 🔒
• The system is set to automatically initialize his private workspace upon his first interaction. ⚙️

Everything is set for him to participate! 🚀"""

try:
    # Send Text
    print("Sending text...")
    subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", user_id, text], check=True)

    # Generate Voice
    print("Generating voice...")
    res = subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/text_to_speech.py", "--ogg", text], capture_output=True, text=True)
    v_path = res.stdout.strip()
    print(f"Voice path: {v_path}")

    if v_path and os.path.exists(v_path):
        # Send Voice
        print("Sending voice...")
        subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", user_id, "--voice", v_path], check=True)
    else:
        print(f"Voice generation failed. Output: {res.stdout} Error: {res.stderr}")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
