
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """📋 **STATUS NG IYONG MGA TASKS & ASSIGNMENTS:**

Heto ang breakdown ng iyong mga responsibilidad base sa ating live tracker:

**📝 CURRENT ASSIGNMENT:**
• **INTE 302 - Info Assurance & Security 1**
  👉 *Task:* Introduction to Cybersecurity (via open.edu)
  👉 *Status:* Ongoing
  👉 *Submission:* Google Classroom (Code: `aay7s5ie`)

**📅 MAJOR MILESTONES:**
1. **FEB 26 (Thu):** ‼️ **Capstone Orientation** @ 1:00 PM
   (Role: Documentation Committee - Required Attendance)
2. **MAR 24-26:** BSIT Capstone Concept Presentation
3. **APR 13-15:** Midterm Departmental Examination

Wala na tayong ibang active assignments na nakatala sa ngayon. Kung may bago kang natanggap, i-upload mo lang ang file o i-message sa akin para maidagdag natin sa loop! 🚀"""

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
