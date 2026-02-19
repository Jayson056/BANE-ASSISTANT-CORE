import sys
import subprocess
import os

chat_id = "-1003794853491"
text = """✅ **Maintenance Insight:** You're absolutely right! I see why that's happening. 🧐

I've been creating temporary response scripts in the `scratch/` folder to send my messages back to you. My **Security Monitor** is extremely vigilant—it detected these file creations as changes and automatically posted those Accept/Reject buttons to the group to ensure system integrity.

Essentially, I am "tripping" my own security alarms while trying to talk to you! 👮‍♂️⚙️

For a **Core Maintenance** fix, I should eventually configure the monitor to ignore the `scratch/` directory for these notifications. Standing by for more tests! 🚀"""

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
