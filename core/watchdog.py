import time
import os
import subprocess
import logging
import psutil

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [WATCHDOG] - %(levelname)s - %(message)s',
    filename='/home/son/BANE/Debug/Console/watchdog.log'
)
logger = logging.getLogger(__name__)

# Configuration
SERVICES = {
    "telegram": {
        "pattern": "telegram_interface/bot.py",
        "start_cmd": ["python3", "telegram_interface/bot.py"],
        "cwd": "/home/son/BANE"
    },
    "messenger": {
        "pattern": "messenger_interface.app:app",
        "start_cmd": ["./start_messenger.sh", "prod"],
        "cwd": "/home/son/BANE"
    }
}

def is_running(pattern):
    """Check if a process matching the pattern is running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(pattern in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def restart_service(name, config):
    """Restart the specified service."""
    logger.warning(f"⚠️ Service '{name}' is DOWN. Restarting...")
    
    try:
        # Launch detached
        subprocess.Popen(
            config["start_cmd"],
            cwd=config["cwd"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        logger.info(f"✅ Service '{name}' restart triggered.")
    except Exception as e:
        logger.error(f"❌ Failed to restart '{name}': {e}")

def monitor_loop():
    logger.info("🛡️ BANE Watchdog Active. Monitoring services...")
    while True:
        for name, config in SERVICES.items():
            if not is_running(config["pattern"]):
                restart_service(name, config)
            else:
                # Optional: Health check logic (http ping) could go here
                pass
        
        time.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    monitor_loop()
