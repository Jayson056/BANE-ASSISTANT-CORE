
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """⚠️ **FILE CORRECTION!**

You are absolutely right! 🛑
My analysis was wrong. I checked the content and it is indeed **Principles of Systems Thinking**.

**Actions Taken:**
1.  **Moved**: File removed from `INTE 302` folder.
2.  **Transferred**: Successfully moved to `COMP 026 - Principles of Systems Thinking`.
3.  **Renamed**: Changed filename to `Principles_of_Systems_Thinking_Main_Module.pdf` for clarity.

This means **INTE 302 (Info Assurance)** is now **EMPTY**. 🗑️
Please upload the correct file for that subject if you have it! 📤"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Critical/Apologetic tone -> Echo or Atlas)
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
