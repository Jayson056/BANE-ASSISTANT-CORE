#!/usr/bin/env python3
"""
BANE Messenger Health Monitor
Runs periodic checks on the Messenger Gateway and restarts if unresponsive.
"""

import requests
import subprocess
import time
import logging
import sys
import os
from datetime import datetime

# Configuration
GATEWAY_URL = "http://127.0.0.1:8082/"
CHECK_INTERVAL = 60        # Seconds between checks
FAILURE_THRESHOLD = 3      # Consecutive failures before restart
REQUEST_TIMEOUT = 10       # Seconds to wait for response
SERVICE_NAME = "bane-messenger"

LOG_DIR = "/home/user/BANE_CORE/Debug/Console"
LOG_FILE = os.path.join(LOG_DIR, "messenger_health.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HEALTH] %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger("messenger_health")

# Status tracker
STATUS_FILE = "/home/user/BANE_CORE/storage/messenger_status.json"

def update_status(status: str, details: str = ""):
    """Write current health status to a JSON file for dashboard consumption."""
    import json
    data = {
        "service": "messenger_gateway",
        "status": status,
        "details": details,
        "last_check": datetime.now().isoformat(),
        "uptime_url": GATEWAY_URL
    }
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write status file: {e}")


def check_health() -> bool:
    """Ping the Messenger Gateway and return True if healthy."""
    try:
        resp = requests.get(GATEWAY_URL, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return True
        logger.warning(f"Unhealthy response: HTTP {resp.status_code}")
        return False
    except requests.ConnectionError:
        logger.warning("Connection refused — gateway may be down.")
        return False
    except requests.Timeout:
        logger.warning("Request timed out — gateway may be stalled.")
        return False
    except Exception as e:
        logger.warning(f"Unexpected health check error: {e}")
        return False


def restart_service():
    """Attempt to restart the Messenger Gateway via systemd."""
    logger.info(f"Restarting {SERVICE_NAME}...")
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", SERVICE_NAME],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            logger.info("Service restarted successfully.")
            update_status("restarting", "Auto-restart triggered by health monitor")
        else:
            logger.error(f"Restart failed: {result.stderr.strip()}")
            update_status("error", f"Restart failed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error("Restart command timed out.")
        update_status("error", "Restart command timed out")
    except Exception as e:
        logger.error(f"Failed to restart: {e}")
        update_status("error", str(e))


def run_monitor():
    """Main health monitor loop."""
    logger.info("Messenger Health Monitor started.")
    consecutive_failures = 0

    while True:
        healthy = check_health()

        if healthy:
            if consecutive_failures > 0:
                logger.info("Gateway recovered.")
            consecutive_failures = 0
            update_status("healthy", "All checks passing")
        else:
            consecutive_failures += 1
            logger.warning(f"Failure {consecutive_failures}/{FAILURE_THRESHOLD}")
            update_status("degraded", f"Failure {consecutive_failures}/{FAILURE_THRESHOLD}")

            if consecutive_failures >= FAILURE_THRESHOLD:
                restart_service()
                consecutive_failures = 0
                time.sleep(15)  # Grace period after restart
                continue

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        run_monitor()
    except KeyboardInterrupt:
        logger.info("Health Monitor stopped by user.")
        update_status("stopped", "Manual shutdown")
    except Exception as e:
        logger.critical(f"Monitor crashed: {e}")
        update_status("error", f"Monitor crashed: {e}")
