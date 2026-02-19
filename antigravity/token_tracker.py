# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

import os
import glob
import time
import logging

logger = logging.getLogger(__name__)

class TokenTracker:
    def __init__(self):
        self.conv_dir = os.path.expanduser("~/.gemini/antigravity/conversations")
        self.last_file = None
        self.last_count = 0
        self.session_total = 0
        self.start_time = time.time()

    def extract_printable_text(self, file_path):
        """Extracts printable text from .pb files using a heuristic filter."""
        try:
            if not os.path.exists(file_path):
                return ""
            
            with open(file_path, "rb") as f:
                buffer = f.read()
            
            filtered = bytearray()
            for b in buffer:
                # Printable ASCII (32-126), tabs (9), LF (10), CR (13), or UTF-8 high bits (>=128)
                if (32 <= b <= 126) or b in [9, 10, 13] or b >= 128:
                    filtered.append(b)
            
            return filtered.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Error parsing .pb file: {e}")
            return ""

    def estimate_tokens(self, text):
        """
        Estimates token count for programming/chat text.
        Heuristic: ~3.7 characters per token for high-information density text.
        """
        if not text:
            return 0
        
        # Tiktoken's cl100k_base usually averages 3.5 to 4 chars per token.
        # We also count special characters as more 'token-dense'.
        char_count = len(text)
        
        # Count non-alphanumeric chars (potential token breakers)
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        
        # Weighted estimate
        estimate = (char_count / 3.9) + (special_chars / 1.5)
        return int(estimate)

    def get_latest_stats(self):
        """Scans for updates and returns current metrics."""
        pb_files = glob.glob(os.path.join(self.conv_dir, "*.pb"))
        if not pb_files:
            return {"session_total": 0, "last_delta": 0, "current_file": None}
        
        # Get latest modified file
        pb_files.sort(key=os.path.getmtime, reverse=True)
        latest_file = pb_files[0]
        
        text = self.extract_printable_text(latest_file)
        current_count = self.estimate_tokens(text)
        
        delta = 0
        if self.last_file == latest_file:
            # Same file, check for growth
            if current_count > self.last_count:
                delta = current_count - self.last_count
                self.session_total += delta
        else:
            # New file detected
            # We treat the first scan of a new file as the baseline
            # subsequent increases in this file will be added to the session total
            self.last_file = latest_file
            delta = 0 # Don't add baseline to session total to avoid giant jumps
        
        self.last_count = current_count
        
        return {
            "session_total": self.session_total,
            "last_delta": delta,
            "current_file_tokens": current_count,
            "filename": os.path.basename(latest_file)
        }

# Singleton instance
tracker = TokenTracker()

def get_token_metrics():
    return tracker.get_latest_stats()
