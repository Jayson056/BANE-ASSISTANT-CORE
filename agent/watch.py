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

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Record screen video for a duration.
    Usage: /watch [seconds] (default 10s)
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    text = update.message.text
    parts = text.split()
    duration = 10  # default
    if len(parts) > 1 and parts[1].isdigit():
        duration = int(parts[1])
        if duration > 30:  # Limit to 30s for safety/size
            duration = 30

    await update.message.reply_text(f"🎥 Recording screen for {duration} seconds...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{RECORDINGS_DIR}/video_{timestamp}.mp4"
    
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)

    # FFmpeg command for screen recording (X11grab)
    # Adjust resolution if needed, or use full screen
    cmd = [
        "ffmpeg",
        "-y", # Overwrite
        "-f", "x11grab",
        "-i", ":0", # Display :0
        "-t", str(duration),
        "-r", "10", # Lower framerate for file size
        filepath
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()

        if os.path.exists(filepath):
            await update.message.reply_video(
                video=open(filepath, 'rb'),
                caption=f"🎥 Screen Recording ({duration}s)"
            )
            logger.info(f"Sent video to {user.first_name}")
        else:
             await update.message.reply_text("❌ Failed to create video file.")

    except Exception as e:
        logger.error(f"Watch failed: {e}")
        await update.message.reply_text(f"❌ Watch failed: {e}")
