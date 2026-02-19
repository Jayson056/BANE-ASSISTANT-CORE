# BANE - OCR Optimization Helper
# Centralizes OCR calls to provide locking, downscaling, and window-cropping
import logging
import pytesseract
import cv2
import numpy as np
import os
import time
from antigravity.window import get_antigravity_geometry

logger = logging.getLogger(__name__)

# File-based lock to prevent multiple Tesseract instances from running in parallel
# across DIFFERENT processes (e.g. Gunicorn workers + main.py)
OCR_LOCK_FILE = "/tmp/bane_ocr.lock"

def get_optimized_screenshot(crop_to_window=True, downscale=0.3, exclude_left_percent=0.0, exclude_bottom_percent=0.0):
    """
    Captures a screenshot, optionally crops to the Antigravity window/sub-region,
    and downscales for faster OCR processing.
    """
    try:
        import pyautogui
        
        # 1. Take raw screenshot
        screenshot = pyautogui.screenshot()
        img_np = np.array(screenshot)
        
        # 2. Crop to window if requested
        if crop_to_window:
            geo = get_antigravity_geometry()
            if geo:
                x, y, w, h = geo
                scr_w, scr_h = screenshot.size
                
                # Exclude left sidebar if requested
                if exclude_left_percent > 0:
                    offset = int(w * exclude_left_percent)
                    x += offset
                    w -= offset

                # Exclude bottom input box/status bar if requested
                if exclude_bottom_percent > 0:
                    h -= int(h * exclude_bottom_percent)
                
                x1 = max(0, x)
                y1 = max(0, y)
                x2 = min(scr_w, x + w)
                y2 = min(scr_h, y + h)
                
                if x2 > x1 and y2 > y1:
                    img_np = img_np[y1:y2, x1:x2]
        
        # 3. Convert to grayscale
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # 4. Downscale
        if downscale < 1.0:
            width = int(img_gray.shape[1] * downscale)
            height = int(img_gray.shape[0] * downscale)
            img_gray = cv2.resize(img_gray, (width, height), interpolation=cv2.INTER_AREA)
            
        return img_gray
    except Exception as e:
        logger.error(f"Screenshot/Preprocessing failed: {e}")
        return None

def run_optimized_ocr(crop_to_window=True, downscale=0.3, output_type="string", config="", exclude_left_percent=0.0, exclude_bottom_percent=0.0):
    """
    Runs OCR under a cross-process lock with image optimization.
    """
    # Simple file lock implementation
    lock_acquired = acquire_lock()
    if not lock_acquired:
        return "" if output_type == "string" else {}

    try:
        img = get_optimized_screenshot(crop_to_window, downscale, exclude_left_percent, exclude_bottom_percent)
        if img is None:
            return "" if output_type == "string" else {}
        
        if output_type == "string":
            return pytesseract.image_to_string(img, config=config)
        else:
            return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
    except Exception as e:
        logger.error(f"Tesseract execution failed: {e}")
        return "" if output_type == "string" else {}
    finally:
        release_lock()

def acquire_lock():
    """Acquires the cross-process OCR lock."""
    max_wait = 10 
    wait_step = 0.5
    waited = 0
    while waited < max_wait:
        try:
            fd = os.open(OCR_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return True
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(OCR_LOCK_FILE) > 30:
                    os.remove(OCR_LOCK_FILE)
            except: pass
            time.sleep(wait_step)
            waited += wait_step
    logger.warning("OCR Lock acquisition timed out.")
    return False

def release_lock():
    """Releases the cross-process OCR lock."""
    try:
        if os.path.exists(OCR_LOCK_FILE):
            os.remove(OCR_LOCK_FILE)
    except:
        pass

def image_to_string_locked(img, config=""):
    """Wrapper for pytesseract.image_to_string with cross-process locking."""
    if acquire_lock():
        try:
            return pytesseract.image_to_string(img, config=config)
        finally:
            release_lock()
    return ""

def image_to_data_locked(img, config=""):
    """Wrapper for pytesseract.image_to_data with cross-process locking."""
    if acquire_lock():
        try:
            return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
        finally:
            release_lock()
    return {}
