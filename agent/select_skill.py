# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, constants
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.skill_manager import SKILL_CONFIG, get_current_skill

logger = logging.getLogger(__name__)

# State management for password flow in select_skill
_awaiting_skill_password = {} # user_id -> skill_id

async def select_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display skill selection menu based on user permissions."""
    from telegram_interface.auth import is_admin_context
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return
    
    is_admin = is_admin_context(update)
    current_skill = get_current_skill()
    
    keyboard = []
    current_row = []
    
    # Build reply keyboard
    for skill_id, config in SKILL_CONFIG.items():
        if config.get("admin_only") and not is_admin:
            continue
            
        btn_text = f"{config['name']}"
        current_row.append(KeyboardButton(btn_text))
        
        if len(current_row) == 2: # 2 buttons per row
            keyboard.append(current_row)
            current_row = []
            
    if current_row:
        keyboard.append(current_row)
    
    # Add a close button
    keyboard.append([KeyboardButton("❌ Close Menu")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    msg = f"""🧠 **AI SKILL SELECTION**
{"*(Admin Mode Active)*" if is_admin else "*(Public Access Mode)*"}

📍 **Current**: `{SKILL_CONFIG.get(current_skill, {}).get('name', 'Unknown')}`

Select a skill from the menu below to switch persona:"""
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_skill_text_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text based skill switching (from Reply Keyboard or direct typing)."""
    from antigravity.skill_manager import SKILL_CONFIG, set_current_skill
    from telegram_interface.auth import is_admin_context, is_authorized
    
    text = update.message.text
    user = update.effective_user
    
    if text == "❌ Close Menu":
        await update.message.reply_text("Menu closed.", reply_markup=ReplyKeyboardRemove())
        return True

    # Find skill by name
    target_id = None
    for skill_id, config in SKILL_CONFIG.items():
        if config['name'] == text:
            target_id = skill_id
            break
    
    if not target_id:
        return False # Not a skill command
        
    config = SKILL_CONFIG[target_id]
    
    # Admin Check
    if config.get("admin_only") and not is_admin_context(update):
        await update.message.reply_text("🔒 **ACCESS DENIED**\n\nThis skill is restricted to the admin core.")
        return True
        
    if config.get("password_protected"):
        _awaiting_skill_password[user.id] = target_id
        await update.message.reply_text(
            f"🔒 **PASSWORD REQUIRED**\n\nThe skill `{config['name']}` is protected.\n\nPlease type the maintenance password:",
            reply_markup=ReplyKeyboardRemove()
            )
        return True
    
    if set_current_skill(target_id):
        await update.message.reply_text(f"✅ **Skill Switched**\n\nNow using: `{config['name']}`", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("❌ Failed to switch skill.")
    
    return True

async def handle_skill_selection(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle skill selection button click."""
    from antigravity.skill_manager import SKILL_CONFIG, set_current_skill
    from telegram_interface.auth import get_admin_id
    
    user_id = query.from_user.id
    skill_id = query.data.replace("SKILL:", "")
    logger.info(f"handle_skill_selection triggered: user={user_id}, skill={skill_id}")
    
    if skill_id not in SKILL_CONFIG:
        await query.message.reply_text("❌ Unknown skill.")
        return

    config = SKILL_CONFIG[skill_id]
    
    # Permission Check
    from telegram_interface.auth import is_admin_context
    if config.get("admin_only") and not is_admin_context(query):
        await query.answer("❌ Permission Denied: Admin only skill.", show_alert=True)
        return
    
    if config.get("password_protected"):
        logger.info(f"Skill {skill_id} is protected. Prompting for password.")
        _awaiting_skill_password[user_id] = skill_id
        try:
            await query.edit_message_text(
                text=f"🔒 **PASSWORD REQUIRED**\n\nThe skill `{config['name']}` is protected.\n\nPlease type the maintenance password to proceed:",
                parse_mode=constants.ParseMode.MARKDOWN
            )
            logger.info("Password prompt displayed successfully.")
        except Exception as e:
            logger.error(f"Failed to edit message for password prompt: {e}")
            await query.message.reply_text("🔒 **PASSWORD REQUIRED**\n\nPlease type the maintenance password to proceed.")
    else:
        if set_current_skill(skill_id):
            try:
                await query.edit_message_text(
                    text=f"✅ **Skill Switched**\n\nNow using: `{config['name']}`",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to edit message for skill switch: {e}")
                await query.message.reply_text(f"✅ **Skill Switched**\n\nNow using: `{config['name']}`", parse_mode=constants.ParseMode.MARKDOWN)
        else:
            await query.edit_message_text("❌ Failed to switch skill.")

def is_awaiting_skill_password(user_id):
    return user_id in _awaiting_skill_password

async def verify_skill_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from antigravity.skill_manager import SKILL_CONFIG, set_current_skill
    
    user_id = update.effective_user.id
    password = update.message.text
    skill_id = _awaiting_skill_password.get(user_id)
    
    if not skill_id:
        return False

    # Use environment password if available
    correct_pwd = os.getenv("MAINTENANCE_PASSWORD", "core2026")
    
    if password == correct_pwd:
        if set_current_skill(skill_id):
            await update.message.reply_text(
                f"✅ **Authenticated!**\n\nSkill switched to: `{SKILL_CONFIG[skill_id]['name']}`",
                parse_mode=constants.ParseMode.MARKDOWN
            )
            del _awaiting_skill_password[user_id]
            return True
        else:
            await update.message.reply_text("❌ Failed to switch skill after authentication.")
    else:
        await update.message.reply_text("❌ **Incorrect password.** Skill switch aborted.", parse_mode=constants.ParseMode.MARKDOWN)
        del _awaiting_skill_password[user_id]
    
    return True
