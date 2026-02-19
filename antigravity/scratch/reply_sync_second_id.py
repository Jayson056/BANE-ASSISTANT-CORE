
import sys
import subprocess
import os

user_id = "MESSENGER_USER_ID"
text = """✅ **SYSTEM SYNC COMPLETE : WORKSPACE RECONFIGURED**

Jayson, na-process ko na ang request mo para sa account na ito. Here is the confirmation of all updates:

1. 🔍 **COR Verified**: Nahanap ko ang COR mo (`file_20260214_194044.pdf`). Inalis ko na ang Ethics at pinalitan ng **Information Management (COMP 010)** sa official record mo.
2. 📅 **Schedule & Grid Sync**: Updated na ang schedule mo with exact times (e.g., 4:30 PM labs) at accurate room numbers from the grid.
3. ‼️ **Capstone Date Fixed**: Corrected the Orientation date to **Feb 26** (Documentation Committee role is active).
4. 📂 **Content-First Sorting**: Active na ang protocol ko. Simula ngayon, babasahin ko ang laman ng bawat file bago ko ito i-save sa tamang subject folder.
5. ⏰ **11:59 PM Auto-Sync**: Naka-schedule na ang system ko na mag-sync ng tracker link niyo every midnight para handa ang info mo paggising.

Everything is now synchronized across your Messenger accounts. Ready na ako sa next task! 🚀"""

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
