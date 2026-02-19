# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import pytesseract
import cv2
import numpy as np
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load sudo password from secrets
load_dotenv("/home/user/BANE_CORE/config/secrets.env")
SUDO_PASSWORD = os.getenv("SUDO_PASSWORD", "")

KEYWORDS = ["password", "unlock", "authentication required", "keyring",
            "enter password", "default keyring", "[sudo]", "password for"]

def detect_password_prompt() -> bool:
    """
    Checks if the screen is showing a password/sudo prompt.
    Uses in-memory OCR (no disk writes for security).
    """
    try:
        import pyautogui
        from utils.ocr_helper import run_optimized_ocr
        
        text = run_optimized_ocr(crop_to_window=True, downscale=0.5, output_type="string")
        text_lower = text.lower()
        
        for key in KEYWORDS:
            if key in text_lower:
                logger.info(f"🔐 Password prompt detected: keyword '{key}'")
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Password detection failed: {e}")
        return False

def auto_inject_sudo():
    """
    Automatically inject sudo password when a prompt is detected.
    Password is loaded from secrets.env, never hardcoded.
    """
    if not SUDO_PASSWORD:
        logger.warning("SUDO_PASSWORD not set in secrets.env, cannot auto-inject")
        return False
    
    try:
        import pyautogui
        import time
        
        # Type password into the active terminal/prompt
        pyautogui.write(SUDO_PASSWORD, interval=0.02)
        pyautogui.press("enter")
        
        logger.info("🔐 Sudo password auto-injected successfully")
        return True
    except Exception as e:
        logger.error(f"Sudo auto-injection failed: {e}")
        return False
