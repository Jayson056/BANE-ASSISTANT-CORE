# BANE Messenger Interface
# Handles Webhook verification and message reception for Meta Messenger API
# Also serves Legal Documents for App Review

import os
import logging
from flask import Flask, request, render_template, send_from_directory
from dotenv import load_dotenv

# Load Environment from Root
# Load from config relative to root or absolute path
load_dotenv(dotenv_path="config/secrets.env")
if not os.getenv("MESSENGER_VERIFY_TOKEN"):
    # Fallback for localized testing
    load_dotenv(dotenv_path="../config/secrets.env")

app = Flask(__name__, template_folder="templates")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
verify_token = os.getenv("MESSENGER_VERIFY_TOKEN")
access_token = os.getenv("MESSENGER_PAGE_ACCESS_TOKEN")

logger.info(f"Gateway config loaded. Verify Token present: {bool(verify_token)}, Access Token present: {bool(access_token)}")

@app.route("/", methods=["GET"])
def index():
    return "BANE - Messenger Gateway Online. Visit <a href='/privacy'>/privacy</a> or <a href='/terms'>/terms</a>."

# --- Legal Docs (Required for Meta App Review) ---
@app.route("/privacy", methods=["GET"])
def privacy():
    return render_template("legal/privacy.html")

@app.route("/terms", methods=["GET"])
def terms():
    return render_template("legal/terms.html")

# --- Webhook Verification & Event Handling ---
@app.route("/webhook", methods=["GET"])
def verify():
    """Validates webhook subscription."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            logger.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification Failed", 403
    return "Webhook Endpoint Operational", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming messages."""
    data = request.get_json()
    
    if data["object"] == "page":
        for entry in data["entry"]:
            # Iterate over messaging events
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event or "reaction" in event:
                        try:
                            # Run processing in a background thread to prevent Meta webhook timeouts (retries)
                            import threading
                            thread = threading.Thread(target=process_messenger_event, args=(event,))
                            thread.start()
                        except Exception as e:
                            logger.error(f"Failed to spawn processing thread: {e}")

        return "EVENT_RECEIVED", 200
    else:
        return "Not a Page Event", 404

def process_messenger_event(event):
    """Bridge to Core Router's async handler with persistent event loop."""
    import asyncio
    from core.router import handle_messenger_message
    
    sender_id = event["sender"]["id"]
    
    # ⚡ IMMEDIATE USER FEEDBACK (Connection-Pooled)
    # Use a persistent session to avoid TLS handshake on every message
    if not hasattr(process_messenger_event, '_session'):
        process_messenger_event._session = __import__('requests').Session()
    
    def quick_feedback():
        try:
            token = os.getenv("MESSENGER_PAGE_ACCESS_TOKEN")
            url = f"https://graph.facebook.com/v19.0/me/messages?access_token={token}"
            sess = process_messenger_event._session
            # Batch: mark_seen + typing_on using persistent session (saves ~200ms TLS)
            sess.post(url, json={"recipient": {"id": sender_id}, "sender_action": "mark_seen"}, timeout=3)
            sess.post(url, json={"recipient": {"id": sender_id}, "sender_action": "typing_on"}, timeout=3)
        except: pass

    import threading
    threading.Thread(target=quick_feedback, daemon=True).start()
    
    # Use a persistent event loop instead of creating a new one per message
    if not hasattr(process_messenger_event, '_loop'):
        process_messenger_event._loop = asyncio.new_event_loop()
        def _run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        t = threading.Thread(target=_run_loop, args=(process_messenger_event._loop,), daemon=True)
        t.start()
    
    # Schedule the coroutine on the persistent loop
    try:
        future = asyncio.run_coroutine_threadsafe(
            handle_messenger_message(event, sender_id, access_token),
            process_messenger_event._loop
        )
        future.result(timeout=180)  # Max 3 min per message
    except Exception as e:
        logger.error(f"Async Bridge Error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    app.run(host="0.0.0.0", port=port)

