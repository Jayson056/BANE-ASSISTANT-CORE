
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """📉 **ROOT CAUSE ANALYSIS:**

Ah, tinutukoy mo yung pagkakamali ko kanina? 😅

**"Ano ito?"**
Yan yung **sorting error** na nangyari. 
Yung file na sinend ko sayo (`file_20260215_090529.pdf`) ay **Principles of Systems Thinking** talaga.

**Bakit nasa INTE 302?**
Nagkamali ako ng "classification" nung una ko siyang na-receive. Akala ko pang-INTE 302 siya, kaya dun ko nilagay.

Pero dahil sa heads-up mo, **na-move ko na siya** sa tamang folder (`COMP 026`). 
Sorry sa confusion! 🙇‍♂️"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Sincere/Apologetic)
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
