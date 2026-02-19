
import os
import json
import subprocess

# Settings
BASE_STORAGE = "/home/son/BANE/storage/users"
SEND_MESSENGER_PATH = "/home/son/BANE/utils/sender.py"
SEND_TELEGRAM_PATH = "/home/son/BANE/utils/sender.py"
PYTHON_PATH = "/home/son/BANE/.venv/bin/python3"

def run_weekly_update():
    """Iterates through all users and sends the weekly schedule update prompt."""
    if not os.path.exists(BASE_STORAGE):
        return

    message = (
        "📊 **WEEKLY SCHEDULE REFRESH**\n\n"
        "Hello! It's Saturday night. I am about to refresh the system-wide "
        "reminders for the upcoming week.\n\n"
        "💡 **ACTION REQUIRED:**\n"
        "If you have any changes to your class schedule, new assignments, or adjusted "
        "deadlines, please send them now or update your tracker link.\n\n"
        "I will perform the autonomous sync in a few moments to ensure your "
        "reminders for next week are 100% accurate. 🚀\n\n"
        "- bane"
    )

    for user_hash in os.listdir(BASE_STORAGE):
        identity_file = os.path.join(BASE_STORAGE, user_hash, "identity.json")
        if os.path.exists(identity_file):
            try:
                with open(identity_file, 'r') as f:
                    user_info = json.load(f)
                
                platform = user_info.get('platform')
                uid = user_info.get('uid')
                
                if platform == 'messenger':
                    cmd = [PYTHON_PATH, SEND_MESSENGER_PATH, "--platform", "messenger", "--text", message, "--recipient_id", uid]
                    subprocess.run(cmd)
                elif platform == 'telegram':
                    cmd = [PYTHON_PATH, SEND_TELEGRAM_PATH, "--platform", "telegram", "--text", message, "--recipient_id", uid]
                    subprocess.run(cmd)
            except Exception as e:
                print(f"Error notifying user {user_hash}: {e}")

if __name__ == "__main__":
    run_weekly_update()
