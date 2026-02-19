
import sys
import subprocess
import os

user_id = "26065703363071727"
text = """📚 **STATUS NG INSTRUCTIONAL MATERIALS (IMs):**

Chineck ko ang bawat course folder mo, andito ang mga subjects na may lamang materials:

1. ✅ **COMP 010 - Information Management**
   • Marami itong files (SQL, Data Modeling, Relational Algebra, etc.) na nasa loob mismo ng subject folder.

2. ✅ **COMP 026 - Principles of Systems Thinking**
   • Meron itong sub-folder na **"Instructional Materials"** na may nilalaman na PPTX at PDF files.

3. ⚠️ **Ibang Subjects**
   • Sa ngayon, wala pang laman na "Instructional Materials" ang `COMP 019`, `GEED 003`, `HRMA 001`, `INTE 302`, at `INTE 303`.

Handa na akong mag-sort kung may mga bagong materials kang i-u-upload! 🚀"""

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice
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
