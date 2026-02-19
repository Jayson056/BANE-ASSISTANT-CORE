# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
from utils.ocr_helper import run_optimized_ocr

logger = logging.getLogger(__name__)

# Keywords that indicate the AI is currently generating a response
BUSY_KEYWORDS = ["Thinking", "Progress", "Loading", "Load", "Progress", "Query", "Thought", "Generating", "Writing"]

# Keywords that indicate a quota or error state
ERROR_KEYWORDS = ["quota reached", "rate limit", "api error", "limit reached", "unavailable", "something went wrong"]

def detect_state():
    """
    Analyzes the screen to determine the current state of Antigravity.
    Returns: 'busy', 'error', or 'idle'.
    """
    try:
        # Run optimized OCR (locked, cropped, downscaled)
        text_data = run_optimized_ocr(crop_to_window=True, downscale=0.3).lower()
        
        if not text_data:
            return "idle"

        # Check for error/quota first (higher priority)
        for keyword in ERROR_KEYWORDS:
            if keyword in text_data:
                logger.warning(f"Detected error state via keyword: {keyword}")
                return "error"
        
        # Check for busy state
        for keyword in BUSY_KEYWORDS:
            if keyword in text_data:
                logger.info(f"Detected busy state via keyword: {keyword}")
                return "busy"
        
        return "idle"
        
    except Exception as e:
        logger.error(f"State detection failed: {e}")
        return "idle" # Fallback to idle to avoid blocking the bot

def is_busy():
    """Helper to check specifically if the bot is busy."""
    return detect_state() == "busy"

def get_error_details():
    """Attempts to extract more specific error text if in error state."""
    try:
        text_data = run_optimized_ocr(crop_to_window=True, downscale=0.3)
        
        # Find the line containing error keywords
        lines = text_data.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ERROR_KEYWORDS):
                return line.strip()
        
        return "Unknown error detected in Antigravity UI."
    except:
        return "An error occurred while communicating with Antigravity."
