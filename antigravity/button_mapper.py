# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from utils.ocr_helper import run_optimized_ocr
from antigravity.window import get_antigravity_geometry

logger = logging.getLogger(__name__)

# Keywords to identify action buttons
ACCEPT_KEYWORDS = ["accept", "apply", "confirm", "allow once", "allow this conversation"]
REJECT_KEYWORDS = ["reject", "dismiss", "cancel", "discard", "deny"]
ALL_KEYWORD = "all"
ALLOW_KEYWORDS = ["allow", "access"]
ALWAYS_RUN_KEYWORDS = ["always run", "run automatically", "auto run"]

def detect_action_buttons():
    """
    Scan the screen for Accept ALL and Reject ALL buttons using phrase detection.
    Optimized to find toast notifications in the bottom-right corner.
    
    DISABLED GLOBALLY PER USER REQUEST ("Pa tangal nlng") - OCR was picking up text in editor.
    """
    return None

    # OLD LOGIC BELOW (DISABLED)
    try:
        # Lazy import to support headless backend
        import pyautogui

        
        geo = get_antigravity_geometry()
        win_x, win_y = (geo[0], geo[1]) if geo else (0, 0)
        
        # Run OCR with detailed output
        # Upgrade: Use full resolution (scale 1.0) to catch small toast text
        scale = 1.0
        data = run_optimized_ocr(crop_to_window=True, downscale=scale, output_type="dict")
        
        if not data or "text" not in data:
            return None
            
        screen_width, screen_height = pyautogui.size()
        detected = {}
        
        # We search for sequences like "Accept" + "all" on the same line
        for i, text in enumerate(data["text"]):
            text_clean = text.lower().strip()
            if not text_clean:
                continue
            
            y = data["top"][i]
            x = data["left"][i]
            
            # Context window - look for a phrase on the same line
            context_parts = []
            for j in range(max(0, i-2), min(len(data["text"]), i+3)):
                if abs(data["top"][j] - y) < (15 * scale):
                    context_parts.append(data["text"][j].strip().lower())
            
            full_phrase = " ".join(context_parts)
            
            is_accept_all = "accept all" in full_phrase or "apply all" in full_phrase
            is_reject_all = "reject all" in full_phrase or "dismiss all" in full_phrase or "discard all" in full_phrase
            is_allow_once = "allow once" in full_phrase
            is_allow_conv = "allow this conversation" in full_phrase or "allow conversion" in full_phrase
            is_always_run = any(kw in full_phrase for kw in ALWAYS_RUN_KEYWORDS) or "always run" in full_phrase or "run automatically" in full_phrase

            # Adjust for scale and window
            actual_x = int((x + data["width"][i] // 2) / scale) + win_x
            actual_y = int((y + data["height"][i] // 2) / scale) + win_y
            
            # Context-aware mapping
            if is_accept_all and text_clean in ["accept", "apply"]:
                detected["accept_all"] = (actual_x, actual_y)
            
            if is_reject_all and text_clean in ["reject", "dismiss", "discard"]:
                detected["reject_all"] = (actual_x, actual_y)

            if is_allow_once and text_clean in ["allow", "once"]:
                detected["allow_once"] = (actual_x, actual_y)

            if is_allow_conv and text_clean in ["allow", "this", "conversation"]:
                detected["allow_conv"] = (actual_x, actual_y)
            
            if is_always_run and (text_clean in ["always", "run", "auto"]):
                detected["always_run"] = (actual_x, actual_y)

        if not detected:
            # Collect all candidates for "Accept All" to pick the best one (bottom-right most)
            accept_candidates = []
            
            for i, text in enumerate(data["text"]):
                text_clean = text.lower().strip()
                # Use geometry-relative coords (OCR returns relative to window crop)
                rel_x = data["left"][i]
                rel_y = data["top"][i]
                
                # Check if in bottom-right quadrant of the crop
                # Assuming window is mostly the screen, check if it's > 60% across and down
                
                # Case 1: "Accept All" on one line
                if "accept all" in text_clean:
                     actual_x = int((data["left"][i] + data["width"][i]//2) / scale) + win_x
                     actual_y = int((data["top"][i] + data["height"][i]//2) / scale) + win_y
                     accept_candidates.append((actual_x, actual_y))
                
                # Case 2: "Accept" then "All" next word
                elif text_clean == "accept":
                    if i+1 < len(data["text"]) and "all" in data["text"][i+1].lower().strip():
                        # Use the "All" word's position as it's further right (safer for button click)
                        actual_x = int((data["left"][i+1] + data["width"][i+1]//2) / scale) + win_x
                        actual_y = int((data["top"][i+1] + data["height"][i+1]//2) / scale) + win_y
                        accept_candidates.append((actual_x, actual_y))

            # Pick the best candidate: The one furthest down (Y) and right (X)
            # This avoids clicking the "Accept all changes" header text
            # PLUS: verify it's blue (VS Code button color)
            if accept_candidates:
                # Sort by Y desc, then X desc
                accept_candidates.sort(key=lambda p: (p[1], p[0]), reverse=True)
                
                logger.debug(f"Accept All candidates: {accept_candidates}")
                
                # Check for blue color to confirm it's a button
                for coords in accept_candidates:
                    if is_blue_region(coords[0], coords[1]):
                        detected["accept_all"] = coords
                        logger.info(f"Confirmed BLUE button at {coords}")
                        break
                
                # Fallback: if no blue found, take the bottom-most one anyway (risky but better than nothing)
                if "accept_all" not in detected:
                     detected["accept_all"] = accept_candidates[0]
                     logger.warning(f"No blue button found, falling back to bottom-most candidate at {accept_candidates[0]}")

        # Fallback 3: Targeted crop on Bottom-Right quadrant only (Toast Area)
        # If no valid blue button found yet, try a zoomed-in scan
        if "accept_all" not in detected:
            logger.info("Scanning bottom-right quadrant for toast...")
            
            # Define quadrant: 60% right, 60% down
            q_x = int(screen_width * 0.6)
            q_y = int(screen_height * 0.6)
            q_w = screen_width - q_x
            q_h = screen_height - q_y
            
            # Run OCR on quadrant
            data_q = run_optimized_ocr(region=(q_x, q_y, q_w, q_h), downscale=1.0, output_type="dict")
            
            if data_q and "text" in data_q:
                accept_candidates_q = []
                for i, text in enumerate(data_q["text"]):
                    text_clean = text.lower().strip()
                    
                    # Check for "Accept All" via words
                    # OCR coords are relative to crop
                    if "accept" in text_clean:
                         # Calculate absolute coords
                         abs_x = int(data_q["left"][i] + data_q["width"][i]//2) + q_x
                         abs_y = int(data_q["top"][i] + data_q["height"][i]//2) + q_y
                         accept_candidates_q.append((abs_x, abs_y))
                
                # Sort bottom-right first
                accept_candidates_q.sort(key=lambda p: (p[1], p[0]), reverse=True)
                
                for coords in accept_candidates_q:
                    # Relaxed blue check for this targeted scan
                    if is_blue_region(coords[0], coords[1], relaxed=True):
                        detected["accept_all"] = coords
                        logger.info(f"Confirmed BLUE button in quadrant at {coords}")
                        break

        if detected:
            return detected
        
        return None
        
    except Exception as e:
        logger.error(f"Button detection failed: {e}")
        return None

def is_blue_region(x, y, relaxed=False):
    """Check if the region around (x,y) contains blue pixels (VS Code button color)."""
    try:
        import pyautogui
        # Check a 10x10 area around center
        # Region must be int
        region = (int(x-5), int(y-5), 10, 10)
        screenshot = pyautogui.screenshot(region=region)
        
        blue_count = 0
        total_count = 0
        
        for px in screenshot.getdata():
            total_count += 1
            # Handle RGB or RGBA
            if len(px) >= 3:
                r, g, b = px[:3]
                
                if relaxed:
                    # Relaxed: Blue > Red + 30, Blue > Green - 10, Blue > 100
                    if b > r + 30 and b > g - 10 and b > 100:
                        blue_count += 1
                else:
                    # Strict: Blue > Red + 60, Blue > Green + 20, Blue > 140
                    if b > r + 60 and b > g + 20 and b > 140:
                        blue_count += 1
        
        # If > 30% of pixels in the 10x10 box are blue, it's the button
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
    DISABLED GLOBALLY PER USER REQUEST.
    """
    logger.info("Auto-click attempt BLOCKED (Feature Disabled).")
    return False

    # OLD LOGIC BELOW
    try:
        # Lazy import to support headless backend
        import pyautogui

        import time
        
        x, y = coords
        logger.info(f"Clicking button at ({x}, {y})")
        
        # Move to position
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.1)
        
        # Click
        pyautogui.click(x, y)
        logger.info(f"Successfully clicked at ({x}, {y})")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to click button at {coords}: {e}")
        return False
