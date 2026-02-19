# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
from telegram import Update
from telegram.ext import ContextTypes
import subprocess
import os

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search history and workspace for keywords with references."""
    if not context.args:
        await update.message.reply_text("🔍 **SEARCH COMMAND**\n\nUsage: `/search [keyword]`\nExample: `/search Jupiter`")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 **Searching for: '{query}'...**")

    try:
        # Use our search_engine utility
        engine_script = "/home/son/BANE/utils/search_engine.py"
        python_bin = "/home/son/BANE/.venv/bin/python3"
        
        user_id = update.effective_user.id
        result = subprocess.run([python_bin, engine_script, query, "--user_id", str(user_id)], capture_output=True, text=True, timeout=30)
        
        output = result.stdout.strip()
        
        if not output or "No results found" in output:
            await update.message.reply_text(f"❌ No matching references found for '{query}'.")
            return

        # Format for Telegram (respecting 4096 char limit)
        if len(output) > 4000:
            output = output[:4000] + "... (truncated)"
        
        # Wrap in premium design
        formatted = f"📊 **SEARCH RESULTS & REFERENCES**\n`{'─' * 25}`\n\n{output}"
        
        # Send via message (dual-mode logic will be handled if user asks AI to search)
        # But for direct /search command, we just reply textually here.
        await update.message.reply_text(formatted, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Search failed: {str(e)}")
