
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """📄 **FILE ANALYSIS:**

That was the file **"Principles of Systems Thinking"** (the same one you have in your COMP 026 folder).

**Details:**
• **Title:** Principles of Systems Thinking
• **Authors:** Compiled by Domingo, Iluminada Vivien R. & Moñeza, Teresita G.
• **Reason for Removal:** It was uploaded to the **INTE 302 (Information Assurance)** folder, but it belongs to **COMP 026**. Since you already have a copy there, I removed this duplicate to keep your files clean. 🧹

Please double-check and upload the **Information Assurance** file instead! 🛡️"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Atlas for clear explanation)
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
