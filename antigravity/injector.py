# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import time
import logging
from antigravity.window import focus_antigravity
from antigravity.mapper import locate_input_box

logger = logging.getLogger(__name__)

from antigravity.skill_manager import get_skill_header

# Global session and cache states (lowers token consumption/io)
_cached_context = None
_session_initialized = False
_shadow_cache = {"state": None, "timestamp": 0}  # In-memory shadow state cache

def get_context():
    """Fetches and caches the skill header to avoid redundant DISK I/O."""
    global _cached_context
    if _cached_context is None:
        _cached_context = get_skill_header()
    return _cached_context

def smart_wait(seconds=0.5):
    """Refined polling wait for better UI responsiveness."""
    start = time.time()
    while time.time() - start < seconds:
        time.sleep(0.01)

def close_all_editor_tabs():
    """
    Close all open editor tabs in Antigravity to prevent:
    1. Open code files being read as AI context (extra token consumption)
    2. Code content being referenced/sent back to users in responses
    Uses VS Code keyboard shortcut: Ctrl+K, Ctrl+W (Close All Editors)
    """
    try:
        import pyautogui
        # Ctrl+K, Ctrl+W = Close All Editors in VS Code / Antigravity
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.15)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.3)
        logger.info("🧹 Closed all editor tabs before injection (token optimization)")
    except Exception as e:
        logger.warning(f"Failed to close editor tabs: {e}")

def send_to_antigravity(user_text, **kwargs):
    if kwargs:
        logger.warning(f"send_to_antigravity received extra args: {kwargs}")
    """
    Focus window, find input box, and inject text.
    Returns (success, message).
    """
    if not focus_antigravity():
        return False, "Antigravity window not found"

    # Wait for window to settle/render
    time.sleep(0.1) # Optimized from 0.3

    location = None
    for attempt in range(3):
        location = locate_input_box()
        if location:
            break
        logger.warning(f"Input box not found (attempt {attempt+1}/3). Retrying...")
        time.sleep(0.1) # Hyper-Optimized from 0.5

    if not location:
        return False, "Input box not detected after retries"

    x, y = location
    import pyautogui
    from antigravity.window import is_point_in_safe_window
    screen_width, screen_height = pyautogui.size()
    
    # 2D Editor Zone Protection (Stronger Awareness)
    editor_x_min, editor_x_max = screen_width * 0.25, screen_width * 0.75
    editor_y_min, editor_y_max = screen_height * 0.15, screen_height * 0.85
    
    if (editor_x_min < x < editor_x_max) and (editor_y_min < y < editor_y_max):
        if not is_point_in_safe_window(x, y):
            logger.error(f"🛑 Blocking injection: Target {x, y} is in forbidden Editor Zone (2D).")
            return False, "Targeting error: Refusing to paste into editor zone."
        else:
            logger.info(f"Allowing injection at {x, y} (Confirmed SAFE window)")

    try:
        import pyperclip
        
        # 1. Click to focus the input box
        pyautogui.click(x, y)
        smart_wait(0.05) # Hyper-Optimized from 0.1
        
        # 2. BANE v2 Content Construction (Shadow Refactor)
        global _session_initialized
        context = get_context()
        
        # Extract metadata from user_text (sent from router.py)
        import re
        ctx_regex = r"\[CTX\|U:([\d]+)\|P:([\w]+)\|S:([\w]+)\]"
        ctx_match = re.search(ctx_regex, user_text)
        
        if ctx_match:
            u_id, plat, s_state = ctx_match.groups()
            # Original message is between the CTX tags
            body_match = re.search(rf"{re.escape(ctx_match.group(0))}\n?(.*)\n?{re.escape(ctx_match.group(0))}", user_text, re.DOTALL)
            original_body = body_match.group(1) if body_match else user_text
            
            # --- UNIFIED METADATA ENCRYPTION (Always Protected) ---
            import base64
            inner_metadata = f"[META|U:{u_id}|P:{plat}|K:AES256]"
            # Encrypt ONLY the metadata block for Shadow OFF, or EVERYTHING for Shadow ON
            enc_meta = f"ENC[AES256]::{base64.b64encode(inner_metadata.encode('utf-8')).decode('utf-8')}"
            
            if s_state == "ON":
                # Stealth Mode: Metadata + Body together
                inner_payload = f"{inner_metadata}\n{original_body}"
                payload = base64.b64encode(inner_payload.encode("utf-8")).decode("utf-8")
                shadow_handshake = "[CTX|MODE:SHADOW|K:AES256]"
                full_text = f"{shadow_handshake}\nENC[AES256]::{payload}\n{shadow_handshake}"
                logger.info(f"🕶️ Shadow Protocol: Full stealth encryption deployed for {plat}")
            else:
                # Semi-Stealth: Encrypted Metadata + Plain Body
                full_text = (
                    f"{enc_meta}\n" # Encrypted ID/Platform
                    f"[SYSTEM: MANDATORY: You ANSWER/RESPOND SEND VIA utils/sender.py platform {plat.upper()}]\n"
                    f"{user_text}\n"
                    f"{enc_meta}"
                )
                logger.info(f"🔒 Metadata Locked: ID encrypted for {plat} (Shadow OFF)")
        else:
            full_text = user_text


        # Header only on first injection of session
        if not _session_initialized:
            full_text = f"{context}\n{full_text}"
            close_all_editor_tabs()
            _session_initialized = True
            
        # 3. Final Assembly
        pyperclip.copy(full_text)
        
        # 3. Clean and Paste (OVERWRITE MODE)
        # We select all and then paste directly — no need for backspace.
        pyautogui.hotkey('ctrl', 'a')
        smart_wait(0.05) # Optimized from 0.1
        
        pyautogui.hotkey('ctrl', 'v')
        smart_wait(0.05) # Optimized from 0.1
        
        # 4. SEND (Single Enter Execution)
        pyautogui.press("enter")
        
        return True, "Message sent to Antigravity"
    except Exception as e:
        logger.error(f"Injection failed: {e}")
        try:
            from antigravity.skill_manager import get_current_skill, update_skill_analytics
            update_skill_analytics(get_current_skill(), error=True, message=f"Injection failed: {e}")
        except:
            pass
        return False, f"Injection error: {e}"