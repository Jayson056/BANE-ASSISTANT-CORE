# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
from telegram import Bot

logger = logging.getLogger(__name__)

async def send_startup_notification():
    """Send startup notification to user via Telegram."""
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="config/secrets.env")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = os.getenv("TELEGRAM_USER_ID")
    
    if not token or not user_id:
        logger.warning("Cannot send startup notification: missing token or user ID")
        return
    
    try:
        bot = Bot(token)
        
        # Try to get user's first name for a personalized greeting
        user_name = "User"
        try:
            chat = await bot.get_chat(user_id)
            user_name = chat.first_name or "User"
        except Exception:
            pass

        # Get local IP dynamically
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "192.168.11.10" # Fallback

        message = f"""
🦅 **BANE ONLINE**

Hello, {user_name}! BANE is powered on and ready.

**System Status:**
✅ Bot service started
✅ BANE Engine launched
✅ Dashboard active

🌐 **Local Dashboard:**
http://{local_ip}:8081

*Ready for commands.*
"""
        await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
        logger.info(f"Startup notification sent to {user_name}")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
