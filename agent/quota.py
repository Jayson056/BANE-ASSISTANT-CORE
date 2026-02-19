# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized
from antigravity.quota_detector import extract_quota_details

logger = logging.getLogger(__name__)


def detect_quota():
    """Returns detected quota information."""
    info = {
        "model": os.getenv("ANTIGRAVITY_MODEL", "Unknown"),
        "provider": "Antigravity",
        "rate_limit": "Not exposed",
        "tokens": "Not exposed",
    }

    quota_file = "config/quota.yaml"
    if os.path.exists(quota_file):
        try:
            with open(quota_file, "r") as f:
                info["notes"] = f.read().strip()
        except Exception:
            pass

    return info


async def show_quota(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the AI quota status with visual warning detection."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    # Initial message
    await update.message.reply_text(
        "🔍 Scanning for quota warnings...",
        parse_mode=None
    )

    quota_data = extract_quota_details()
    q = detect_quota()

    msg = (
        "📊 AI QUOTA STATUS\n\n"
        f"🏢 Provider: {q['provider']}\n"
        f"🤖 Model: {q['model']}\n"
    )

    if quota_data.get("models"):
        msg += "\n⚠️ LIMITS DETECTED:\n"
        for model in quota_data["models"]:
            msg += f"   • {model['name']} → {model['limit']}\n"
    else:
        msg += "\n✅ No quota warnings detected\n"

    if "notes" in q:
        msg += f"\n📝 Notes:\n{q['notes']}\n"

    msg += "\n➡️ Use /select_model to switch models"

    await update.message.reply_text(
        msg,
        parse_mode=None
    )

