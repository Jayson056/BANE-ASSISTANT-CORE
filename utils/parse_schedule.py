
import re
import sys 

def parse_cor(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    schedule = []
    
    subject_code_re = re.compile(r"^[A-Z]{4}\s\d{3}$")
    schedule_re = re.compile(r"^([A-Z]+)\s(\d{2}:\d{2}:\d{2}-\d{2}:\d{2}:\d{2})\s(LEC|LAB)$")
    
    current_subject = None
    
    for i, line in enumerate(lines):
        if subject_code_re.match(line):
            # If we were tracking a subject, save it
            if current_subject:
                schedule.append(current_subject)
            
            # Start new subject
            description = lines[i+1] if i+1 < len(lines) else "Unknown"
            current_subject = {
                "code": line,
                "description": description,
                "times": []
            }
        
        elif schedule_re.match(line):
            if current_subject:
                # Add schedule to current subject
                day, time, type_ = schedule_re.match(line).groups()
                current_subject['times'].append(f"{day} {time} ({type_})")

    # Append the last subject
    if current_subject:
        schedule.append(current_subject)
            
    return schedule

def format_schedule(schedule):
    output = "🎓 SCHOOL SCHEDULE / CALENDAR 📅\n"
    output += "========================================\n\n"
    
    days_map = {'M': 1, 'T': 2, 'W': 3, 'TH': 4, 'F': 5, 'S': 6, 'SU': 7}
    
    # Sort by day/time? Or just list by subject?
    # Let's list by subject first
    
    for item in schedule:
        output += f"📌 {item['code']} - {item['description']}\n"
        for time in item['times']:
            # time string: "S 16:30:00-19:30:00 (LEC)"
            parts = time.split()
            day = parts[0]
            clock = parts[1][:-3] # remove leading seconds if cleaner? No, keep as is
            # converting 16:30:00 to 4:30 PM ?
            
            output += f"   🕒 {time}\n"
        output += "\n"
        
    return output

if __name__ == "__main__":
    file_path = "/home/son/BANE/storage/users/9eb397f15a125a6d/cor_text.txt"
    try:
        schedule = parse_cor(file_path)
    except Exception as e:
        print(f"Error: {e}")
        schedule = None
        
    if not schedule:
        print("No schedule found! Check parsing logic.")
    else:
        text = format_schedule(schedule)
        print(text)
        
        # Save to file (Text)
        out_dir = "/home/son/BANE_Workspaces/USER-DATA/9eb397f15a125a6d/School/School Calendar"
        import os
        import json
        os.makedirs(out_dir, exist_ok=True)
        with open(f"{out_dir}/My_Class_Schedule.txt", "w") as f:
            f.write(text)
            
        # Save to file (JSON) for automation
        with open(f"{out_dir}/Class_Schedule.json", "w") as f:
            json.dump(schedule, f, indent=4)
            
        print(f"Schedule (Text/JSON) saved to {out_dir}/")
