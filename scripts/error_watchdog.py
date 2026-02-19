
# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Setup logging
LOG_DIR = "storage/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("storage/logs/error_watchdog.log")
    ]
)
logger = logging.getLogger("ErrorWatchdog")

# Add project root to path (Priority)
sys.path.insert(0, "/home/user/BANE_CORE")

# Attempt import
try:
    from antigravity.injector import send_to_antigravity
except ImportError as e:
    logger.error(f"Failed to import antigravity.injector: {e}")
    sys.exit(1)

SERVICE_NAME = "bane.service"

def get_service_status():
    try:
        res = subprocess.run(["systemctl", "is-active", SERVICE_NAME], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to check service status: {e}")
        return "unknown"

def get_recent_logs(last_cursor_file):
    """Fetch logs since the last cursor or last 30 seconds."""
    cursor = None
    if os.path.exists(last_cursor_file):
        with open(last_cursor_file, 'r') as f:
            cursor = f.read().strip()
    
    cmd = ["journalctl", "-u", SERVICE_NAME, "--no-pager", "--output=short-iso"]
    
    if cursor:
        cmd.extend(["--after-cursor", cursor])
    else:
        cmd.extend(["--since", "30 seconds ago"])
        
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.stdout
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        return ""

def update_cursor():
    """Update last cursor file with current cursor position."""
    try:
        res = subprocess.run(["journalctl", "-u", SERVICE_NAME, "-n", "0", "--show-cursor"], capture_output=True, text=True)
        # Output format: -- cursor: s=...
        line = res.stdout.strip()
        if "cursor: " in line:
            return line.split("cursor: ")[1]
    except Exception:
        pass
    return None

def analyze_and_report(logs):
    if not logs:
        return
        
    lines = logs.splitlines()
    error_buffer = []
    capture = False
    
    for line in lines:
        if "ERROR" in line or "Traceback" in line or "Exception" in line or "Failed" in line:
            capture = True
            error_buffer.append(line)
        elif capture and (line.startswith(" ") or line.startswith("\t")):
            error_buffer.append(line)
        else:
            capture = False
            
    if error_buffer:
        # Avoid huge messages
        recent_errors = "\n".join(error_buffer[-15:]) 
        prompt = f"fix me with context error:\n\n```\n{recent_errors}\n```"
        
        logger.info(f"🚨 Error detected! Sending to Antigravity:\n{prompt}")
        
        success, msg = send_to_antigravity(prompt)
        if success:
            logger.info("✅ Error report injected successfully.")
        else:
            logger.error(f"❌ Failed to inject error report: {msg}")

def main():
    logger.info("🛡️ BANE Error Watchdog Started")
    CURSOR_FILE = "storage/states/last_error_cursor.txt"
    os.makedirs(os.path.dirname(CURSOR_FILE), exist_ok=True)
    
    while True:
        try:
            status = get_service_status()
            logger.info(f"Service status: {status}")
            
            logs = get_recent_logs(CURSOR_FILE)
            if logs:
                analyze_and_report(logs)
            
            # Update cursor position
            new_cursor = update_cursor()
            if new_cursor:
                with open(CURSOR_FILE, 'w') as f:
                    f.write(new_cursor)
                    
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Watchdog crash: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
