import requests
import json
import os

# Load token from secrets
_sf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "secrets.env")
if os.path.exists(_sf):
    with open(_sf) as _f:
        for _l in _f:
            if _l.strip() and not _l.startswith('#') and '=' in _l:
                _k, _v = _l.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"'))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

params = {"offset": -10} # Get last 10 updates
response = requests.get(API_URL, params=params)
data = response.json()

if data.get("ok"):
    for update in data["result"]:
        # Check message
        if "message" in update:
            chat = update["message"]["chat"]
            print(f"Message in: {chat.get('title', 'Private')} ({chat['id']})")
        # Check my_chat_member (when bot is added)
        if "my_chat_member" in update:
            chat = update["my_chat_member"]["chat"]
            print(f"Added to: {chat.get('title')} ({chat['id']})")
        # Check chat_member
        if "chat_member" in update:
            chat = update["chat_member"]["chat"]
            print(f"Member update in: {chat.get('title')} ({chat['id']})")
else:
    print(f"Error: {data}")
