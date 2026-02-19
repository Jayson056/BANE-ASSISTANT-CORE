
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """🫡 **NOTED, JAYSON! "CONTENT-FIRST SORTING" PROTOCOL ACTIVE.**

Loud and clear. Simula ngayon, ito ang susundin kong steps kapag nag-send ka ng file:

1. 🔍 **Deep Scan**: Hindi lang filename ang titignan ko. Babasahin ko mismo ang laman ng document (via OCR/Text extraction).
2. 🏷️ **Course Match**: Ihahambing ko ang keywords sa content (gaya ng "Cryptography" para sa INTE 302 o "Relational Algebra" para sa COMP 010) sa listahan ng active subjects mo.
3. 📂 **Smart Storage**: Awtomatiko ko itong ilalagay sa tamang folder para hindi mo na kailangang mag-manual move.

Asahan mo na bago ko i-move ang file, siguradong na-verify ko na ang relevance nito. Ready na ako sa susunod na uploads mo! 🚀"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice (Atlas for a professional, reliable tone)
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "atlas"], capture_output=True, text=True)
    v_path = res.stdout.strip()
    
    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice (as attachment)
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
