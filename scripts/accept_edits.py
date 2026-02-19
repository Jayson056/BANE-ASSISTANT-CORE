# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import sys
import os

# Add parent directory to sys.path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from antigravity.button_mapper import detect_action_buttons, click_button
# Note: Notification via sender.py can be added if needed

def main():
    print("🔍 Scanning for action buttons...")
    buttons = detect_action_buttons()
    
    if not buttons:
        print("❌ No action buttons detected on screen.")
        sys.exit(1)
        
    if "accept_all" in buttons:
        print(f"✅ Found 'Accept ALL' at {buttons['accept_all']}. Clicking...")
        success = click_button(buttons["accept_all"])
        if success:
            print("🚀 Successfully clicked 'Accept ALL'.")
            sys.exit(0)
        else:
            print("❌ Failed to click 'Accept ALL'.")
            sys.exit(1)
    else:
        print("⚠️ 'Accept ALL' button not found among detected buttons.")
        print(f"Detected: {list(buttons.keys())}")
        sys.exit(1)

if __name__ == "__main__":
    main()
