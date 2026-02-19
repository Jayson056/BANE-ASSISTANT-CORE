# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
import sys
import atexit
import asyncio
import fcntl
from datetime import datetime
from telegram_interface.bot import run_bot
from utils.startup import send_startup_notification
from core.watcher import start_watcher, wait_for_antigravity
from core.security import check_core_integrity
import subprocess

# Ensure DISPLAY is set for GUI operations (even when running as service)
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"

# --- READ-ONLY RUNTIME CHECK (Self-Defense) ---
if not check_core_integrity():
    print("\n⚠️  [SECURITY ALERT] BANE core is writable — unsafe state")
# -----------------------------------------------
if "XAUTHORITY" not in os.environ:
    os.environ["XAUTHORITY"] = "/home/son/.Xauthority"
if "XDG_RUNTIME_DIR" not in os.environ:
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

# Paths
LOG_DIR = "Debug/Console"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logging():
    """Sets up logging to console and file."""
    # Create a unique temp filename for this session
    start_time = datetime.now()
    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    temp_log_file = os.path.join(LOG_DIR, f"current_session_{start_time.strftime('%Y%m%d_%H%M%S')}.log")

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to console
            logging.FileHandler(temp_log_file, mode='w', encoding='utf-8')  # Log to file
        ],
        force=True  # Ensure this overrides any module-level basicConfig
    )
    
    return temp_log_file, start_str

def finalize_log(temp_file, start_str):
    """Renames the temp log file to include end time."""
    if not os.path.exists(temp_file):
        return

    end_time = datetime.now()
    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    safe_start = start_str.replace(":", "-").replace(" ", "_")
    safe_end = end_str.replace(":", "-").replace(" ", "_")
    
    final_name = f"consoleLog-{safe_start}_to_{safe_end}.txt"
    final_path = os.path.join(LOG_DIR, final_name)
    
    try:
        os.rename(temp_file, final_path)
        print(f"\n📝 Log saved to: {final_path}")
    except OSError as e:
        print(f"\n❌ Failed to save log: {e}")

def start_dashboard():
    """Launches the BANE dashboard in the background."""
    print("⚡ Launching BANE Dashboard...")
    try:
        dashboard_script = "/home/son/BANE/scripts/launch_dashboard.sh"
        if os.path.exists(dashboard_script):
            # Launch in background, independent of main process
            subprocess.Popen(["bash", dashboard_script], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
            print("✅ Dashboard launch triggered.")
        else:
            print(f"⚠️ Dashboard script not found at {dashboard_script}")
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")

if __name__ == "__main__":
    # Singleton check: Ensure only one instance of main.py is running
    lock_file_path = "/tmp/bane_main.lock"
    lock_file = open(lock_file_path, 'w')
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("⚠️ [ERROR] Another instance of BANE main.py is already running. Exiting.")
        sys.exit(1)

    # 🛑 CLEANUP: Kill any lingering processes on critical ports
    print("🧹 Cleaning up lingering processes...")
    subprocess.run("fuser -k 8082/tcp 5353/tcp 5454/tcp 2>/dev/null", shell=True)

    # Setup logging
    temp_log, start_str = setup_logging()
    
    # Register cleanup handler
    atexit.register(finalize_log, temp_log, start_str)
    
    # Start Antigravity watcher (waits and auto-restarts)
    print("🔍 Starting Antigravity watcher...")
    start_watcher()
    
    # Launch Dashboard
    start_dashboard()
    
    # Launch Network Watchdog
    print("🌐 Starting Network Watchdog...")
    subprocess.Popen(
        ["/home/son/BANE/.venv/bin/python3", "/home/son/BANE/core/network_watchdog.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # Launch Messenger Gateway (Gunicorn)
    print("💬 Starting Messenger Gateway on :8082...")
    try:
        messenger_log = os.path.join(LOG_DIR, "messenger_startup.log")
        with open(messenger_log, "a") as mlog:
            subprocess.Popen(
                [
                    "/home/son/BANE/.venv/bin/gunicorn",
                    "--bind", "0.0.0.0:8082",
                    "--workers", "2",
                    "--threads", "4",
                    "--timeout", "120",
                    "--access-logfile", os.path.join(LOG_DIR, "messenger_access.log"),
                    "--error-logfile", os.path.join(LOG_DIR, "messenger_error.log"),
                    "--capture-output",
                    "messenger_interface.app:app"
                ],
                stdout=mlog,
                stderr=mlog,
                cwd="/home/son/BANE",
                env={**os.environ, "PYTHONPATH": "/home/son/BANE"},
                start_new_session=True
            )
        print("✅ Messenger Gateway launched.")
    except Exception as e:
        print(f"⚠️ Messenger Gateway failed to start: {e}")
    
    # Wait for Antigravity to be ready before sending notification
    print("⏳ Waiting for Antigravity...")
    antigravity_ready = wait_for_antigravity(timeout=120)
    
    # Send startup notification
    if antigravity_ready:
        try:
            asyncio.run(send_startup_notification())
        except Exception as e:
            print(f"⚠️ Notification failed: {e}")
    else:
        print("⚠️ Starting without Antigravity (will retry in background)")
    
    # Run the bot
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        logging.error(f"Fatal Error: {e}")
        print(f"\n❌ Fatal Error: {e}")
