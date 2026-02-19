
import os
import json
import datetime
import subprocess

# Settings
BASE_WORKSPACE = "/home/user/BANE_CORE_Workspaces/USER-DATA"
BASE_STORAGE = "/home/user/BANE_CORE/storage/users"
SEND_MESSENGER_PATH = "/home/user/BANE_CORE/utils/sender.py"
SEND_TELEGRAM_PATH = "/home/user/BANE_CORE/utils/sender.py"
PYTHON_PATH = "/home/user/BANE_CORE/.venv/bin/python3"

# Day Mapping
DAY_MAP = {
    "M": 0, "T": 1, "W": 2, "TH": 3, "F": 4, "S": 5, "SU": 6
}

# Periodic Trigger Hours (24h format)
# 8:00 AM, 12:00 PM, 6:00 PM (18), 10:00 PM (22), 12:00 AM (0)
TRIGGER_HOURS = [0, 8, 12, 18, 22]
SYNC_SCRIPT = "/home/user/BANE_CORE/antigravity/scripts/sync_task_tracker.py"

def check_all_users():
    """Iterates through all hashed user directories to check for schedules and assignments."""
    if not os.path.exists(BASE_WORKSPACE):
        return

    for user_hash in os.listdir(BASE_WORKSPACE):
        user_ws_path = os.path.join(BASE_WORKSPACE, user_hash)
        if not os.path.isdir(user_ws_path):
            continue
            
        schedule_file = os.path.join(user_ws_path, "School/School Calendar/Class_Schedule.json")
        tracker_file = os.path.join(user_ws_path, "School/Live_Task_Tracker.json")
        identity_file = os.path.join(BASE_STORAGE, user_hash, "identity.json")
        
        if os.path.exists(identity_file):
            with open(identity_file, 'r') as f:
                user_info = json.load(f)
            
            # 1. Check Class Schedule (Reminds exactly 10H prior to a specific class)
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r') as f:
                    schedule = json.load(f)
                check_user_specific_class_alert(user_info, schedule)
            
            # 2. Periodic Comprehensive Reminder (Assignments + Tomorrow's Schedule)
            check_periodic_reminders(user_info, tracker_file, schedule_file)

def check_user_specific_class_alert(user_info, schedule):
    """Legacy 10-hour alert for specific classes."""
    now = datetime.datetime.now()
    target_time = now + datetime.timedelta(hours=10)
    target_day_index = target_time.weekday()
    target_clock = target_time.strftime("%H:%M")
    
    for subject in schedule:
        for entry in subject['times']:
            parts = entry.split()
            if not parts: continue
            day_code = parts[0]
            time_range = parts[1]
            start_time = time_range.split('-')[0][:5]
            
            if DAY_MAP.get(day_code) == target_day_index and start_time == target_clock:
                send_class_alert(user_info, subject, start_time, day_code)

def check_periodic_reminders(user_info, tracker_file, schedule_file):
    """
    Sends comprehensive reminders at specific hours (8am, 12pm, 6pm, 10pm, 12am).
    Includes assignments and tomorrow's schedule.
    """
    now = datetime.datetime.now()
    if now.hour not in TRIGGER_HOURS or now.minute != 0:
        return

    # A. PERFORM LIVE SYNC RIGHT BEFORE REMINDER
    log_msg = f"Starting Live Sync for reminder at {now.hour}:00"
    print(log_msg)
    try:
        subprocess.run([PYTHON_PATH, SYNC_SCRIPT], check=True)
        print("✅ Live Sync Successful")
    except Exception as e:
        print(f"❌ Live Sync Failed: {e}")

    # B. Get Upcoming Assignments/Tasks
    pending_tasks = []
    if os.path.exists(tracker_file):
        with open(tracker_file, 'r') as f:
            tracker_data = json.load(f)
        milestones = tracker_data.get("major_milestones", [])
        for m in milestones:
            date_str = m.get("date")
            if not date_str: continue
            try:
                task_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                days_remaining = (task_date - now.replace(hour=0, minute=0, second=0, microsecond=0)).days
                if 0 <= days_remaining <= 7:
                    pending_tasks.append(m)
            except: continue

    # B. Get Upcoming Schedule (Look-ahead 3 Days)
    upcoming_schedule = []
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r') as f:
            schedule = json.load(f)
        
        for i in range(1, 4):
            target_date = now + datetime.timedelta(days=i)
            target_day_index = target_date.weekday()
            day_label = "BUKAS" if i == 1 else target_date.strftime("%A, %b %d")
            
            day_classes = []
            for subject in schedule:
                sub_times = []
                for entry in subject['times']:
                    parts = entry.split()
                    if not parts: continue
                    day_code = parts[0]
                    if DAY_MAP.get(day_code) == target_day_index:
                        sub_times.append(parts[1])
                if sub_times:
                    day_classes.append({"code": subject['code'], "desc": subject['description'], "times": sub_times})
            
            upcoming_schedule.append({"label": day_label, "classes": day_classes})

    # C. Always Send Periodic Summary at Trigger Hours
    send_comprehensive_summary(user_info, pending_tasks, upcoming_schedule)

def send_class_alert(user_info, subject, start_time, day_code):
    full_day_name = {
        "M": "Monday", "T": "Tuesday", "W": "Wednesday", 
        "TH": "Thursday", "F": "Friday", "S": "Saturday", "SU": "Sunday"
    }.get(day_code, day_code)

    message = f"⏰ **CLASS REMINDER (10H PRIOR)**\n\n"
    message += f"Hi! Just a heads up—you have a class scheduled for tomorrow:\n\n"
    message += f"📖 **{subject['code']}**\n"
    message += f"📝 {subject['description']}\n"
    message += f"📅 {full_day_name}\n"
    message += f"🕒 Starts at: **{start_time}**\n\n"
    message += f"Handa ka na ba? 🚀"
    
    _deliver(user_info, message)

def send_comprehensive_summary(user_info, tasks, schedule_days):
    now = datetime.datetime.now()
    time_label = now.strftime("%I:%M %p")
    
    message = f"🔔 **BANE PERIODIC REMINDER ({time_label})**\n\n"
    
    # 1. Upcoming Schedule Section
    message += "📅 **UPCOMING SCHEDULE:**\n"
    has_any_class = False
    for day in schedule_days:
        if day['classes']:
            has_any_class = True
            message += f"📍 {day['label']}:\n"
            for s in day['classes']:
                message += f"• {s['code']} - {s['desc']}\n"
                for t in s['times']:
                    message += f"  🕒 {t}\n"
            message += "\n"
    
    if not has_any_class:
        message += "No classes found for the next 3 days. Free time! 🌊\n\n"

    # 2. Tasks Section
    if tasks:
        message += "📝 **UPCOMING TASKS/MILESTONES:**\n"
        for t in tasks:
            message += f"• **{t['event']}**\n"
            message += f"  📅 Date: {t['date']}\n"
        message += "\n"
    else:
        message += "📝 No major tasks due in the next 7 days. Chill muna! 🌊\n"
    
    message += "Stay productive and prepared! 💪"
    _deliver(user_info, message)

def _deliver(user_info, text):
    platform = user_info.get('platform', 'messenger')
    uid = user_info.get('uid')
    
    if platform == 'messenger':
        cmd = [PYTHON_PATH, SEND_MESSENGER_PATH, "--platform", "messenger", "--text", text, "--recipient_id", uid]
        subprocess.run(cmd)
    elif platform == 'telegram':
        cmd = [PYTHON_PATH, SEND_TELEGRAM_PATH, "--platform", "telegram", "--text", text, "--recipient_id", uid]
        subprocess.run(cmd)

if __name__ == "__main__":
    check_all_users()
