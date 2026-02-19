# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from security.confirm import request_confirmation
from security.sudo_flow import set_awaiting_sudo, execute_with_sudo

logger = logging.getLogger(__name__)

async def syslogout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Request system logout."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    text, markup = request_confirmation(user.id, "SYSTEM_LOGOUT")
    await update.message.reply_markdown(text, reply_markup=markup)

async def execute_system_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes the logout."""
    # Handle both callback query (from buttons) and regular message
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    
    await message.reply_text("👋 Logging out...")
    
    # Logout doesn't typically need sudo, so just execute directly
    try:
        subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"], check=False)
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        await message.reply_text(f"❌ Logout failed: {e}")
