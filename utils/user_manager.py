import os
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

BASE_STORAGE = "/home/son/BANE/storage/users"
BASE_WORKSPACES = "/home/son/BANE_Workspaces/USER-DATA"

def get_user_hash(user_identifier, platform="telegram"):
    """
    Generates a consistent hash for a user identifier.
    Maintains backward compatibility for Telegram users.
    """
    if platform == "telegram":
        # Keep legacy hashing for Telegram to avoid data loss for existing users
        composite_id = str(user_identifier)
    else:
        composite_id = f"{platform}:{user_identifier}"
    
    return hashlib.sha256(composite_id.encode()).hexdigest()[:16]

def get_user_paths(user_identifier, platform="telegram"):
    """Returns the storage and workspace paths for a specific user identifier."""
    user_hash = get_user_hash(user_identifier, platform)
    return {
        "storage": os.path.join(BASE_STORAGE, user_hash),
        "workspace": os.path.join(BASE_WORKSPACES, user_hash),
        "history": os.path.join(BASE_STORAGE, user_hash, "conversation_history.txt"),
        "received": os.path.join(BASE_STORAGE, user_hash, "received_files"),
        "hash": user_hash,
        "platform": platform
    }

def initialize_user(user_identifier, platform="telegram"):
    """Initializes folders and privacy notice for a new user."""
    paths = get_user_paths(user_identifier, platform)
    
    # Create directories
    os.makedirs(paths["storage"], exist_ok=True)
    os.makedirs(paths["workspace"], exist_ok=True)
    os.makedirs(paths["received"], exist_ok=True)
    
    # Create identity reference for back-mapping (used by background automation)
    identity_path = os.path.join(paths["storage"], "identity.json")
    if not os.path.exists(identity_path):
        with open(identity_path, "w") as f:
            json.dump({
                "uid": str(user_identifier),
                "platform": platform,
                "hash": paths["hash"]
            }, f)
            
    # Check for Data Access Privacy Notice
    privacy_notice_path = os.path.join(paths["storage"], "PRIVACY_NOTICE_ACK.txt")
    if not os.path.exists(privacy_notice_path):
        reminder_promo = ""
        if platform == "messenger" or platform == "telegram":
            reminder_promo = """🚀 **KAYA KO MAG-SET NG REMINDERS:** 
Sabihan mo lang ako, kaya ko i-set kahit anong reminder para sa'yo—kahit anong oras, kahit anong task! Sabihan mo lang ako ng 'Paalala: [Task] sa [Oras]' at ako na ang bahala.

"""
        
        notice_content = f"""👋 **MABUHAY! AKO SI BANE**

Ako ang iyong matalinong digital helper. I am here to help you manage your tasks, write code, and organize your digital life. 

{reminder_promo}🛡️ **DATA ACCESS PRIVACY NOTICE ({platform.upper()})**

This bane instance has initialized a private, isolated environment for your identity:

* 🔐 **Isolated History**: Your conversation logs are stored in a private, hashed directory.
* 📂 **Private Storage**: All uploaded files are contained within your personal `received_files` folder.
* 🏗️ **Isolated Workspace**: Your development workspace is architecturally blocked from other users.
* 🚫 **No Leakage Policy**: Access to cross-tenant data is strictly prohibited and monitored.

*Platform Isolation: {platform}*
"""
        with open(privacy_notice_path, "w") as f:
            f.write(notice_content)
        return True, notice_content
    
    return False, None

def is_user_initialized(user_identifier, platform="telegram"):
    paths = get_user_paths(user_identifier, platform)
    return os.path.exists(os.path.join(paths["storage"], "PRIVACY_NOTICE_ACK.txt"))
