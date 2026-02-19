# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "AI_SKILLS_DIR")
STATE_FILE = os.path.join(os.path.dirname(__file__), "current_skill.txt")
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), "skill_analytics.json")
EVOLUTION_LOG = os.path.join(os.path.dirname(__file__), "persona_evolution.log")

def update_skill_analytics(skill_id, error=False, message=""):
    """Increments usage or error count for a skill and logs a detailed record."""
    if not os.path.exists(ANALYTICS_FILE):
        return
    
    event_type = "ERROR" if error else "USAGE"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. Update Aggregated Analytics
        with open(ANALYTICS_FILE, 'r') as f:
            data = json.load(f)
        
        if skill_id in data:
            if error:
                data[skill_id]["errors"] += 1
            else:
                data[skill_id]["usage"] += 1
            
            with open(ANALYTICS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        
        # 2. Update Detailed Evolution Log
        log_entry = f"[{timestamp}] [{skill_id}] [{event_type}] {message}\n"
        with open(EVOLUTION_LOG, 'a') as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Failed to update analytics/log: {e}")


SKILL_CONFIG = {
    "WORKSPACE": {"name": "Workspace Productivity", "file": "WORKSPACE.skill", "admin_only": False},
    "SCHOOL": {"name": "School & Academic", "file": "SCHOOL.skill", "admin_only": True},
    "STUDENT": {"name": "Student Tasks", "file": "STUDENT.skill", "admin_only": False},
    "RESEARCH_PAPER": {"name": "Research Papers", "file": "RESEARCH_PAPER.skill", "admin_only": True},
    "ASSIGNMENT": {"name": "Assignments", "file": "ASSIGNMENT.skill", "admin_only": True},
    "PROGRAMMING_TASK": {"name": "Programming Tasks", "file": "PROGRAMMING_TASK.skill", "admin_only": False},
    "CORE_MAINTENANCE": {"name": "Core Maintenance", "file": "CORE_MAINTENANCE.skill", "password_protected": True, "admin_only": True},
    "BUG_HUNTER": {"name": "Bug Hunter", "file": "BUG_HUNTER.skill", "admin_only": True},
    "CODE_REVIEWER": {"name": "Code Reviewer", "file": "CODE_REVIEWER.skill", "admin_only": True},
    "DATA_ANALYSIS": {"name": "Data Analysis", "file": "DATA_ANALYSIS.skill", "admin_only": True},
    "CREATIVE_WRITER": {"name": "Creative Writer", "file": "CREATIVE_WRITER.skill", "admin_only": True},
    "CYBERSECURITY": {"name": "Cybersecurity Skills", "file": "CYBER_SECURITY.skill", "admin_only": True},
    "AI_ARCHITECT": {"name": "AI Systems Architect", "file": "AI_ARCHITECT.skill", "admin_only": True},
    "PROJECT_LEAD": {"name": "Project Lead", "file": "PROJECT_LEAD.skill", "admin_only": True},
    "TECH_WRITER": {"name": "Technical Writer", "file": "TECH_WRITER.skill", "admin_only": True},
    "MULTIMEDIA": {"name": "Multimedia Creator", "file": "MULTIMEDIA.skill", "admin_only": True},
    "AUTO_ENGAGE": {"name": "Auto Engage Mode", "file": "AUTO_ENGAGE.skill", "admin_only": True},
}

def get_current_skill():
    """Returns the current active skill ID."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                skill_id = f.read().strip()
                if skill_id in SKILL_CONFIG:
                    return skill_id
        except Exception as e:
            logger.error(f"Error reading skill state: {e}")
    
    # Default skill
    return "WORKSPACE"

def set_current_skill(skill_id):
    """Sets the current active skill ID."""
    if skill_id not in SKILL_CONFIG:
        logger.error(f"Invalid skill ID: {skill_id}")
        return False
    
    try:
        with open(STATE_FILE, "w") as f:
            f.write(skill_id)
        
        update_skill_analytics(skill_id, message=f"Skill switched to {skill_id}") # Track the switch/use
        
        # Log to conversation history
        try:
            from utils.logger import log_conversation_step
            log_conversation_step(f"🔄 GLOBAL SYSTEM: Skill switched to {SKILL_CONFIG[skill_id]['name']} ({skill_id})", "system")
        except:
            pass
            
        return True
    except Exception as e:
        logger.error(f"Error saving skill state: {e}")
        return False

def get_skill_header():
    """Returns a concise pointer header for the current active skill."""
    skill_id = get_current_skill()
    config = SKILL_CONFIG[skill_id]
    skill_file = os.path.abspath(os.path.join(SKILLS_DIR, config["file"]))
    core_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "AI_SKILLS"))
    
    # We provide the pointers and the core persona instructions.
    # The user wants "pointing file mentine not in actual message". 
    # I'll provide the paths and the core behavior, but point to the skill file for specific persona.
    # Track usage for analytics
    update_skill_analytics(skill_id, message="Header requested for message interaction")
    
    header = f"### [SYSTEM: BANE ACTIVE SKILL: {config['name']} | SKILL_FILE: {skill_file} | PERSONA: {core_file}] ###"
    return header
