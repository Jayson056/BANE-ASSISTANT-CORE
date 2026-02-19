# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = "storage/screenshots"

def capture_screen():
    """
    Capture the screen and save to storage.
    Returns the absolute path to the screenshot file.
    """
    # Lazy import to support headless backend
    import pyautogui
    
    try:
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{SCREENSHOTS_DIR}/screen_{timestamp}.png"
        
        # Taking screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        logger.info(f"Screenshot saved to {filename}")
        return os.path.abspath(filename)

    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return None
