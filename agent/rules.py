# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands with tiered access."""
    user = update.effective_user
    if not user: return
    
    from telegram_interface.auth import is_authorized, get_admin_id
    auth_ok, _ = is_authorized(user.id)
    if not auth_ok: return

    is_admin = (user.id == get_admin_id())

    # --- Core Command Sets ---
    guest_commands = """
🛰️ bane command center

[ standard commands ]
• /start - verify connectivity
• /help - show this guide
• /rules - available commands

[ ai interface ]
• /select_skill - switch persona
• /quota - check usage limits
• /select_model - model selection

[ file tools ]
• /ls [path] - list directory
• /search [word] - find information
• /save - save snapshot

guest access mode active.
"""

    admin_commands = """
💎 bane core command center

[ system entry ]
• /start - re-initialize core
• /rules - full command menu

[ core monitoring ]
• /screen - high-res capture
• /watch - live monitor
• /hear - system audio scan
• /report - telemetry report

[ system maintenance ]
• /restart - restart ai core
• /sysrest - system reboot
• /syslogout - session logout
• /accept / /reject - file auth

[ ai & security ]
• /select_skill - persona shift
• /select_model - model shift
• /pass [pwd] - keyring injection
• /quota - capacity check

[ development tools ]
• /ls [path] - file listing
• /search [key] - user search
• /save - snapshot save
• /sandbox - sandbox toggle

admin root access active.
"""

    response_text = admin_commands if is_admin else guest_commands

    try:
        await update.message.reply_markdown(response_text)
    except Exception as e:
        logger.error(f"Failed to send rules: {e}")
        await update.message.reply_text(response_text.replace("*", "").replace("•", "-"))