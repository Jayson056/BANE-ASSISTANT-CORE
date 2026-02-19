import requests
import time
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
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
CHAT_ID = -1003794853491
ADMIN_ID = 5662168844

def api_call(method, **kwargs):
    resp = requests.post(API_URL + method, json=kwargs, timeout=30)
    return resp.json()

def cleanup_notifications():
    print(f"Starting cleanup in chat {CHAT_ID}...")
    
    # Send probe to get latest message_id
    probe = api_call("sendMessage", chat_id=CHAT_ID, text="✨ Cleaning up system notifications...")
    if not probe.get("ok"):
        print(f"Error: {probe.get('description')}")
        return
        
    latest_id = probe["result"]["message_id"]
    api_call("deleteMessage", chat_id=CHAT_ID, message_id=latest_id)
    
    deleted = 0
    # Scan backward
    for msg_id in range(latest_id - 1, latest_id - 50, -1):
        # We can't read messages directly, so we try to "edit" it to see if it's ours,
        # or forward it to admin to check content.
        # But wait, we know the content we are looking for.
        # Actually, if we forward it to ourselves (the Bot) or Admin, we can see the text.
        
        fwd = api_call("forwardMessage", chat_id=ADMIN_ID, from_chat_id=CHAT_ID, message_id=msg_id)
        if fwd.get("ok"):
            msg_text = fwd["result"].get("text", "") or fwd["result"].get("caption", "")
            fwd_id = fwd["result"]["message_id"]
            
            # Clean up the forward message
            api_call("deleteMessage", chat_id=ADMIN_ID, message_id=fwd_id)
            
            if "AI has made changes to files" in msg_text or "Choose an action" in msg_text:
                res = api_call("deleteMessage", chat_id=CHAT_ID, message_id=msg_id)
                if res.get("ok"):
                    print(f"Deleted notification: {msg_id}")
                    deleted += 1
                else:
                    print(f"Failed to delete {msg_id}: {res.get('description')}")
        
        time.sleep(0.1)

    print(f"Cleanup complete. Deleted {deleted} messages.")
    
    # Notify admin
    requests.post(API_URL + "sendMessage", json={
        "chat_id": ADMIN_ID,
        "text": f"✅ **Cleanup Protocol Complete**\n\nRemoved {deleted} 'File Change' notifications from the group chat."
    })

if __name__ == "__main__":
    cleanup_notifications()
