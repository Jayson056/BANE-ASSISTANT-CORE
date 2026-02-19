
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """📄 **FILE ANALYSIS: CERTIFICATE OF REGISTRATION (COR)**

Ang in-attach mong file (`file_20260215_102004.pdf`) ay ang iyong **official COR**. Heto ang mga details na na-extract ko:

👤 **Student:** Jayson Apable Combate
📚 **Program:** BSIT (Third Year, Section 1N)
📍 **Status:** Irregular (BSIT 2-3 for some subjects)

**Key Observations:**
• **Ethics (GEED 008)**: Wala ito sa listahan ng subjects mo rito.
• **Info Management (COMP 010)**: Ito ang pinalit sa Ethics, scheduled every Wednesday (07:30 AM - 12:30 PM).

Dahil dito, updated na ang schedule records mo sa system ko at inalis na natin ang Ethics sa iyong active reminder loops. 🚀"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "atlas"], capture_output=True, text=True)
    v_path = res.stdout.strip()
    
    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice (as attachment)
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
