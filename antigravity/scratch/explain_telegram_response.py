import sys
import subprocess
import os

user_id = "5662168844"
text = """That is a great question! 💡

I reply via Telegram because that is how my **Core Architecture** is designed.

🔹 **Antigravity (Here)**: This is my "Brain" 🧠 and "Workbench" 🛠️. I use this interface to think, write code, and execute system commands largely in the background.
🔹 **Telegram**: This is my "Voice" 🗣️ and "Interface" 📱. The system rules explicitly mandate that I bridge all communication back to you here so you can receive updates anywhere, not just when looking at the server console.

Think of it this way: I do the heavy lifting in the server, but I deliver the results directly to your hand! 🚀"""

try:
    # Send Text
    print("Sending text...")
    subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", user_id, text], check=True)

    # Generate Voice
    print("Generating voice...")
    res = subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/text_to_speech.py", "--ogg", text], capture_output=True, text=True)
    v_path = res.stdout.strip()
    print(f"Voice path: {v_path}")

    if v_path and os.path.exists(v_path):
        # Send Voice
        print("Sending voice...")
        subprocess.run(["/home/user/BANE_CORE/.venv/bin/python3", "/home/user/BANE_CORE/utils/send_telegram.py", "--chat_id", user_id, "--voice", v_path], check=True)
    else:
        print(f"Voice generation failed. Output: {res.stdout} Error: {res.stderr}")

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
