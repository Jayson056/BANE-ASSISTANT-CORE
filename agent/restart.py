# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import subprocess
import time
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.window import focus_antigravity
from core.watcher import PauseWatcher

logger = logging.getLogger(__name__)

ANTIGRAVITY_LAUNCH_SCRIPT = "/home/user/BANE_CORE/scripts/launch_antigravity.sh"

async def restart_antigravity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Restart the Antigravity application.
    Closes the window, waits, and relaunches it.
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    await update.message.reply_text("🔄 Closing BANE Engine...")
    
    try:
        with PauseWatcher():
            # Close ALL Antigravity windows (not just one)
            PROCESS_SEARCH = "antigravity"
            
            # Close all windows using wmctrl
            result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "antigravity" in line.lower() or "bane" in line.lower():
                    window_id = line.split()[0]
                    subprocess.run(["wmctrl", "-ic", window_id], check=False)
                    logger.info(f"Closed window: {window_id}")
            
            # Wait a moment for graceful close
            time.sleep(1)
            
            # Force kill any remaining processes
            if subprocess.run(["pgrep", "-if", PROCESS_SEARCH], stdout=subprocess.DEVNULL).returncode == 0:
                subprocess.run(["pkill", "-9", "-if", PROCESS_SEARCH], check=False)
                logger.info("Force killed remaining Antigravity processes")
                time.sleep(1)
            
            # Verify all processes are gone
            if subprocess.run(["pgrep", "-if", PROCESS_SEARCH], stdout=subprocess.DEVNULL).returncode == 0:
                logger.error("Failed to terminate all Antigravity processes")
                await update.message.reply_text("❌ Failed to close BANE Engine completely. Please close manually.")
                return

            await update.message.reply_text("⏳ Waiting 5 seconds before relaunch...")
            time.sleep(5)
            
            await update.message.reply_text("🚀 Launching BANE Engine...")
            
            # Use launch script instead of direct binary for single-instance guarantee
            subprocess.Popen([ANTIGRAVITY_LAUNCH_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            
            # Wait for window to appear (max 10 seconds)
            for i in range(10):
                await asyncio.sleep(1)
                if focus_antigravity():
                    await update.message.reply_text("✅ BANE Engine restarted successfully!")
                    return
            
        await update.message.reply_text("⚠️ BANE Engine launch started, but window not detected yet. Check if it's running.")
        
    except Exception as e:
        logger.error(f"Restart failed: {e}")
        await update.message.reply_text(f"❌ Restart failed: {e}")
