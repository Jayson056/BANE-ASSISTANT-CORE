# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """
    Creates a YES/NO inline keyboard for confirmation.
    Callback data: YES:{action} or NO:{action}
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ YES", callback_data=f"YES:{action}"),
            InlineKeyboardButton("❌ NO", callback_data=f"NO:{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def accept_reject_keyboard() -> InlineKeyboardMarkup:
    """
    Creates Accept ALL / Reject ALL buttons for file changes.
    Callback data: ACCEPT_ALL or REJECT_ALL
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Accept ALL", callback_data="ACCEPT_ALL"),
            InlineKeyboardButton("❌ Reject ALL", callback_data="REJECT_ALL")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def allow_access_keyboard() -> InlineKeyboardMarkup:
    """
    Creates Allow Once / Allow This Conversation buttons for directory access prompts.
    """
    keyboard = [
        [
            InlineKeyboardButton("✨ Allow Once", callback_data="ALLOW_ONCE"),
            InlineKeyboardButton("🔄 Allow Conversation", callback_data="ALLOW_CONV")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
