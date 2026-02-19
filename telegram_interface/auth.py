# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="config/secrets.env")

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed user IDs - Primary Admin
ADMIN_USER_ID = int(os.getenv("TELEGRAM_USER_ID", 0))

def is_authorized(user_id: int):
    """Check if the user is authorized and initialize their environment if needed."""
    from utils.user_manager import initialize_user, is_user_initialized
    
    # Initialize user environment (folders, privacy notice)
    is_new, notice = initialize_user(user_id)
    
    # In this architectural update, we permit the join but enforce isolation
    if user_id == ADMIN_USER_ID:
        return True, notice if is_new else None
    
    # For new users, we'll log it as a Guest Access
    logger.info(f"Authorized Guest Access for user ID: {user_id} (Hashed Environment Created)")
    return True, notice if is_new else None

def get_admin_id():
    return ADMIN_USER_ID

def is_admin_context(obj):
    """Checks if the user is the admin AND in an admin-enabled context (not 'All chats').
    Handles both Update and CallbackQuery objects.
    """
    if not obj:
        return False
        
    # Handle Update object or CallbackQuery object
    user = getattr(obj, "effective_user", None) or getattr(obj, "from_user", None)
    chat = getattr(obj, "effective_chat", None) or (getattr(obj, "message", None).chat if hasattr(obj, "message") and obj.message else None)

    if not user or user.id != ADMIN_USER_ID:
        return False
        
    # Special restricted group check: treat admin as normal user in 'All chats'
    if chat and chat.title == "All chats":
        return False
        
    return True
