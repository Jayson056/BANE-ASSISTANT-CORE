
import subprocess
import os

# RECIPIENTS
MESSENGER_USERS = ["MESSENGER_USER_ID", "26065703363071727", "26118950644407578"]
TELEGRAM_USERS = ["5662168844", "-1003794853491"]

# CONTENT
ANNOUNCEMENT = """📢 **ADMIN ANNOUNCEMENT: BATMAN'S TALE**

🐈 **The Whiskered Watchman**
"I am Batman. Not the one in a cape, but the one with paws. While the system stays awake for 24 hours, I stay awake too, watching the green pulses of the BANE core. My human thinks he’s in charge, but I am the one who keeps the processor warm with my fur. Today the screen is bright, the code is locked, and the mouse pointer is finally trapped by my tail. Sleep is for the weak; the core and I are eternal."

-- *Broadcasted by Admin Order* 🦅"""

PYTHON_PATH = "/home/user/BANE_CORE/.venv/bin/python3"
MSG_SCRIPT = "/home/user/BANE_CORE/utils/send_messenger.py"
TG_SCRIPT = "/home/user/BANE_CORE/utils/send_telegram.py"

def broadcast():
    # 1. Messenger Broadcast
    for psid in MESSENGER_USERS:
        print(f"Sending to Messenger: {psid}")
        try:
            subprocess.run([PYTHON_PATH, MSG_SCRIPT, ANNOUNCEMENT, "--recipient_id", psid], check=True)
        except Exception as e:
            print(f"Failed to send to Messenger {psid}: {e}")

    # 2. Telegram Broadcast
    for chat_id in TELEGRAM_USERS:
        print(f"Sending to Telegram: {chat_id}")
        try:
            subprocess.run([PYTHON_PATH, TG_SCRIPT, ANNOUNCEMENT, "--chat_id", chat_id, "--title", "ANNOUNCEMENT"], check=True)
        except Exception as e:
            print(f"Failed to send to Telegram {chat_id}: {e}")

if __name__ == "__main__":
    broadcast()
