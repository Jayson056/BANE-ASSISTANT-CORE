# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
import json
from utils.ocr_helper import run_optimized_ocr
from antigravity.window import get_antigravity_geometry

logger = logging.getLogger(__name__)

CACHE_FILE = "/home/son/BANE/storage/mapper_cache.json"
KEYWORDS = [
    "ask anything", 
    "@ to mention", 
    "/ for workflows", 
    "ctrl+l", 
    "ask anything, @ to mention, / for workflows"
]
OFFSET_Y = 10  # Pixels within/near the label to click

def locate_input_box():
    """
    Capture screen, run OCR, and find the input box coordinates.
    Returns (x, y) tuple or None.
    """
    try:
        # Lazy import to support headless backend
        import pyautogui
        
        # 1. Get window geometry to adjust coordinates later
        geo = get_antigravity_geometry()
        win_x, win_y = (geo[0], geo[1]) if geo else (0, 0)
        
        # 2. Run optimized OCR (dict mode)
        # We use a slight downscale (0.4) for better speed in mapping vs previous 0.8
        scale = 0.4
        data = run_optimized_ocr(crop_to_window=True, downscale=scale, output_type="dict")

        if not data or "text" not in data:
            return _try_cache_or_fallback()

        screen_width, screen_height = pyautogui.size()
        
        matches = []
        for i, text in enumerate(data["text"]):
            text_clean = text.lower().strip()
            if not text_clean:
                continue
            
            # Context words for phrase matching
            context_window = 6
            context_words = data["text"][max(0, i-2):i+context_window]
            context_phrase = " ".join([w.lower().strip() for w in context_words if w.strip()]).strip()
            
            match_found = False
            phrase_normalized = context_phrase.replace(" ", "")
            for kw in KEYWORDS:
                kw_normalized = kw.lower().replace(" ", "")
                if kw_normalized in phrase_normalized:
                    match_found = True
                    break
            
            if not match_found:
                if "ask" in text_clean and ("any" in context_phrase or "thing" in context_phrase):
                    match_found = True
                elif "type" in text_clean and "your" in context_phrase:
                    match_found = True
                elif "mention" in context_phrase or "workflows" in context_phrase:
                    match_found = True

            if match_found:
                # IMPORTANT: Adjust for downscaling and window cropping
                x = int((data["left"][i] / scale) + win_x)
                y = int((data["top"][i] / scale) + win_y)
                width = int(data["width"][i] / scale)
                height = int(data["height"][i] / scale)
                
                # Center the click
                input_x = x + width // 2
                input_y = y + height // 2
                
                # ─── REJECTION LOGIC ───
                from antigravity.window import is_point_in_safe_window
                if (screen_width * 0.25) < input_x < (screen_width * 0.75):
                    if not is_point_in_safe_window(input_x, input_y):
                        continue
                
                if input_y < (screen_height * 0.4):
                    continue
                if "save" in context_phrase:
                    continue
                if input_y > (screen_height - 60):
                    continue

                # ─── SCORING LOGIC ───
                score = 0
                if input_x > screen_width * 0.65:
                    score += 10000 
                if input_y > screen_height * 0.75:
                    score += 5000
                elif input_y > screen_height * 0.5:
                    score += 1000
                
                if "ask anything" in context_phrase:
                    score += 2000
                if "@ to mention" in context_phrase:
                    score += 2000
                if "workflows" in context_phrase:
                    score += 2000
                if "ask anything, @ to mention, / for workflows" in context_phrase.replace(",", ""):
                    score += 10000 

                matches.append({
                    "coords": (input_x, input_y),
                    "phrase": context_phrase,
                    "score": score
                })

        if matches:
            best_match = max(matches, key=lambda m: m["score"])
            logger.info(f"Input box found at {best_match['coords']} (score: {best_match['score']})")
            
            # Save to cache
            try:
                os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                with open(CACHE_FILE, 'w') as f:
                    json.dump({"last_x": int(best_match['coords'][0]), "last_y": int(best_match['coords'][1])}, f)
            except:
                pass
                
            return best_match["coords"]

        return _try_cache_or_fallback()

    except Exception as e:
        logger.error(f"OCR mapping failed: {e}")
        return None

def _try_cache_or_fallback():
    """Internal helper for cache/layout fallback."""
    import pyautogui
    screen_width, screen_height = pyautogui.size()
    
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                logger.info(f"Using cached input box location: ({cache['last_x']}, {cache['last_y']})")
                return (cache['last_x'], cache['last_y'])
        except:
            pass

    # Fallback 2: Hard-coded Sidebar location
    logger.warning("Input box keywords not found. Using layout fallback.")
    sidebar_x = screen_width - (screen_width // 6) 
    sidebar_y = screen_height - 100
    return (sidebar_x, sidebar_y)