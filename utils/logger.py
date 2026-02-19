import os
import datetime

LOG_FILE = "/home/son/BANE/storage/conversation_history.txt"

def get_current_skill_info():
    """Reads the current skill name for the header."""
    try:
        state_file = "/home/son/BANE/antigravity/current_skill.txt"
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                skill_id = f.read().strip()
                # Simple mapping for display
                mapping = {
                    "WORKSPACE": "WORKSPACE",
                    "CORE_MAINTENANCE": "CORE MAINTENANCE",
                    "AI_ARCHITECT": "AI ARCHITECT",
                    "CYBER_SECURITY": "CYBERSECURITY",
                    "PROJECT_LEAD": "PROJECT LEAD",
                    "PROGRAMMING_TASK": "PROGRAMMING",
                    "BUG_HUNTER": "BUG HUNTER",
                    "SANDBOX_EXAMPLE": "SANDBOX MODE"
                }
                return mapping.get(skill_id, skill_id.replace("_", " "))
    except:
        pass
    return "SYSTEM"

def log_conversation_step(text, role, user_id=None):
    """Logs a conversation step to a persistent user-specific text file."""
    try:
        from utils.user_manager import get_user_paths
        from telegram_interface.auth import get_admin_id
        current_uid = user_id if user_id else get_admin_id()
        
        paths = get_user_paths(current_uid)
        log_file = paths["history"]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        skill_name = get_current_skill_info()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the entry
        header_line = "━" * 40
        header = f"{header_line}\nTIME:  {timestamp}\nSKILL: {skill_name}\nROLE:  {role.upper()}\n"
        sub_sep = "─" * 40
        log_entry = f"{header}{sub_sep}\n{text}\n\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Prune to keep only the last 10 entries (Memory Efficiency)
        prune_conversation_history(log_file, limit=10)
            
    except Exception as e:
        print(f"Failed to log to text file: {e}")

def prune_conversation_history(file_path, limit=10):
    """Trims the log file to keep only the most recent N entries."""
    if not os.path.exists(file_path):
        return
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        entries = content.split(separator)
        
        # First entry is usually empty or noise from the split
        clean_entries = [e.strip() for e in entries if e.strip()]
        
        if len(clean_entries) > limit:
            recent_entries = clean_entries[-limit:]
            # Reconstruct with separators
            new_content = ""
            for entry in recent_entries:
                new_content += f"{separator}\n{entry}\n\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
    except Exception as e:
        print(f"Failed to prune history: {e}")
