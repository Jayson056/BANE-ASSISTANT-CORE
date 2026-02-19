# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update
from telegram.ext import ContextTypes

# Import command handlers
from agent.rules import rules_command
from agent.screen import screen_command
from agent.report import report_command
from agent.restart import restart_antigravity
from agent.ls import list_dir
from agent.watch import watch_command
from agent.hear import hear_command
from agent.sysrest import sysrest_command, execute_system_restart
from agent.syslogout import syslogout_command
from agent.quota import show_quota
from agent.save import save_snapshot
from agent.passkey import pass_command
from agent.select_model import select_model_command
from agent.select_skill import select_skill_command
from agent.actions import accept_command, reject_command
from agent.sandbox import sandbox_command
from agent.search import search_command
from agent.turbo import turbo_command
from telegram_interface.auth import is_authorized # Needed for start check

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send beautifully designed welcome message based on user tier."""
    user = update.effective_user
    if not user: return
    
    from telegram_interface.auth import is_authorized, get_admin_id
    auth_ok, notice = is_authorized(user.id)
    if not auth_ok: return

    is_admin = is_admin_context(update)

    # 1. Send Isolation Notice if initialized (Privacy Notice)
    if notice:
        await update.message.reply_text(notice)

    # 2. Construct Premium Welcome
    admin_welcome = f"""
🚀 WELCOME TO THE BANE CORE

Greeting acknowledged, root admin. The systems current integrity is stable, and all telemetry modules are online.

[ root session initialized ]
• identity: {user.first_name} (Admin)
• uplink: encrypted dual-channel
• status: full system visibility

Type /rules to access the full array of monitoring and maintenance tools.
"""

    guest_welcome = f"""
🛰️ WELCOME TO THE BANE INTERFACE

Hello, {user.first_name}. Your private, isolated session with the bane ai core has been successfully established.

[ session details ]
• privacy: 100% isolated workspace
• mode: visitor permissions active
• uplink: secure telegram bridge

Type /rules to see your available command set.
"""

    welcome_text = admin_welcome if is_admin else guest_welcome

    try:
        await update.message.reply_markdown(welcome_text)
    except:
        await update.message.reply_text(welcome_text.replace("*", "").replace("•", "-"))

# Command Descriptions for Telegram Menu
COMMAND_DESCRIPTIONS = {
    "start": "Verify BANE connectivity",
    "rules": "Show all available commands",
    "help": "Show all available commands",
    "screen": "Capture and send current desktop screenshot",
    "report": "Get system status report (CPU, RAM, Disk)",
    "restart": "Restart the BANE Engine interface",
    "ls": "List directory contents (usage: /ls [path])",
    "watch": "Monitor screen for changes",
    "hear": "Listen to the last 10s of system audio",
    "sysrest": "Restart the entire system (OS)",
    "syslogout": "Log out the current desktop session",
    "quota": "Check AI model usage limits",
    "save": "Save a conversation snapshot",
    "pass": "Send password for keyring (usage: /pass [pwd])",
    "select_model": "Open interactive model selection menu",
    "select_skill": "Switch AI persona/skills mode",
    "accept": "Click 'Accept ALL' in BANE Core UI",
    "reject": "Click 'Reject ALL' in BANE Core UI",
    "sandbox": "Switch to AI Sandbox Mode",
    "search": "Search history and files for keywords with references",
    "turbo": "Enable/Disable autonomous 'Always Run' mode",
}

# Command Registry
COMMANDS = {
    "/start": start_command, # Ensure explicit start handling
    "/rules": rules_command,
    "/help": rules_command,
    "/screen": screen_command,
    "/report": report_command,
    "/restart": restart_antigravity,
    "/ls": list_dir,
    "/watch": watch_command,
    "/hear": hear_command,
    "/sysrest": sysrest_command,
    "/sysret": sysrest_command,
    "/syslogout": syslogout_command,
    "/logout": syslogout_command,
    "/quota": show_quota,
    "/save": save_snapshot,
    "/pass": pass_command,
    "/select_model": select_model_command,
    "/select_skill": select_skill_command,
    "/accept": accept_command,
    "/reject": reject_command,
    "/sandbox": sandbox_command,
    "/search": search_command,
    "/turbo": turbo_command,
    "/now": execute_system_restart, # Emergency bypass
}

async def route_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Route a command to its appropriate handler.
    Expected update.message.text to start with /.
    """
    text = update.message.text
    if not text:
        return

    # Extract command (first word) and handle @botname
    full_cmd = text.split()[0].lower()
    cmd = full_cmd.split('@')[0]

    # Security: Restrict high-risk telemetry and system commands to Core (Admin)
    RESTRICTED_COMMANDS = [
        "/screen", "/report", "/watch", "/hear", 
        "/sysrest", "/sysret", "/syslogout", "/logout", 
        "/restart", "/sandbox", "/turbo", "/now"
    ]
    if cmd in RESTRICTED_COMMANDS:
        from telegram_interface.auth import is_admin_context
        if not is_admin_context(update):
            logger.warning(f"Unauthorized access attempt: {cmd} by user {update.effective_user.id}")
            await update.message.reply_text("🔒 **ACCESS RESTRICTED**\n\nThis command is restricted to the **bane** core admin. Guest users are permitted to use standard commands but cannot access system-level tools or monitoring.")
            return
    
    # Check if command exists in registry
    handler = COMMANDS.get(cmd)
    
    if handler:
        logger.info(f"Routing command: {cmd}")
        try:
            await handler(update, context)
        except Exception as e:
            logger.error(f"Error in handler for {cmd}: {e}")
            await update.message.reply_text(f"❌ Error executing command: {e}")
    else:
        # Avoid replying to unknown commands in groups if they aren't for us
        if '@' in full_cmd and not full_cmd.endswith(context.bot.username.lower()):
            return
            
        await update.message.reply_text("❌ Unknown command. Use /rules to see available commands.")

