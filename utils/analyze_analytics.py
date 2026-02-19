# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import json
import os
import re
from datetime import datetime

ANALYTICS_FILE = "/home/son/BANE/antigravity/skill_analytics.json"
EVOLUTION_LOG = "/home/son/BANE/antigravity/persona_evolution.log"

def analyze_errors():
    report = ["# 🔍 BANE Comprehensive Analytics Audit\n"]
    
    # 1. Overview from JSON
    if os.path.exists(ANALYTICS_FILE):
        with open(ANALYTICS_FILE, 'r') as f:
            data = json.load(f)
        
        total_errors = sum(s.get('errors', 0) for s in data.values())
        total_usage = sum(s.get('usage', 0) for s in data.values())
        
        report.append(f"**System Health Overview**")
        report.append(f"• **Total Interactions:** {total_usage}")
        report.append(f"• **Total Errors Recorded:** {total_errors}")
        if total_usage > 0:
            reliability = ((total_usage / (total_usage + total_errors)) * 100)
            report.append(f"• **Global System Reliability:** {reliability:.1f}%\n")

    # 2. Detailed Log Analysis
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG, 'r') as f:
            lines = f.readlines()
        
        error_counts = {}
        error_types = {}
        
        for line in lines:
            if "[ERROR]" in line:
                # Format: [Timestamp] [Skill ID] [Event Type] Context
                parts = line.split("] ", 3)
                if len(parts) >= 4:
                    skill_id = parts[1].strip("[")
                    context = parts[3].strip()
                    
                    # Count by Skill
                    error_counts[skill_id] = error_counts.get(skill_id, 0) + 1
                    
                    # Categorize Error Type
                    err_type = "Unknown"
                    if "Timeout" in context:
                        err_type = "⏱️ Timeout"
                    elif "Injection failed" in context:
                        err_type = "💉 Injection Failure"
                    elif "legacy" in context.lower():
                        err_type = "📜 Legalcy/Unlogged"
                    
                    error_types[err_type] = error_types.get(err_type, 0) + 1

        report.append(f"**Error Distribution by Skill**")
        for skill, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"• **{skill}:** {count} errors")
        
        report.append(f"\n**Common Failure Modes**")
        for etype, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"• **{etype}:** {count} occurrences")

    print("\n".join(report))

if __name__ == "__main__":
    analyze_errors()
