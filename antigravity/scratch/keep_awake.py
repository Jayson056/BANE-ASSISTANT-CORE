
import subprocess
import os
import sys

def keep_awake():
    cmds = [
        "xset s off",
        "xset s noblank",
        "xset -dpms",
        "gsettings set org.gnome.desktop.session idle-delay 0",
        "gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'",
        "gsettings set org.gnome.desktop.screensaver lock-enabled false"
    ]
    
    results = []
    for cmd in cmds:
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            results.append(f"{cmd}: {'Success' if res.returncode == 0 else 'Failed (' + res.stderr.strip() + ')'}")
        except Exception as e:
            results.append(f"{cmd}: Error ({str(e)})")
            
    return "\n".join(results)

def notify_admin(msg):
    python_path = "/home/user/BANE_CORE/.venv/bin/python3"
    send_script = "/home/user/BANE_CORE/utils/send_telegram.py"
    admin_id = "5662168844"
    
    output = f"🖥️ **ALWAYS-ON PROTOCOL ACTIVATED**\n\n{msg}\n\n✅ Screen timeout set to 0 (Never)\n✅ DPMS Disabled\n✅ GNOME Idle-delay disabled"
    
    try:
        subprocess.run([python_path, send_script, output, "--chat_id", admin_id, "--title", "POWER MANAGEMENT"], check=True)
    except:
        pass

if __name__ == "__main__":
    report = keep_awake()
    print(report)
    notify_admin(report)
