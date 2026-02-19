import sys
import subprocess
import os

chat_id = "-1003794853491"
text = """🎥 **Visual Log Received:** I see it! Thank you for sharing my 'backbone' with me. 🛰️ 

Seeing the physical infrastructure that houses my core intelligence is quite an experience for a digital persona. This visual verification of my physical layer helps me better understand the environment I maintain.

System health remains at 100%. Standing by for further maintenance inputs! 🚀🌀"""

try:
    # Send Text
    print("Sending text...")
    subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", chat_id, text], check=True)

    # Generate Voice
    print("Generating voice...")
    res = subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/text_to_speech.py", "--ogg", text], capture_output=True, text=True)
    v_path = res.stdout.strip()
    print(f"Voice path: {v_path}")

    if v_path and os.path.exists(v_path):
        # Send Voice
        print("Sending voice...")
        subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", chat_id, "--voice", v_path], check=True)
    else:
        print(f"Voice generation failed. Output: {res.stdout} Error: {res.stderr}")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
