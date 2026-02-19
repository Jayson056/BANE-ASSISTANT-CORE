# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

async def pass_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /pass command to inject password automatically.
    Usage: /pass <password>
    Example: /pass 2001
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return
    
    # 🛡️ SECURITY: Immediately delete the password message from chat history
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete password message: {e}")

    
    # Get password from command arguments
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /pass <password>\n\nExample: /pass 2001")
        return
    
    # Join all arguments as password (in case password has spaces)
    password = " ".join(context.args)
    
    try:
        # Import pyautogui lazily to avoid issues in headless mode
        import pyautogui
        import time
        
        # Get screen size to click center for focus
        width, height = pyautogui.size()
        center_x, center_y = width // 2, height // 2
        
        # Click center to ensure focus
        logger.info(f"Clicking center at ({center_x}, {center_y}) for focus...")
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # Type password and press Enter
        logger.info("Typing password and pressing Enter...")
        pyautogui.write(password, interval=0.01)
        pyautogui.press("enter")
        
        logger.info("Password injected successfully")
        await update.message.reply_text("🔑 Password entered and submitted automatically!")
        
    except Exception as e:
        logger.error(f"Password injection failed: {e}")
        await update.message.reply_text(f"❌ Failed to inject password: {str(e)}")
