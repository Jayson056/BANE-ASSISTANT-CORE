# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.button_mapper import detect_action_buttons, click_button

logger = logging.getLogger(__name__)

async def accept_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explicit command to click Accept ALL."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return
    
    status_msg = await update.message.reply_text("🔍 **Searching for Accept ALL button...**")
    
    buttons = detect_action_buttons()
    if buttons and "accept_all" in buttons:
        success = click_button(buttons["accept_all"])
        if success:
            await status_msg.edit_text("✅ **Success!** Clicked 'Accept ALL' in Antigravity UI.")
        else:
            await status_msg.edit_text("❌ **Failed** to click the button. Please check the screen.")
    else:
        await status_msg.edit_text("⚠️ **'Accept ALL' button not found.** Make sure the changes are visible in Antigravity.")

async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explicit command to click Reject ALL."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return
    
    status_msg = await update.message.reply_text("🔍 **Searching for Reject ALL button...**")
    
    buttons = detect_action_buttons()
    if buttons and "reject_all" in buttons:
        success = click_button(buttons["reject_all"])
        if success:
            await status_msg.edit_text("✅ **Done!** Clicked 'Reject ALL' in Antigravity UI.")
        else:
            await status_msg.edit_text("❌ **Failed** to click the button.")
    else:
        await status_msg.edit_text("⚠️ **'Reject ALL' button not found.** Is Antigravity showing any changes?")
