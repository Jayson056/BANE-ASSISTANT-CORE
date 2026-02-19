# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from utils.ocr_helper import run_optimized_ocr
from antigravity.window import get_antigravity_geometry

logger = logging.getLogger(__name__)

# Keywords to identify action buttons (comprehensive for full automation)
ACCEPT_KEYWORDS = ["accept", "apply", "confirm", "allow once", "allow this conversation"]
REJECT_KEYWORDS = ["reject", "dismiss", "cancel", "discard", "deny"]
ALLOW_KEYWORDS = ["allow", "access", "trust", "permit"]
ALWAYS_RUN_KEYWORDS = ["always run", "run automatically", "auto run", "always allow", "always trust"]
RUN_KEYWORDS = ["run", "execute", "proceed", "continue"]
CONFIRM_KEYWORDS = ["ok", "yes", "confirm", "trust", "proceed", "continue", "got it", "i understand"]


def detect_action_buttons():
    """
    Scan the Antigravity sidebar for ALL approval/permission buttons.
    DISABLED PER REQUEST.
    """
    return None


def _scan_for_buttons(data, scale, win_x, win_y, win_w, sidebar_offset=0.0):
    """
    Scans OCR data for action buttons. Returns detected dict or None.
    sidebar_offset: fraction of window width that was excluded from the left.
    """
    if not data or "text" not in data:
        return None
    
    detected = {}
    x_offset = int(win_w * sidebar_offset)
    
    for i, text in enumerate(data["text"]):
        text_clean = text.lower().strip()
        if not text_clean or len(text_clean) < 2:
            continue
        
        y = data["top"][i]
        x = data["left"][i]
        
        # Context window — phrases on the same line (wider range for sidebar)
        context_parts = []
        for j in range(max(0, i-3), min(len(data["text"]), i+4)):
            if abs(data["top"][j] - y) < 15:
                context_parts.append(data["text"][j].strip().lower())
        
        full_phrase = " ".join(context_parts)
        
        # Adjust coordinates: OCR returns relative to crop, add window + sidebar offset
        actual_x = int((x + data["width"][i] // 2) / scale) + win_x + x_offset
        actual_y = int((y + data["height"][i] // 2) / scale) + win_y
        
        # === DETECT ALL BUTTON TYPES ===
        
        # Accept All / Apply All
        if ("accept all" in full_phrase or "apply all" in full_phrase) and text_clean in ["accept", "apply"]:
            detected["accept_all"] = (actual_x, actual_y)
        
        # Save All
        if "save all" in full_phrase and text_clean == "save":
            detected["save_all"] = (actual_x, actual_y)
        
        # Save (standalone)
        if text_clean == "save" and "save all" not in full_phrase and "save" not in detected:
            detected["save"] = (actual_x, actual_y)
        
        # Always Allow / Always Trust
        if ("always allow" in full_phrase or "always trust" in full_phrase) and text_clean in ["always", "allow", "trust"]:
            detected["always_allow"] = (actual_x, actual_y)
        
        # Allow All
        if "allow all" in full_phrase and text_clean in ["allow", "all"]:
            detected["allow_all"] = (actual_x, actual_y)
        
        # Allow This Conversation
        if ("allow this conversation" in full_phrase or "allow conversion" in full_phrase) and text_clean in ["allow", "this", "conversation"]:
            detected["allow_conv"] = (actual_x, actual_y)
        
        # Allow Once
        if "allow once" in full_phrase and text_clean in ["allow", "once"]:
            detected["allow_once"] = (actual_x, actual_y)
        
        # Always Run / Run Automatically / Auto Run
        if any(kw in full_phrase for kw in ALWAYS_RUN_KEYWORDS) and text_clean in ["always", "run", "auto", "automatically"]:
            detected["always_run"] = (actual_x, actual_y)
        
        # Run (standalone, not "always run" or "ran command")
        if text_clean == "run" and "always" not in full_phrase and "ran" not in full_phrase:
            detected["run"] = (actual_x, actual_y)
        
        # Keep (file changes)
        if text_clean == "keep":
            detected["keep"] = (actual_x, actual_y)

        # Insert at Cursor
        if text_clean == "insert":
            detected["insert"] = (actual_x, actual_y)
        
        # Reject All
        if ("reject all" in full_phrase or "dismiss all" in full_phrase or "discard all" in full_phrase) and text_clean in ["reject", "dismiss", "discard"]:
            detected["reject_all"] = (actual_x, actual_y)
        
        # Trust
        if text_clean == "trust" and "always" not in full_phrase:
            detected["trust"] = (actual_x, actual_y)
        
        # Confirm
        if text_clean == "confirm":
            detected["confirm"] = (actual_x, actual_y)
        
        # Continue / Proceed
        if text_clean in ["continue", "proceed"]:
            detected["continue"] = (actual_x, actual_y)
        
        # OK / Yes
        if text_clean in ["ok", "yes"]:
            detected["ok"] = (actual_x, actual_y)
    
    return detected if detected else None


def is_blue_region(x, y, relaxed=False):
    """Check if the region around (x,y) contains blue pixels (VS Code button color)."""
    try:
        import pyautogui
        region = (int(x-5), int(y-5), 10, 10)
        screenshot = pyautogui.screenshot(region=region)
        
        blue_count = 0
        total_count = 0
        
        for px in screenshot.getdata():
            total_count += 1
            if len(px) >= 3:
                r, g, b = px[:3]
                if relaxed:
                    if b > r + 30 and b > g - 10 and b > 100:
                        blue_count += 1
                else:
                    if b > r + 60 and b > g + 20 and b > 140:
                        blue_count += 1
        
        is_blue = (blue_count / total_count) > 0.3
        if is_blue:
            logger.info(f"Blue button detected at {x},{y} ({blue_count}/{total_count} pixels)")
        else:
            logger.debug(f"Region at {x},{y} is NOT blue: {blue_count}/{total_count} pixels matches")
            
        return is_blue
    except Exception as e:
        logger.error(f"Color check failed: {e}")
        return True  # Be permissive if check fails


def click_button(coords):
    """
    Click at the specified coordinates.
    DISABLED PER REQUEST.
    """
    logger.warning("Auto-click attempt BLOCKED (Feature Disabled).")
    return False
