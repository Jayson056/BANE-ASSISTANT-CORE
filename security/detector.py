# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import pytesseract
import cv2
import numpy as np
import logging
from screen.capture import capture_screen

logger = logging.getLogger(__name__)

KEYWORDS = ["password", "unlock", "authentication required", "keyring", "enter password", "default keyring"]

def detect_password_prompt() -> bool:
    """DISABLED"""
    return False

def _OLD_detect_password_prompt() -> bool:
    """
    Checks if the screen is showing a password prompt or lock screen.
    Returns True if any keyword is found.
    """
    try:
        # Capture screen directly (we can reuse screen.capture but we need raw image here usually)
        # For simplicity, let's use the file from capture_screen and read it back with cv2,
        # or just use pyautogui directly to avoid disk I/O for security if possible, 
        # but capture_screen saves to disk. Ideally detector should not save to disk for security?
        # The prompt says "runs after screen wake", so maybe transient is better.
        # But our capture_screen helper saves to disk. Let's use pyautogui directly here to avoid saving sensitive lock screen images if possible,
        # or just use capture_screen and delete it.
        
        # Let's use pyautogui directly for in-memory processing as per "No file writes" principle for passwords,
        # although this is just the detector.
        import pyautogui
        screenshot = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Simple OCR
        text = pytesseract.image_to_string(img).lower()
        
        for key in KEYWORDS:
            if key in text:
                logger.info(f"Security Alert: Detected keyword '{key}'")
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        return False
