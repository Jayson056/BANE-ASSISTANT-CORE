# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.quota_detector import detect_warning_icons
from antigravity.model_selector import ALL_MODELS

logger = logging.getLogger(__name__)

async def select_model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display model selection menu with buttons for ALL known models.
    Marks detected/limited models based on real-time scan.
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return
    
    # 🔍 Quick feedback
    status_msg = await update.message.reply_text("🔍 **Scanning models...** Listing all options.")
    
    # 📝 Detect current state
    from antigravity.model_selector import get_available_models, ALL_MODELS, normalize_model_name
    raw_current, available_models = get_available_models()
    current_model = normalize_model_name(raw_current)
    
    # Map detected models for fast lookup
    detected_map = {m["name"]: m for m in available_models}
    
    # ⌨️ Build keyboard
    keyboard = []
    
    # Force open button at the top
    keyboard.append([InlineKeyboardButton("🖱️ Reveal Menu On Screen", callback_data="CLICK_MODEL_DROPDOWN")])
    
    for model_name in ALL_MODELS:
        m_info = detected_map.get(model_name)
        
        status_icon = "🔘"
        if m_info:
            status_icon = "⚠️" if m_info.get("is_limited") else "🟢"
            
        keyboard.append([InlineKeyboardButton(text=f"{status_icon} {model_name}", callback_data=f"MODEL:{model_name}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = f"""🤖 **AI MODEL SELECTION**

📍 **Current**: `{current_model}`

**Status Key:**
🟢 = Detected & Available
⚠️ = **Usage Limit Reached**
🔘 = Not detected (Click to force switch)

Choose a model to switch:
"""
    await status_msg.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
