# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import os
import json
import logging
import asyncio
from datetime import datetime
from antigravity.window import get_antigravity_geometry, focus_antigravity
from antigravity.mapper import locate_input_box, CACHE_FILE
from core.watcher import is_antigravity_running, restart_antigravity

logger = logging.getLogger(__name__)

async def run_self_fix(bot, user_id):
    """
    Automated self-fix routine for Injection Errors.
    1. Check if BANE Engine is running.
    2. Recalculate input box position.
    3. Update cache.
    4. Notify user.
    """
    logger.info("🛠️ Starting automated self-fix for Injection Pipeline...")
    
    # 1. Ensure Antigravity is running and focused
    if not is_antigravity_running():
        logger.warning("Antigravity not running. Restarting...")
        restart_antigravity()
        await asyncio.sleep(8) # Wait for launch
    
    focus_antigravity()
    await asyncio.sleep(2)

    # 2. Try to locate input box using OCR
    logger.info("Recalculating input box position...")
    new_location = locate_input_box()
    
    if new_location:
        # Success - cache is already updated by locate_input_box()
        x, y = new_location
        msg = f"✅ **Automated Fix Successful!**\n\nI have recalibrated the injection pipeline.\n\n📍 **New Target:** `{x, y}`\n🛡️ **Status:** Injection bypass active.\n\nYou can now retry your last command."
        logger.info(f"Self-fix successful. New location: {new_location}")
    else:
        # Fallback to geometry-based sidebar position
        logger.warning("OCR failed during fix. Falling back to geometry-based position.")
        geom = get_antigravity_geometry()
        if geom:
            wx, wy, ww, wh = geom
            # Best guess: Bottom center of the right sidebar
            fallback_x = wx + ww - (ww // 8)
            fallback_y = wy + wh - 80
            
            # Manually update cache
            try:
                os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                with open(CACHE_FILE, 'w') as f:
                    json.dump({"last_x": int(fallback_x), "last_y": int(fallback_y)}, f)
                msg = f"⚠️ **Recalibration Partial**\n\nOCR failed to find keywords, so I used a layout-based fallback.\n\n📍 **Target:** `{fallback_x, fallback_y}`\n\nIf injection still fails, please ensure the BANE Engine sidebar is visible."
            except Exception as e:
                msg = f"❌ **Automated Fix Failed**\n\nFailed to update cache: `{str(e)}`"
        else:
            msg = "❌ **Automated Fix Failed**\n\nCould not detect any active BANE Engine or Manager window."

    # 3. Notify User
    try:
        await bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send fix notification: {e}")

def monitor_bot_status():
    """Placeholder for future 24/7 internal monitoring hooks."""
    pass
