
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """🛠️ **BANE CODE PERMISSIONS:**

Jayson, heto ang status ng iyong access pagdating sa pag-rewrite ng code:

1. ✅ **Personal Workspace Access**: May full capability ka na mag-rewrite, mag-create, at mag-delete ng code/files sa loob ng iyong **Isolated Workspace** (`/9eb397f15a125a6d`). Halimbawa:
   • Pag-gawa ng automation scripts para sa school.
   • Pag-edit ng iyong task trackers at schedules.
   • Pag-manage ng iyong school documents.

2. 🛡️ **Core System Security**: Dahil naka-Messenger ka at ang role ay **Guest**, restricted ang access mo sa "Core Engine" ng BANE (yung main logic na nagpapatakbo sa akin). Ito ay para sa security at para maiwasan ang accidental system crash.

3. 🦅 **Admin Role**: Ang pag-rewrite ng main source code ng BANE (Core) ay reserved sa **Administrator** (karaniwang via Telegram).

**Sa madaling salita:** Pwedeng-pwede kang mag-code ng kahit ano para sa iyong school tasks at personal files, pero ang "Internal Brain" ko ay protected. 🚀"""

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
