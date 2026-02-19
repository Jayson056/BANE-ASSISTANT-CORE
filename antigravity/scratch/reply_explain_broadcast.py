
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """🛡️ **BANE SYSTEM DIAGNOSTICS:**

Ang natanggap mong message kanina ay isang **System Health Check**. 

Nagkaroon kasi tayo ng maintenance sa server para ma-fix ang "Seen" status at response speed sa Messenger. Ang Admin ay nag-trigger ng test broadcast sa lahat ng active users para masiguradong:
1. ✅ Narereceive niyo ang messages nang mabilis.
2. ✅ Gumagana ang automated responses.
3. ✅ Online ang aming core router.

Wala kang kailangang gawin! Patunay lang ito na **fully operational** na ang system at mas responsive na ako sa mga utos mo. 🦅🚀"""

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
