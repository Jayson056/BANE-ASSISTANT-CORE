#EDITED BY: SON

# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

import logging
import pytesseract
import cv2
import numpy as np
import time
import re

logger = logging.getLogger(__name__)

# --------------------------------------------------
# MODEL DEFINITIONS (CANONICAL)
# --------------------------------------------------

ALL_MODELS = [
    "Gemini 3 Pro (High)",
    "Gemini 3 Pro (Low)",
    "Gemini 3 Flash",
    "Claude Sonnet 4.5",
    "Claude Sonnet 4.5 (Thinking)",
    "Claude Opus 4.5 (Thinking)",
    "GPT-OSS 120B (Medium)",
]

# --------------------------------------------------
# SAFETY HELPERS
# --------------------------------------------------

def sanitize_text(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    text = re.sub(r"[*_`\[\]()<>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def normalize_model_name(raw: str) -> str:
    raw_lower = raw.lower()
    
    # 1. Exact or clear substring matching first
    for model in ALL_MODELS:
        m_lower = model.lower()
        if m_lower in raw_lower:
            return model
            
    # 2. Fuzzy checks for specific models
    if "gemini" in raw_lower:
        if "pro" in raw_lower:
            if "low" in raw_lower: return "Gemini 3 Pro (Low)"
            return "Gemini 3 Pro (High)" # Default pro
        if "flash" in raw_lower: return "Gemini 3 Flash"
        return "Gemini 3 Pro (High)"

    if "claude" in raw_lower or "laude" in raw_lower:
        if "opus" in raw_lower: return "Claude Opus 4.5 (Thinking)"
        if "think" in raw_lower: return "Claude Sonnet 4.5 (Thinking)"
        return "Claude Sonnet 4.5"

    if "gpt" in raw_lower or "oss" in raw_lower:
        return "GPT-OSS 120B (Medium)"
    
    return raw


# --------------------------------------------------
# UI INTERACTION CORE
# --------------------------------------------------

def click_model_dropdown():
    """
    Opens the model selector dropdown in the Antigravity UI.
    Uses window geometry for precise targeting.
    """
    try:
        import pyautogui
        from antigravity.window import focus_antigravity, get_antigravity_geometry
        
        focus_antigravity()
        time.sleep(0.5)

        geom = get_antigravity_geometry()
        if not geom:
            logger.error("Could not determine Antigravity window geometry.")
            # Absolute fallback
            pyautogui.click(640, 600) 
            return True, "Unknown"

        xw, yw, ww, hw = geom
        
        # Take screenshot and crop to window
        screenshot = pyautogui.screenshot()
        img_full = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        img = img_full[yw:yw+hw, xw:xw+ww]
        
        # OCR on window only
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 3')

        # 1. Look for "Select another model" or "Switch"
        for i, text in enumerate(data["text"]):
            t = text.lower().strip()
            if t in ["select", "another", "switch"]:
                # Check line context
                line_text = " ".join([data["text"][j].lower() for j in range(max(0, i-3), min(len(data["text"]), i+4))])
                if "select another" in line_text or "switch model" in line_text:
                    x = xw + data["left"][i] + data["width"][i] // 2
                    y = yw + data["top"][i] + data["height"][i] // 2
                    pyautogui.click(x, y)
                    logger.info(f"Clicked switch button in quota box at ({x}, {y})")
                    return True, normalize_model_name(line_text)

        # 2. Look for current model in the bottom bar (Y > 80% of window height)
        for i, text in enumerate(data["text"]):
            t = text.lower().strip()
            # If we see any part of a model name in the bottom area
            if any(k in t for k in ["gemini", "claude", "gpt", "oss", "laude", "sonnet"]):
                item_y = data["top"][i]
                if item_y > hw * 0.7:
                    x = xw + data["left"][i] + data["width"][i] // 2
                    y = yw + data["top"][i] + data["height"][i] // 2
                    pyautogui.click(x, y)
                    
                    # Get full name from context
                    context = " ".join([data["text"][j] for j in range(max(0, i-4), min(len(data["text"]), i+5))])
                    model = normalize_model_name(context)
                    logger.info(f"Clicked model selector '{model}' at ({x}, {y})")
                    return True, model

        # Fallback: Bottom-Left of window (typical model selector position)
        fx, fy = xw + 150, yw + hw - 50
        pyautogui.click(fx, fy)
        logger.warning(f"Fallback click at window bottom-left: ({fx}, {fy})")
        return True, "Unknown (Fallback)"

    except Exception as e:
        logger.error(f"Dropdown click failed: {e}")
        return False, "Unknown"


# --------------------------------------------------
# AVAILABLE MODELS DETECTION
# --------------------------------------------------

def get_available_models():
    """
    Returns: (current_model, [{name, is_limited, coords}])
    """
    try:
        import pyautogui
        from antigravity.window import get_antigravity_geometry
        from antigravity.quota_detector import detect_warning_icons

        success, current_model = click_model_dropdown()
        if not success:
            return current_model, []

        time.sleep(0.8) # Wait for animation
        
        geom = get_antigravity_geometry()
        xw, yw, ww, hw = geom or (0,0,1920,1080)

        screenshot = pyautogui.screenshot()
        img_full = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        img = img_full[yw:yw+hw, xw:xw+ww] if geom else img_full
        
        # Use PSM 6 for list blocks
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 6')
        warnings = detect_warning_icons() # Full screen scan for warnings is fine

        detected = []
        seen = set()

        for i, text in enumerate(data["text"]):
            t = text.lower().strip()
            if len(t) < 3: continue

            if any(k in t for k in ["gemini", "claude", "gpt", "oss", "sonnet", "opus"]):
                y_local = data["top"][i]
                context = " ".join([data["text"][j] for j in range(max(0, i-5), min(len(data["text"]), i+6)) if abs(data["top"][j] - y_local) < 20])
                name = normalize_model_name(sanitize_text(context))
                
                if name in ALL_MODELS and name not in seen:
                    abs_x = xw + data["left"][i] + data["width"][i] // 2
                    abs_y = yw + data["top"][i] + data["height"][i] // 2
                    
                    is_limited = any(((wx - abs_x)**2 + (wy - abs_y)**2)**0.5 < 100 for wx, wy in warnings)
                    
                    detected.append({"name": name, "is_limited": is_limited, "coords": (abs_x, abs_y)})
                    seen.add(name)

        pyautogui.press("escape")
        time.sleep(0.2)
        pyautogui.press("escape")
        
        return normalize_model_name(current_model), detected

    except Exception as e:
        logger.error(f"Detection failed: {e}")
        return "Unknown", []


# --------------------------------------------------
# MODEL SELECTION
# --------------------------------------------------

def select_model_by_name(model_name):
    """
    Switches to the requested model.
    """
    try:
        import pyautogui
        from antigravity.window import get_antigravity_geometry
        from antigravity.quota_detector import detect_warning_icons

        # 1. Open dropdown
        success, _ = click_model_dropdown()
        if not success: return False, False, "Failed to open menu."
        
        time.sleep(0.6)

        # 2. Capture and Scan
        geom = get_antigravity_geometry()
        xw, yw, ww, hw = geom or (0,0,1920,1080)
        
        screenshot = pyautogui.screenshot()
        img_full = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        img = img_full[yw:yw+hw, xw:xw+ww] if geom else img_full
        
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 6')
        warnings = detect_warning_icons()
        
        target = model_name
        
        for i, text in enumerate(data["text"]):
            t = text.lower().strip()
            if len(t) < 3: continue
            
            y_local = data["top"][i]
            context = " ".join([data["text"][j] for j in range(max(0, i-5), min(len(data["text"]), i+6)) if abs(data["top"][j] - y_local) < 20])
            found_name = normalize_model_name(sanitize_text(context))
            
            if found_name == target:
                abs_x = xw + data["left"][i] + data["width"][i] // 2
                abs_y = yw + data["top"][i] + data["height"][i] // 2
                
                pyautogui.click(abs_x, abs_y)
                
                is_limited = any(((wx - abs_x)**2 + (wy - abs_y)**2)**0.5 < 100 for wx, wy in warnings)
                return True, is_limited, f"Switched to {target}."

        pyautogui.press("escape")
        return False, False, f"Model '{target}' not found in the list."

    except Exception as e:
        logger.error(f"Selection failed: {e}")
        return False, False, str(e)