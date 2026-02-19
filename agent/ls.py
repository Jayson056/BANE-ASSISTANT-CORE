# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

async def list_dir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    List files in a directory.
    Usage: /ls [path]
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    text = update.message.text
    parts = text.split(maxsplit=1)
    path = parts[1] if len(parts) > 1 else "."
    
    # Resolve relative paths relative to CWD if needed, or just use as is
    # For security, one might restrict this, but documentation implies full access.
    
    if not os.path.exists(path):
        await update.message.reply_text(f"❌ Path not found: {path}")
        return

    try:
        if os.path.isfile(path):
             await update.message.reply_text(f"📄 Path is a file: {path} ({os.path.getsize(path)} bytes)")
             return
             
        files = os.listdir(path)
        files.sort()
        
        # Limit output
        count = len(files)
        display_files = files[:50]
        
        output = "\n".join(display_files)
        if count > 50:
            output += f"\n\n... and {count - 50} more."
            
        reply = f"📂 **Listing: {path}**\n\n{output}"
        # Telegram max message length is 4096. Truncate if needed.
        if len(reply) > 4000:
            reply = reply[:4000] + "\n...(truncated)"
            
        await update.message.reply_text(reply)
        
    except Exception as e:
        logger.error(f"ls failed: {e}")
        await update.message.reply_text(f"❌ Error listing directory: {e}")
