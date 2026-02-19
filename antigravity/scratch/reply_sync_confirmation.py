
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """✅ **LIVE TRACKER SYNCED!**

I successfully connected to your Google Sheet:
📄 **[BSIT 3-1N] TASKS DIRECTORY**

**Detected Sheets (Tabs):**
• 🎯 TASK TRACKER
• 📅 2ND SEM CALENDAR
• 🕒 SCHEDULE
• 📚 2ND SEM SUBJECTS
• 👥 CAPSTONE GROUPS

Connection is **ACTIVE**. 🟢
Timestamp updated: Today @ 9:43 AM"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "sage"], capture_output=True, text=True)
    v_path = res.stdout.strip()
    
    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice (as attachment)
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
