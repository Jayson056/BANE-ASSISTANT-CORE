import json
import os
import logging
from datetime import datetime

STORAGE_FILE = "/home/son/BANE/storage/message_id_map.json"
MAX_HISTORY = 1000

logger = logging.getLogger(__name__)

def save_message(message_id, text, sender_id="system", attachments=None):
    """Saves a message ID and its content/attachments to the history map."""
    try:
        data = {}
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        
        # Add timestamp for potential cleanup/sorting
        data[message_id] = {
            "text": text,
            "sender_id": sender_id,
            "attachments": attachments or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Trim if too large
        if len(data) > MAX_HISTORY:
            # Sort by timestamp and keep pertinent ones
            # Dictionary is insertion ordered in recent python, but let's be safe
             sorted_items = sorted(data.items(), key=lambda item: item[1]['timestamp'])
             data = dict(sorted_items[-MAX_HISTORY:])
             
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to save message history: {e}")

def get_message(message_id):
    """Retrieves message content by ID."""
    try:
        if not os.path.exists(STORAGE_FILE):
            return None
            
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
            
        return data.get(message_id)
        
    except Exception as e:
        logger.error(f"Failed to retrieve message history: {e}")
        return None
