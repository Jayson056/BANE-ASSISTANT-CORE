
import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from antigravity.button_mapper import detect_action_buttons, click_button

logger = logging.getLogger(__name__)
STATE_FILE = "storage/automation_state.json"

def get_automation_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"autonomous": False}  # Default OFF

def set_automation_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"autonomous": state}, f)
        return True
    except:
        return False

async def turbo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage autonomous execution and 'Always run' state."""
    state = get_automation_state()["autonomous"]
    
    # Check for arguments
    if context.args:
        arg = context.args[0].lower()
        if arg in ["on", "enable", "start"]:
            set_automation_state(True)
            await update.message.reply_text("🚀 **TURBO MODE ENABLED**\n\nI will now automatically click 'Accept ALL' and 'Always Run' prompts in the core UI without waiting for Telegram confirmation.")
            return
        elif arg in ["off", "disable", "stop"]:
            set_automation_state(False)
            await update.message.reply_text("🛑 **TURBO MODE DISABLED**\n\nI will wait for manual confirmation for all system changes.")
            return

    # Toggle if no arg, or just show status
    keyboard = [
        [
            InlineKeyboardButton("🚀 Enable Turbo", callback_data="TURBO:ON"),
            InlineKeyboardButton("🛑 Disable Turbo", callback_data="TURBO:OFF")
        ],
        [InlineKeyboardButton("🔍 Sync Always Run UI", callback_data="TURBO:SYNC")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "ENABLED 🚀" if state else "DISABLED 🛑"
    await update.message.reply_text(
        f"🤖 **AUTOMATION SETTINGS**\n\nStatus: **{status}**\n\nTurbo Mode allows BANE to autonomously accept its own code changes and security prompts in real-time.",
        reply_markup=reply_markup
    )

async def handle_turbo_callback(query):
    data = query.data.replace("TURBO:", "")
    
    if data == "ON":
        set_automation_state(True)
        await query.edit_message_text("🚀 **TURBO MODE ENABLED**")
    elif data == "OFF":
        set_automation_state(False)
        await query.edit_message_text("🛑 **TURBO MODE DISABLED**")
    elif data == "SYNC":
        await query.edit_message_text("🔍 Syncing with 'Always Run' UI...")
        buttons = detect_action_buttons()
        if buttons and "always_run" in buttons:
            success = click_button(buttons["always_run"])
            if success:
                await query.message.reply_text("✅ Successfully toggled 'Always Run' in Core UI.")
            else:
                await query.message.reply_text("❌ Failed to click 'Always Run' button.")
        else:
            await query.message.reply_text("⚠️ 'Always Run' button not found in UI.")
