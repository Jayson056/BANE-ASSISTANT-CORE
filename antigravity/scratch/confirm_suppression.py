import sys
import subprocess
import os

chat_id = "-1003794853491"
text = """✅ **System Update: Noise Suppression Active** 🤫

I have successfully modified my **Core Router**. 

🔹 **Group Chats (Like this one)**: I will no longer post "AI has made changes" notifications or Accept/Reject buttons here. This keeps our conversation clean and focused.
🔹 **Private Core Chat**: Those notifications and safety buttons will still appear there, allowing you to maintain full administrative control over the system's file changes.

This improvement ensures a premium, clutter-free experience for group interactions while keeping the core secure! 🚀🌀"""

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
