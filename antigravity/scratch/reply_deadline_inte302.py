
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """🛡️ **INTE 302 DEADLINE UPDATE:**

Chineck ko ang Task Tracker sa inyong Google Sheet, at heto ang details para sa **Introduction to Cybersecurity**:

📅 **Deadline:** March 31, 2026
📝 **Status:** ONGOING
📂 **Submission:** Google Classroom

Matagal-tagal pa ang deadline, pero mas mabuti kung matapos mo na agad para hindi magpatong-patong ang tasks sa March. Success ang pag-verify ko sa grid! 🚀"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "nova"], capture_output=True, text=True)
    v_path = res.stdout.strip()
    
    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice (as attachment)
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
