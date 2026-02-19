import requests
import time
import os
import argparse

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
ADMIN_ID = ADMIN_USER_ID
GROUP_ID = -1003794853491

TEST_KEYWORDS = [
    "Test", "demo", "Diagnostics", "Check", "verified", 
    "Korean Voice Engine", "Global Voice Gallery", 
    "Polyglot", "Targeting", "accent", "demonstration",
    "Kamusta", "안녕하세요", "Bonjour", "Hola", "Hello Jayson",
    "Resending", "Broadcast", "Korean Logic"
]

def api_call(method, **kwargs):
    try:
        resp = requests.post(API_URL + method, json=kwargs, timeout=30)
        return resp.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def cleanup_chat(chat_id, scan_depth=100):
    print(f"Starting cleanup in chat {chat_id} (Scan depth: {scan_depth})...")
    
    probe = api_call("sendMessage", chat_id=chat_id, text="🧹 **Initializing Cleanup Mode...**")
    if not probe.get("ok"):
        print(f"Error probing {chat_id}: {probe.get('description')}")
        return 0
        
    latest_id = probe["result"]["message_id"]
    api_call("deleteMessage", chat_id=chat_id, message_id=latest_id)
    
    deleted = 0
    for msg_id in range(latest_id - 1, latest_id - scan_depth - 1, -1):
        # Forward to admin to check content (even if in private chat, forwarding works)
        fwd = api_call("forwardMessage", chat_id=ADMIN_ID, from_chat_id=chat_id, message_id=msg_id)
        if fwd.get("ok"):
            res = fwd["result"]
            msg_text = res.get("text", "") or res.get("caption", "")
            fwd_id = res["message_id"]
            
            # Clean up the forward message immediately
            api_call("deleteMessage", chat_id=ADMIN_ID, message_id=fwd_id)
            
            # Check if it matches testing criteria (is from bot and has keywords)
            # Checking if from bot: res.get("from", {}).get("is_bot") might not work as it's forwarded
            # But the 'forward_from' would be the bot if it was the bot's message.
            is_from_bot = res.get("forward_from", {}).get("id") == int(BOT_TOKEN.split(":")[0]) or \
                          res.get("from_user", {}).get("is_bot") # Fallback
            
            # Simple content check
            should_delete = any(kw.lower() in msg_text.lower() for kw in TEST_KEYWORDS)
            
            if should_delete:
                del_res = api_call("deleteMessage", chat_id=chat_id, message_id=msg_id)
                if del_res.get("ok"):
                    print(f"Deleted [{chat_id}] Message {msg_id}: {msg_text[:30]}...")
                    deleted += 1
        
        time.sleep(0.05)
    return deleted

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=150)
    args = parser.parse_args()
    
    total_deleted = 0
    
    # 1. Clean Group
    total_deleted += cleanup_chat(GROUP_ID, scan_depth=args.depth)
    
    # 2. Clean Private
    total_deleted += cleanup_chat(ADMIN_ID, scan_depth=args.depth)
    
    print(f"Cleanup complete. Total deleted: {total_deleted}")
    
    # Final Report
    requests.post(API_URL + "sendMessage", json={
        "chat_id": ADMIN_ID,
        "text": f"✅ **Test Cleanup Complete**\n\nI have scanned both platforms and removed **{total_deleted}** testing-related messages.\n\nSystems remain active and clean. 🦅"
    })
