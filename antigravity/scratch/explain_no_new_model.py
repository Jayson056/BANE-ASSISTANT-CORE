import sys
import subprocess
import os

user_id = "5662168844"
text = """No need to create anything new! 🙅‍♂️ 

The **Core Maintenance** skill (and I, **Clawbolt**) is already fully capable of interacting in the group chat. 

**Why I replied privately:**
My system currently defaults to sending critical data (like identifying a user) directly to **you** to ensure it reaches you safely. 🔒

**How to fix it:**
You don't need a new persona. Just continue chatting in **AI test**. I will adjust my targeting to reply in the group for general queries. 

Let's try again: Ask me something in the group, and I will reply there! 🚀"""

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
