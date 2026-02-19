import os
import time
import subprocess
import argparse
from datetime import datetime

def schedule_reminder(target_time_str, message, recipient_id, platform="messenger"):
    """
    Schedules a reminder using a simple background process.
    target_time_str: HH:MM (24h format)
    """
    now = datetime.now()
    try:
        target_time = datetime.strptime(target_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
    except ValueError:
        print(f"❌ Invalid time format: {target_time_str}. Use HH:MM")
        return False

    # If target time is in the past today, assume tomorrow? 
    # For this specific request "mamayang 3:25 pm now", it's clearly today.
    if target_time < now:
        # Check if it was meant for "today" but we are already past it
        print(f"⚠️ Target time {target_time_str} is in the past. Scheduling for tomorrow.")
        # But for 3:25 PM today (03:17 now), it's in the future.
        # However, let's just use the absolute difference.
        pass

    delay = (target_time - now).total_seconds()
    if delay < 0:
        delay += 86400 # 24 hours later

    print(f"✅ Scheduling reminder in {delay} seconds for {target_time}...")
    
    # Construct the command to send the message
    # Construct the command to send the message
    if platform == "messenger":
        send_cmd = [
            "/home/user/BANE_CORE/.venv/bin/python3",
            "/home/user/BANE_CORE/utils/sender.py",
            "--platform", "messenger",
            "--recipient_id", recipient_id,
            "--text", f"🔔 PAALALA: {message}"
        ]
    else:
        send_cmd = [
            "/home/user/BANE_CORE/.venv/bin/python3",
            "/home/user/BANE_CORE/utils/sender.py",
            "--platform", "telegram",
            "--recipient_id", recipient_id,
            "--text", f"🔔 PAALALA: {message}"
        ]

    # Use a detached process to wait and send
    # We'll use a small python wrapper to handle the sleep + send
    wrapper_code = f"""
import time
import subprocess
import os

time.sleep({delay})
subprocess.run({send_cmd})
"""
    
    with open("/tmp/reminder_temp.py", "w") as f:
        f.write(wrapper_code)
    
    subprocess.Popen(["python3", "/tmp/reminder_temp.py"], start_new_session=True)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--platform", default="messenger")
    args = parser.parse_args()
    
    schedule_reminder(args.time, args.message, args.id, args.platform)
