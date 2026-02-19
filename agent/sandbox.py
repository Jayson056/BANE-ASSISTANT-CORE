# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.skill_manager import set_current_skill

async def sandbox_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to Sandbox Mode directly."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    # Force switch to Sandbox
    if set_current_skill("SANDBOX_EXAMPLE"):
        await update.message.reply_text("✅ **Sandbox Mode ENGAGED**\n\nActive Skill: `Sandbox Mode`\n\nAll commands are now isolated.")
    else:
        await update.message.reply_text("❌ Failed to engage Sandbox Mode.")
