
import sys
import subprocess
import os
import json

user_id = "26065703363071727" 
schedule_path = "/home/user/BANE_CORE_Workspaces/USER-DATA/fed376378616f599/School/Live_Task_Tracker.json"

text = ""
if os.path.exists(schedule_path):
    with open(schedule_path, 'r') as f:
        data = json.load(f)
        
    milestones = data.get("major_milestones", [])
    
    if milestones:
        text = "🔄 **CURRENT REMINDER LOOPS (UPCOMING EVENTS):**\n\n"
        for m in milestones:
            date = m.get("date")
            event = m.get("event")
            notes = m.get("notes", "")
            time = m.get("time", "")
            
            line = f"📅 **{date}**"
            if time: line += f" @ {time}"
            line += f"\n👉 {event}"
            if notes: line += f"\n📝 *Note: {notes}*"
            
            text += line + "\n\n"
            
        text += "Yan ang mga naka-loop sa system ko ngayon! 🚀"
    else:
        text = "Galing! Wala kang active reminder loops ngayon. Free ka! 🎉"
else:
    text = "Wala pa akong nakikitang set na reminders sa workspace mo. Gusto mo mag-set tayo? 🗓️"

python_path = "/home/user/BANE_CORE/.venv/bin/python3"
send_script = "/home/user/BANE_CORE/utils/send_messenger.py"
tts_script = "/home/user/BANE_CORE/utils/text_to_speech.py"

try:
    # 1. Send Text
    print("Sending text...")
    subprocess.run([python_path, send_script, text, "--recipient_id", user_id], check=True)

    # 2. Generate Voice
    print("Generating voice...")
    res = subprocess.run([python_path, tts_script, text, "--voice", "sage"], capture_output=True, text=True)
    v_path = res.stdout.strip()
    
    if v_path and os.path.exists(v_path):
        print(f"Voice generated at: {v_path}")
        # 3. Send Voice (as attachment for Messenger)
        print("Sending voice...")
        subprocess.run([python_path, send_script, "--attachment", v_path, "--type", "audio", "--recipient_id", user_id], check=True)

except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    sys.exit(1)
