# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import time
import logging
import pytesseract
import cv2
import numpy as np

logger = logging.getLogger(__name__)

_temp_password = None
_awaiting_input = False

def set_awaiting_password(awaiting: bool):
    """Sets whether the system is waiting for a password input."""
    global _awaiting_input
    _awaiting_input = awaiting
    if awaiting:
        logger.info("System is now awaiting password input")

def is_awaiting_password() -> bool:
    """Checks if the system is waiting for password input."""
    return _awaiting_input

def set_password(pw: str):
    """Store password temporarily in memory."""
    global _temp_password
    _temp_password = pw

def inject_password() -> bool:
    """
    Type the stored password and wipe it immediately.
    Includes click-to-focus at screen center for Keyring/Sudo prompts.
    """
    global _temp_password, _awaiting_input

    if not _temp_password:
        return False

    try:
        import pyautogui
        
        # 1. Get screen size
        width, height = pyautogui.size()
        center_x, center_y = width // 2, height // 2
        
        # 2. Click center to ensure focus (Keyring prompts are usually centered)
        logger.info(f"Clicking center at ({center_x}, {center_y}) for focus...")
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # 3. Type password fast
        pyautogui.write(_temp_password, interval=0.01)
        pyautogui.press("enter")
        
        logger.info("Password injected successfully")
        return True
    except Exception as e:
        logger.error(f"Password injection failed: {e}")
        return False
    finally:
        # Critical: Wipe memory and reset state
        _temp_password = None
        _awaiting_input = False
