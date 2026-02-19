
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """⚠️ **Duplicate Detected!**

This appears to be the **Systems Thinking** module again (Same file as before). 🔄
Since I already have this in your `COMP 026` folder, I've cleared it from the `INTE 302 - Information Assurance` folder to avoid confusion.

Still need the correct **Information Assurance & Security** file if you have it! 📤"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Sage for friendly notice)
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "sage"], capture_output=True, text=True)
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
