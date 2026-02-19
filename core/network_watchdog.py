
import asyncio
import logging
import subprocess
import time
import sys
import os
sys.path.append("/home/son/BANE") # Ensure root path is available 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NetworkWatchdog")

# Load Secrets for Notification
from dotenv import load_dotenv
load_dotenv("/home/son/BANE/config/secrets.env")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# Configuration
CHECK_INTERVAL = 30  # Seconds between checks
PING_TARGET = "8.8.8.8"
MAX_FAILURES = 3

async def check_connection():
    """Ping Google DNS to check for internet connectivity."""
    try:
        # Ping with 3 packets, 2 second timeout
        response = subprocess.run(
            ["ping", "-c", "3", "-W", "2", PING_TARGET],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return response.returncode == 0
    except Exception as e:
        logger.error(f"Ping failed with error: {e}")
        return False

async def attempt_fix():
    """Attempt to autonomously fix the network connection."""
    logger.warning("Attempting autonomous network repair...")
    
    # Method 1: Restart NetworkManager (requires sudo password automation if not root)
    # Since we are 'son', we might need to use the stored sudo password or a safer method.
    # 'nmcli networking off/on' usually doesn't need root if user is in plugdev/netdev group.
    
    try:
        logger.info("Cycling networking via nmcli...")
        subprocess.run(["nmcli", "networking", "off"], check=False)
        await asyncio.sleep(2)
        subprocess.run(["nmcli", "networking", "on"], check=False)
        await asyncio.sleep(10) # Wait for DHCP
        
        if await check_connection():
            logger.info("Network recovered via nmcli cycle.")
            return True
            
    except FileNotFoundError:
        logger.error("nmcli not found, skipping Method 1.")

    return False

async def notify_user(message):
    """Send notification via Telegram script."""
    try:
        if not TELEGRAM_USER_ID:
            logger.warning("No TELEGRAM_USER_ID found, skipping notification.")
            return

        cmd = [
            "/home/son/BANE/.venv/bin/python3",
            "/home/son/BANE/utils/sender.py",
            "--platform", "telegram",
            "--recipient_id", TELEGRAM_USER_ID,
            "--text", message
        ]
        subprocess.Popen(cmd)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

async def run_watchdog():
    logger.info("Network Watchdog Started.")
    failures = 0
    was_down = False
    
    while True:
        is_connected = await check_connection()
        
        if is_connected:
            if was_down:
                logger.info("Network is back online.")
                await notify_user("✅ **System Alert**\n\nNetwork is synchronized. Connectivity has been restored.")
                was_down = False
                failures = 0
            else:
                failures = 0 # Reset counter on success
        else:
            failures += 1
            logger.warning(f"Network check failed ({failures}/{MAX_FAILURES})")
            
            if failures >= MAX_FAILURES and not was_down:
                logger.error("Confirmed network outage. Initiating repair protocols...")
                was_down = True
                
                # Attempt Fix
                success = await attempt_fix()
                if success:
                    # notify_user call will happen in next is_connected check
                    failures = 0 
                else:
                    logger.error("Autonomous repair failed. Retrying in next cycle.")

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(run_watchdog())
    except KeyboardInterrupt:
        logger.info("Watchdog stopped.")
