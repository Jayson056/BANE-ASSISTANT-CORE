
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """📅 **DETAILED WEEKLY SCHEDULE (Verified from Grid)**

I've scrolled through the full grid and extracted the exact times:

**TUESDAY:**
• 1:30 PM - 4:30 PM: Contemporary World (E415)
• 4:30 PM - 7:30 PM: Info Assurance & Security 1 Lab (S501/E413)

**WEDNESDAY:**
• 3:00 PM - 5:00 PM: App Dev (E415/S511)
• 6:00 PM - 9:00 PM: App Dev Lab (S511/E415)

**THURSDAY:**
• 1:30 PM - 6:30 PM: Capstone Project 1 Lab (S504/E415)

**FRIDAY:**
• 1:30 PM - 4:30 PM: [Ethics - *Excluded by you*]
• 4:30 PM - 6:30 PM: Info Assurance & Security 1 Lab (S501/E413)

**SATURDAY:**
• 10:30 AM - 1:30 PM: Org and Management (E417)
• 2:00 PM - 7:30 PM: Systems Thinking Lab (E415/S503)

Your local tracker and schedule files are now updated with these precise time blocks! 🚀"""

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
