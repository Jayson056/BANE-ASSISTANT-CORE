
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
file_path = "/home/user/BANE_CORE_Workspaces/USER-DATA/9eb397f15a125a6d/School/INTE 302 - Information Assurance and Security 1/file_20260215_090529.pdf"
file_name = os.path.basename(file_path)

text = f"📂 **INTE 302 RESOURCE**\n\nHere is the file you requested: `{file_name}`\n(Size: ~9MB)\n\nSending now... 📤"

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text Notification
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Upload and Send the File
    if os.path.exists(file_path):
        print(f"Sending file: {file_path}")
        subprocess.run([python_path, send_script, "--attachment", file_path, "--type", "file", "--recipient_id", user_id], check=True)
    else:
        print(f"ERROR: File not found at {file_path}")
        subprocess.run([python_path, send_script, "⚠️ Error: File not found in storage.", "--recipient_id", user_id], check=True)

    # 3. Generate Voice Confirmation
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, "Sending the file for Information Assurance and Security. Check your attachments!", "--voice", "sage"], capture_output=True, text=True)
    v_path = res.stdout.strip()

    if v_path and os.path.exists(v_path):
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
