
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """✅ **CORRECTION NOTED!**

Sorrryyy! My record was outdated. 😓
The file said Feb 16, but I trust you!

**UPDATED SCHEDULE:**
📅 **Feb 23 (Monday)**
‼️ **Capstone Orientation** @ 1:00 PM

So for **tomorrow (Feb 16)**... **FREE DAY!** 🎉
Rest well or catch up on other tasks. Updated na sa system ko!"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Sage for friendly apology)
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
