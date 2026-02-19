# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
from telegram import InlineKeyboardMarkup
from telegram_interface.ui import confirm_keyboard
import logging

logger = logging.getLogger(__name__)

# Dictionary to store pending confirmations: user_id -> action_string
_pending = {}

def request_confirmation(user_id: int, action: str) -> tuple[str, InlineKeyboardMarkup]:
    """
    Registers a pending confirmation.
    Returns: (prompt_text, reply_markup)
    """
    _pending[user_id] = action
    logger.info(f"Confirmation requested: User {user_id} -> {action}")
    
    text = f"⚠️ **CONFIRMATION REQUIRED**\n\nAction: `{action}`\n\nTap below to confirm."
    markup = confirm_keyboard(action)
    return text, markup

def resolve_confirmation(user_id: int, decision: str) -> str | None:
    """
    Resolves a pending confirmation based on decision (YES/NO).
    Returns the action string if confirmed (YES), None otherwise.
    Clears the pending action.
    """
    # Check if the user really has this action pending
    action = _pending.pop(user_id, None)
    
    if not action:
        return None

    if decision == "YES":
        logger.info(f"Action confirmed via button: {action}")
        return action
    else:
        logger.info(f"Action cancelled via button: {action}")
        return None

# Keep validate_confirmation for text fallback if needed, or remove?
# The doc says "We replace text typing with buttons". 
# But let's keep it compatible or just rely on buttons.
# For simplicity and clean switch, let's remove text fallback validation unless requested.
# The user approved "replace text typing". So we focus on buttons.

