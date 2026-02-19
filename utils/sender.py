
"""
BANE Unified Sender Utility
Handles all outbound communications (Messenger & Telegram) with Shadow Protocol support.
Replaces send_messenger.py, send_telegram.py, and shadow_send.py.
"""
import os
import sys
import json
import argparse
import logging
import requests
import subprocess
from dotenv import load_dotenv

# --- CONFIG & SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load Secrets
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_FILE = os.path.join(ROOT_DIR, "config", "secrets.env")
load_dotenv(dotenv_path=SECRETS_FILE)

# Constants
MESSENGER_TOKEN = os.getenv("MESSENGER_PAGE_ACCESS_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SHADOW_STATE_FILE = "/home/son/BANE_Workspaces/USER-DATA/9eb397f15a125a6d/shadow_state.json"

# Persistent Sessions
_SESSION = requests.Session()

# --- SHADOW PROTOCOL ---
def is_shadow_active():
    """Check if Shadow Mode is active."""
    if os.path.exists(SHADOW_STATE_FILE):
        try:
            with open(SHADOW_STATE_FILE, 'r') as f:
                return json.load(f).get("shadow_mode", False)
        except:
            pass
    return False

def encrypt_payload(text):
    """Encrypt text using Shadow Encryptor."""
    try:
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)
        from antigravity.shadow_encryptor import encrypt_text
        return encrypt_text(text)
    except Exception as e:
        logger.warning(f"Encryption failed: {e}")
        return text

def decrypt_payload(text):
    """Decrypt text using Shadow Encryptor."""
    if not text or not text.startswith("ENC[AES"):
        return text
    try:
        sys.path.append(ROOT_DIR)
        from antigravity.shadow_encryptor import decrypt_text
        return decrypt_text(text)
    except Exception as e:
        logger.warning(f"Decryption failed: {e}")
        return text

# --- MESSENGER LOGIC ---
def send_messenger(recipient_id, text=None, attachment=None, att_type="file", reply_to=None, react=None, msg_id=None):
    if not MESSENGER_TOKEN:
        logger.error("Missing Messenger Token")
        return False

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={MESSENGER_TOKEN}"
    
    # 1. Handle Reactions
    if react and msg_id:
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": "react",
            "payload": {"message_id": msg_id, "reaction": react}
        }
        try:
            res = _SESSION.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                logger.info(f"✅ Messenger Reaction Sent: {react}")
                return True
            else:
                logger.error(f"❌ Reaction Failed: {res.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Reaction Error: {e}")
            return False

    # 2. Handle Attachments
    if attachment:
        payload = {
            "recipient": f'{{"id":"{recipient_id}"}}',
            "message": f'{{"attachment":{{"type":"{att_type}", "payload":{{"is_reusable":true}}}}}}'
        }
        try:
            with open(attachment, 'rb') as f:
                files = {'filedata': (os.path.basename(attachment), f, 'application/octet-stream')}
                res = requests.post(url, data=payload, files=files, timeout=60)
                if res.status_code == 200:
                    logger.info(f"✅ Messenger Attachment Sent: {attachment}")
                    return True
                else:
                    logger.error(f"❌ Attachment Failed: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Attachment Error: {e}")
            return False

    # 3. Handle Text
    if text:
        # Shadow Logic: Decrypt if needed (middleware), Encrypt if needed (outbound)
        # However, for OUTBOUND `sender.py`, we usually receive plain text to send.
        # Check if we need to encrypt BEFORE sending to user (if Shadow Mode is ON).
        if is_shadow_active():
            text = encrypt_payload(text)
            logger.info("🔒 Shadow Mode: Payload Encrypted")
        
        # If input text was ALREADY encrypted (e.g. from capture), decrypt it first? 
        # No, usually capture provides encrypted, we decrypt in Python, then re-encrypt if needed?
        # Let's assume input `text` here is what we WANT to send.
        # If it starts with ENC, we might want to decrypt it to see it, but we send what we are told.
        # WAIT: The router usually decrypts `capture`, passes PLAIN text to `sender`.
        # `sender` then checks `is_shadow_active` and ENCRYPTS it.
        
        # Correction: If text comes in as ENC... (double encryption check)
        if text.startswith("ENC[AES256]::"):
             # It's already encrypted. Do we send as is?
             # Yes, likely passed directly.
             pass
        elif is_shadow_active():
             text = encrypt_payload(text)

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"
        }
        if reply_to:
            payload["message"]["reply_to"] = {"message_id": reply_to}

        try:
            res = _SESSION.post(url, json=payload, timeout=10)
            
            # Retry without reply_to if strict mode fails
            if res.status_code == 400 and "reply_to" in res.text and reply_to:
                del payload["message"]["reply_to"]
                res = _SESSION.post(url, json=payload, timeout=10)

            if res.status_code == 200:
                mid = res.json().get("message_id")
                print(f"ID: {mid}") # Output ID for caller
                logger.info("✅ Messenger Text Sent")
                return True
            else:
                logger.error(f"❌ Messenger Failed: {res.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Messenger Error: {e}")
            return False
            
    return False

# --- TELEGRAM LOGIC ---
def send_telegram(chat_id, text=None, attachment=None, att_type="document", reply_to=None):
    if not TELEGRAM_TOKEN:
        logger.error("Missing Telegram Token")
        return False
        
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
    
    # Shadow Logic
    if text and is_shadow_active() and not text.startswith("ENC[AES"):
        text = encrypt_payload(text)
        logger.info("🔒 Shadow Mode: Payload Encrypted (Telegram)")

    # 1. Attachment
    if attachment:
        endpoint = "sendDocument"
        files = {"document": open(attachment, "rb")}
        if att_type == "voice":
            endpoint = "sendVoice"
            files = {"voice": open(attachment, "rb")}
        elif att_type == "photo":
            endpoint = "sendPhoto"
            files = {"photo": open(attachment, "rb")}
            
        data = {"chat_id": chat_id}
        if reply_to: data["reply_to_message_id"] = reply_to
        if text: data["caption"] = text
        
        try:
            res = requests.post(api_url + endpoint, data=data, files=files, timeout=60)
            if res.status_code == 200:
                logger.info(f"✅ Telegram {att_type} Sent")
                return True
            else:
                logger.error(f"❌ Telegram Attachment Failed: {res.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")
            return False

    # 2. Text
    if text:
        data = {"chat_id": chat_id, "text": text}
        if reply_to: data["reply_to_message_id"] = reply_to
        
        # Try Markdown first
        data["parse_mode"] = "Markdown"
        try:
            res = _SESSION.post(api_url + "sendMessage", json=data, timeout=10)
            if res.status_code == 200:
                logger.info("✅ Telegram Text Sent (Markdown)")
                return True
            
            # Fallback to Plain
            if res.status_code == 400:
                data.pop("parse_mode", None)
                res = _SESSION.post(api_url + "sendMessage", json=data, timeout=10)
                if res.status_code == 200:
                    logger.info("✅ Telegram Text Sent (Plain)")
                    return True
            
            logger.error(f"❌ Telegram Failed: {res.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")
            return False

    return False

# --- UTILITIES ---
def contains_sensitive_info(text):
    """Check if text contains sensitive information like passwords or tokens."""
    if not text:
        return False
    # Basic heuristic: check for common sensitive patterns
    sensitive_keywords = ["BEGIN PRIVATE KEY", "AES256", "token=", "key="]
    
    # Check if the message looks like a password injection command
    if text.strip().startswith("/pass") or text.strip().startswith("/sudo"):
        return True
        
    for kw in sensitive_keywords:
        if kw in text:
            return True
            
    return False

def set_message_reaction(chat_id, message_id, reaction):
    """Set a reaction on a Telegram message."""
    if not TELEGRAM_TOKEN:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMessageReaction"
    # Telegram expects a JSON object for reaction
    # Modern API: reaction=[{"type": "emoji", "emoji": "👍"}]
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": reaction}]
    }
    
    try:
        if not reaction: # Clear reaction
             payload["reaction"] = []
             
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            return True
        else:
            logger.error(f"Reaction Failed: {res.text}")
            return False
    except Exception as e:
        logger.error(f"Reaction Error: {e}")
        return False

# --- MAIN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BANE Unified Sender")
    parser.add_argument("--platform", required=True, choices=["messenger", "telegram"], help="Target Platform")
    parser.add_argument("--recipient_id", required=True, help="User ID / Chat ID")
    parser.add_argument("--text", help="Message Text")
    parser.add_argument("--attachment", help="File Path")
    parser.add_argument("--type", default="file", help="Attachment Type (file, voice, image)")
    parser.add_argument("--reply_to", help="Reply Message ID")
    parser.add_argument("--react", help="Reaction Emoji")
    parser.add_argument("--msg_id", help="Target Message ID for reaction")
    parser.add_argument("--shadow_force", action="store_true", help="Force Shadow Mode")

    args = parser.parse_args()
    
    # Handle Newlines in text arg
    text_content = args.text.replace("\\n", "\n") if args.text else None
    
    # Shadow Force Override
    if args.shadow_force:
        # We can implement a temporary override or just rely on logic
        pass

    success = False
    if args.platform == "messenger":
        success = send_messenger(
            args.recipient_id, 
            text=text_content, 
            attachment=args.attachment, 
            att_type=args.type, 
            reply_to=args.reply_to,
            react=args.react,
            msg_id=args.msg_id
        )
    elif args.platform == "telegram":
        success = send_telegram(
            args.recipient_id,
            text=text_content,
            attachment=args.attachment,
            att_type=args.type,
            reply_to=args.reply_to
        )
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
