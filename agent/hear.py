# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import asyncio
import os
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

RECORDINGS_DIR = "storage/recordings"

async def hear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Record audio for a duration.
    Usage: /hear [seconds] [device]
    Example: /hear 10 (default) or /hear 10 hw:1,0
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    text = update.message.text
    parts = text.split()
    
    duration = 10
    device = None
    
    if len(parts) > 1 and parts[1].isdigit():
        duration = min(int(parts[1]), 30)
    
    if len(parts) > 2:
        device = parts[2]

    await update.message.reply_text(f"🎤 Recording audio ({duration}s)...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{RECORDINGS_DIR}/audio_{timestamp}.wav"
    
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)

    # Build command
    cmd = ["arecord", "-f", "cd", "-d", str(duration)]
    if device:
        cmd.extend(["-D", device])
    cmd.append(filepath)

    try:
        # Lazy import for headless
        import pyautogui

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # Check for specific error to trigger fallback
        err_msg = stderr.decode().strip() if stderr else ""
        if "Host is down" in err_msg and not device:
            logger.warning("Sound server down, trying default hardware fallback...")
            fallback_cmd = ["arecord", "-f", "cd", "-d", str(duration), "-D", "plughw:0,0", filepath]
            process = await asyncio.create_subprocess_exec(
                *fallback_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            err_msg = stderr.decode().strip() if stderr else ""

        if os.path.exists(filepath) and os.path.getsize(filepath) > 44:
            await update.message.reply_audio(
                audio=open(filepath, 'rb'),
                caption=f"🎤 Audio Recording ({duration}s)"
            )
            logger.info(f"Sent audio to {user.first_name}")
        else:
             err = stderr.decode().strip() if stderr else "No data captured."
             logger.error(f"arecord failed: {err}")
             await update.message.reply_text(f"❌ Failed: {err}\n\nHint: Try /hear 10 hw:1,0 or /hear 10 hw:0,0")

    except Exception as e:
        logger.error(f"Hear failed: {e}")
        await update.message.reply_text(f"❌ Hear failed: {e}")

