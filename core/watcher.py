# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import time
import logging
import subprocess
import threading
import os

logger = logging.getLogger(__name__)

_watcher_running = False
_watcher_paused = False

class PauseWatcher:
    """Context manager to temporarily pause the watcher."""
    def __enter__(self):
        global _watcher_paused
        _watcher_paused = True
        logger.info("⏸️ Antigravity watcher paused")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _watcher_paused
        _watcher_paused = False
        logger.info("▶️ Antigravity watcher resumed")

def wait_for_antigravity(timeout=60):
    """
    Wait for Antigravity process to appear.
    Returns True if found, False if timeout.
    """
    logger.info("Waiting for Antigravity to start...")
    elapsed = 0
    while elapsed < timeout:
        result = subprocess.run(
            ["pgrep", "-x", "antigravity"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            logger.info("✅ Antigravity detected and running")
            return True
        time.sleep(3)
        elapsed += 3
    
    logger.warning("⏱️ Antigravity wait timeout")
    return False

def is_antigravity_running():
    """Check if Antigravity process is running."""
    result = subprocess.run(
        ["pgrep", "-x", "antigravity"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def restart_antigravity():
    """Restart Antigravity if it's not running."""
    if is_antigravity_running():
        logger.info("Antigravity already running, no restart needed")
        return True
    
    logger.info("🔄 Restarting Antigravity...")
    try:
        # Prepare environment
        env = os.environ.copy()
        env.update({
            "DISPLAY": ":0",
            "XAUTHORITY": "/home/son/.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000"
        })
        
        # Start in new session so it persists
        subprocess.Popen(
            ["/usr/bin/antigravity"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Wait a bit and verify
        time.sleep(5)
        if is_antigravity_running():
            logger.info("✅ Antigravity restarted successfully")
            return True
        else:
            logger.error("❌ Failed to restart Antigravity: Process not found after launch")
            return False
    except Exception as e:
        logger.error(f"Error restarting Antigravity: {e}")
        return False

def watch_antigravity():
    """
    Background watcher that restarts Antigravity if it crashes.
    Runs in a separate thread.
    """
    global _watcher_running
    _watcher_running = True
    
    logger.info("🔍 Antigravity watcher started")
    
    # Check immediately instead of waiting for 120s
    if not is_antigravity_running():
        logger.warning("⚠️ Antigravity not found at startup! Attempting launch...")
        restart_antigravity()
    
    # Monitor loop
    while _watcher_running:
        time.sleep(10)  # Check every 10 seconds
        
        if not _watcher_paused and not is_antigravity_running():
            logger.warning("⚠️ Antigravity crashed or closed! Attempting restart...")
            restart_antigravity()
            time.sleep(5)  # Wait before next check

def start_watcher():
    """Start the Antigravity watcher in a background thread."""
    watcher_thread = threading.Thread(target=watch_antigravity, daemon=True)
    watcher_thread.start()
    logger.info("Watcher thread started")

def stop_watcher():
    """Stop the watcher thread."""
    global _watcher_running
    _watcher_running = False
