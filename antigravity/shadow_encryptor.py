# BANE Shadow Protocol - Encryption Engine
# Real AES-256 via cryptography.Fernet (symmetric encryption)
import json
import os
import logging

logger = logging.getLogger(__name__)

STATE_FILE = "/home/user/BANE_CORE_Workspaces/USER-DATA/9eb397f15a125a6d/shadow_state.json"
PREFIX = "ENC[AES256]::"

def _get_fernet():
    """Load Fernet key from secrets.env securely."""
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path="/home/user/BANE_CORE/config/secrets.env")
        key = os.getenv("SHADOW_KEY")
        if not key:
            logger.warning("SHADOW_KEY not found in secrets.env, falling back to base64")
            return None
        from cryptography.fernet import Fernet
        return Fernet(key.encode('utf-8'))
    except Exception as e:
        logger.warning(f"Fernet init failed: {e}")
        return None

def is_shadow_active():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("shadow_mode", False)
        except Exception as e:
            logger.warning(f"Shadow state read failed: {e}")
            return False
    return False

def encrypt_text(text):
    if not text:
        return text
    fernet = _get_fernet()
    if fernet:
        # Real AES-256 encryption via Fernet
        encrypted = fernet.encrypt(text.encode('utf-8')).decode('utf-8')
        return f"{PREFIX}{encrypted}"
    else:
        # Fallback to base64 if key missing (backward compat)
        import base64
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return f"{PREFIX}{encoded}"

def decrypt_text(text):
    if not text:
        return text
    
    import re
    # Search for ALL ENC tags. We want the LAST one (most recent response in OCR capture)
    # Include - and _ for URL-safe base64 (Fernet tokens)
    matches = re.findall(r"ENC\[AES256\]::([A-Za-z0-9+/=\-_| ]+)", text)
    
    if matches:
        # Take the last match (the AI response, vs the user prompt which appears earlier)
        raw_encoded = matches[-1]
        
        # Clean up common OCR artifacts in the base64 blob
        # Preserve all valid Base64 and URL-safe Base64 chars (+, /, -, _)
        encoded = re.sub(r"[^A-Za-z0-9+/=\-_]", "", raw_encoded)
        
        if not encoded:
            return text

        # Try Fernet first
        fernet = _get_fernet()
        if fernet:
            try:
                # Fernet works with both standard and URL-safe base64 input
                decoded = fernet.decrypt(encoded.encode('utf-8')).decode('utf-8')
                return decoded
            except Exception:
                pass
                
        # Fallback to base64 for legacy or simple payloads
        try:
            import base64
            # Add padding if OCR cut it off
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += '=' * (4 - missing_padding)
            
            # Handle both standard and URL-safe base64
            try:
                decoded = base64.b64decode(encoded).decode('utf-8')
            except:
                decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
            return decoded
        except Exception:
            pass
            
    return text

def set_shadow_state(active: bool):
    """Toggle shadow mode on/off."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump({"shadow_mode": active}, f)
        # FIX #4: Secure permissions (owner only)
        os.chmod(STATE_FILE, 0o600)
        return True
    except Exception as e:
        logger.error(f"Failed to set shadow state: {e}")
        return False
