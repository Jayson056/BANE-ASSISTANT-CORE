import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_school_fallback_response(user_hash: str, query: str) -> str:
    """
    Provides a text-based fallback for school-related queries 
    using local data files when AI is limited.
    """
    try:
        # 1. Locate School files
        workspace_dir = f"/home/user/BANE_CORE_Workspaces/USER-DATA/{user_hash}"
        school_dir = os.path.join(workspace_dir, "School")
        tracker_path = os.path.join(school_dir, "Live_Task_Tracker.json")
        schedule_path = os.path.join(school_dir, "My_Class_Schedule.txt")
        
        if not os.path.exists(tracker_path):
            return "⚠️ School data tracker not found in your workspace."

        with open(tracker_path, 'r') as f:
            data = json.load(f)
        
        query_l = query.lower()
        
        # 2. Match Query Intent
        
        # --- SCHEDULE / CLASSES ---
        if any(kw in query_l for kw in ["sched", "class", "oras", "subject", "sub", "friday", "monday", "tuesday", "wednesday", "thursday", "saturday"]):
            # Get current day
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            today = days[datetime.now().weekday()]
            
            classes = data.get("schedule_configuration", {}).get("CLASSES", [])
            resp = [f"📅 **SCHOOL SCHEDULE FALLBACK (Light Mode)**\nToday is {today}.\n"]
            
            found_today = False
            for c in classes:
                times = c.get("times", [])
                matching_times = [t for t in times if today[:3] in t]
                if matching_times:
                    found_today = True
                    resp.append(f"• **{c['code']} - {c['name']}**")
                    for t in matching_times:
                        resp.append(f"  └─ {t}")
            
            if not found_today:
                resp.append(f"Walang scheduled classes sa listahan ko for {today}.")
            
            # Add general look up for days mentioned in query
            for day in days:
                if day.lower() in query_l:
                    resp.append(f"\n**Schedule for {day}:**")
                    day_found = False
                    for c in classes:
                        times = [t for t in c.get("times", []) if day[:3] in t]
                        if times:
                            day_found = True
                            resp.append(f"• {c['name']} ({', '.join(times)})")
                    if not day_found:
                        resp.append("   (None)")
            
            return "\n".join(resp)

        # --- ASSIGNMENTS / TASKS / DEADLINES ---
        if any(kw in query_l for kw in ["assignment", "task", "deadline", "todo", "gawa", "project", "milestone", "event", "holiday"]):
            resp = [f"📝 **ACADEMIC TRACKER FALLBACK (Light Mode)**\n"]
            
            # Milestones (Holidays, Exams)
            milestones = data.get("major_milestones", [])
            now = datetime.now().date()
            upcoming_milestones = []
            for m in milestones:
                try:
                    m_date = datetime.strptime(m['date'], "%Y-%m-%d").date()
                    if m_date >= now:
                        upcoming_milestones.append(m)
                except: pass
            
            if upcoming_milestones:
                resp.append("**Upcoming Milestones:**")
                for m in upcoming_milestones[:3]: # Show top 3
                    date_str = m['date']
                    resp.append(f"• {date_str}: {m['event']} {('('+m['notes']+')') if 'notes' in m else ''}")
                resp.append("")

            # Current Assignments
            assignments = data.get("current_assignments", [])
            if assignments:
                resp.append("**Active Assignments:**")
                for a in assignments:
                    resp.append(f"• **{a['subject']}**")
                    resp.append(f"  └─ Task: {a['task']}")
                    resp.append(f"  └─ Status: {a['status']} ({a['submission_platform']})")
                resp.append("")
            else:
                resp.append("Wala akong makitang active assignments sa tracker.")

            return "\n".join(resp)

        # --- DEFAULT SCHOOL INFO ---
        return (
            "🎓 **SCHOOL INFO (Local Data)**\n\n"
            "Naka-connect ako sa local `Live_Task_Tracker.json` mo. "
            "Puwede mong itanong:\n"
            "• \"Ano schedule ko ngayon?\"\n"
            "• \"May assignment ba ako?\"\n"
            "• \"Kailan ang susunod na holiday/exam?\""
        )

    except Exception as e:
        logger.error(f"School fallback error: {e}")
        return f"⚠️ Error retrieving school data: {str(e)}"
