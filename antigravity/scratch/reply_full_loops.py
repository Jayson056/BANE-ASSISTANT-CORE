
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """🔄 **ACTIVE REMINDER LOOPS & SCHEDULE**

Here is the breakdown of your current loops:

1️⃣ **TASKS & EVENTS (One-Time Loops):**
• **FEB 26 (Thu):** ‼️ Capstone Orientation @ 1:00 PM
• **MAR 24-26:** Concept Presentations
• **APR 13-15:** Midterm Exams

2️⃣ **WEEKLY SCHEDULE (Recurring Loops):**
• **TUE:** Contemporary World & Info Assurance (1:30 PM - 7:30 PM)
• **WED:** App Dev (3:00 PM - 9:00 PM)
• **THU:** Capstone 1 (1:30 PM - 6:30 PM)
• **FRI:** Info Assurance (4:30 PM - 6:30 PM)
• **SAT:** Org Management & Systems Thinking (10:30 AM - 7:30 PM)

3️⃣ **ASSIGNMENTS:**
❌ **None Found.**
Wala akong nakikitang active assignments files sa workspace mo.

If you have a new assignment, tell me the details so I can add it to the loop! 📝"""

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
        # 3. Send Voice
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
