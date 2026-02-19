
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """📚 **SUBJECTS WITH INSTRUCTIONAL MATERIALS (FOUND):**

Based on your current workspace files, here are the subjects with uploaded materials:

1️⃣ **COMP 010 - Information Management** 🗂️
   • **12 Files Found**: Includes Data Modeling, SQL Functions, Database Development, etc.
   • *Rich resource collection!*

2️⃣ **COMP 026 - Principles of Systems Thinking** 🧠
   • **2 Files**: `Introduction.pdf`, `Welcome.pptx`

3️⃣ **INTE 302 - Information Assurance and Security 1** 🛡️
   • **1 File**: An introductory PDF (`file_20260215_090529.pdf`)

---
⚠️ **Empty / Missing Materials:**
• COMP 019 (App Dev)
• GEED 003 (Contemporary World)
• HRMA 001 (Org & Management)
• INTE 303 (Capstone 1)

If you have materials for these, send them over and I'll sort them for you! 📤"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Atlas for a structured report tone)
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
