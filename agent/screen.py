# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from screen.capture import capture_screen

logger = logging.getLogger(__name__)

async def screen_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Take a screenshot and send it to the user."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    await update.message.reply_text("📸 Capturing screen...")
    
    path = capture_screen()
    
    if path:
        try:
            await update.message.reply_photo(photo=open(path, 'rb'), caption=f"Screenshot saved at {path}")
            logger.info(f"Sent screenshot to {user.first_name}")
        except Exception as e:
            logger.error(f"Failed to send screenshot: {e}")
            await update.message.reply_text("❌ Failed to send screenshot.")
    else:
        await update.message.reply_text("❌ Failed to capture screen.")
