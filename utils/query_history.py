#!/usr/bin/env python3
import sys
import re
import os

def query_history(user_id=None, target_skill=None):
    from utils.user_manager import get_user_paths
    
    if user_id:
        paths = get_user_paths(user_id)
        log_file = paths["history"]
    else:
        # Fallback to admin/old path
        log_file = "/home/son/BANE/storage/conversation_history.txt"
    
    if not os.path.exists(log_file):
        print(f"No conversation history log found for user {user_id or 'global'}.")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Split by the separator bar
        entries = content.split("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        found_count = 0
        for entry in entries:
            if not entry.strip(): continue
            
            # Reconstruct the separator line since split removed it
            full_entry = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + entry
            
            if target_skill:
                match = re.search(r"SKILL:\s*(.*?)\n", entry)
                if match:
                    skill = match.group(1).strip()
                    if target_skill.upper() in skill.upper():
                        print(full_entry.strip())
                        print("\n")
                        found_count += 1
            else:
                print(full_entry.strip())
                print("\n")
                found_count += 1
                
        if found_count == 0 and target_skill:
            print(f"No conversation history found for skill: {target_skill}")
            
    except Exception as e:
        print(f"Error reading history: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query Conversation History")
    parser.add_argument("skill", nargs="?", help="Optional skill name filter")
    parser.add_argument("--user_id", help="Filter by User ID")
    args = parser.parse_args()
    
    query_history(user_id=args.user_id, target_skill=args.skill)
