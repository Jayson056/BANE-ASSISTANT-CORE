# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import subprocess
import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

# Simple pending restart tracker (user_id -> timestamp)
_pending_restart = {}

async def sysrest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Request system restart.
    
    Usage: /sysrest        -> prompt for confirmation
           /sysrest yes    -> confirm immediately
           /sysrest cancel -> cancel pending restart
    """
    user = update.effective_user
    if not user or not is_authorized(user.id)[0]:
        return

    # Check for args
    args = context.args if context.args else []
    arg = args[0].lower() if args else ""

    if arg in ("yes", "confirm", "now"):
        # Direct confirmation
        await _do_restart(update)
        return
    elif arg in ("no", "cancel"):
        _pending_restart.pop(user.id, None)
        await update.message.reply_text("❌ System restart cancelled.")
        return

    # Check if there's already a pending restart (double-tap protection)
    pending = _pending_restart.get(user.id)
    if pending and (time.time() - pending) < 60:
        # User already got prompted, treat as confirmation
        await _do_restart(update)
        return

    # Set pending and ask for confirmation via text
    _pending_restart[user.id] = time.time()
    await update.message.reply_text(
        "⚠️ **SYSTEM RESTART CONFIRMATION**\n\n"
        "You are about to **REBOOT** the entire system.\n\n"
        "To confirm, reply with:\n"
        "✅ `/sysrest yes` — Reboot now\n"
        "❌ `/sysrest cancel` — Cancel\n\n"
        "Or just tap `/sysrest` again within 60s to confirm.",
        parse_mode="Markdown"
    )

async def _do_restart(update: Update):
    """Execute the actual restart."""
    # Clean up pending
    user = update.effective_user
    _pending_restart.pop(user.id, None)

    # Determine the message object (works for both regular and callback)
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text("🔄 Attempting to reboot system...")
    
    # Try without password first (NOPASSWD sudo or polkit)
    try:
        result = subprocess.run(
            ["sudo", "-n", "reboot"], 
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return  # System will reboot
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        logger.error(f"Sudo reboot attempt failed: {e}")

    # Try systemctl (works on many systems without sudo)
    try:
        result = subprocess.run(
            ["systemctl", "reboot"], 
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            await message.reply_text("🔄 Rebooting via systemctl...")
            return
    except Exception:
        pass

    # Try dbus reboot (works for logged-in users on desktop Linux)
    try:
        result = subprocess.run(
            ["dbus-send", "--system", "--print-reply", "--dest=org.freedesktop.login1",
             "/org/freedesktop/login1", "org.freedesktop.login1.Manager.Reboot", "boolean:true"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            await message.reply_text("🔄 Rebooting via DBus...")
            return
    except Exception:
        pass

    # All methods failed — ask for sudo password
    from security.sudo_flow import set_awaiting_sudo
    set_awaiting_sudo("SYSTEM_RESTART")
    await message.reply_text(
        "🔐 **Sudo password required**\n\n"
        "All automatic reboot methods failed.\n"
        "Please send your sudo password to execute the reboot.",
        parse_mode="Markdown"
    )

def is_awaiting_restart_confirmation(user_id: int) -> bool:
    """Check if user has a pending restart confirmation within timeout."""
    pending = _pending_restart.get(user_id)
    if pending and (time.time() - pending) < 60:
        return True
    return False

async def handle_restart_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle text reply for confirmation. Returns True if handled."""
    user = update.effective_user
    text = update.message.text.lower().strip()
    
    if text in ["yes", "confirm", "y", "ok", "now"]:
        await _do_restart(update)
        return True
    elif text in ["no", "cancel", "n", "stop"]:
        _pending_restart.pop(user.id, None)
        await update.message.reply_text("❌ System restart cancelled.")
        return True
    
    return False

async def execute_system_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Legacy entry point for button-based confirmation. Delegates to _do_restart."""
    await _do_restart(update)
