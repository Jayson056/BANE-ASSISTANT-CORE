# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import subprocess
import logging

logger = logging.getLogger(__name__)

def focus_antigravity(window_name="Antigravity"):
    """
    Bring the Antigravity window to the foreground using wmctrl.
    Returns True if successful, False otherwise.
    """
    try:
        # Try finding "Antigravity"
        subprocess.run(
            ["wmctrl", "-a", window_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info(f"Focused window: {window_name}")
        return True
    except subprocess.CalledProcessError:
        # Fallback: Try "BANE" or "Walkthrough" since the user has those windows
        logger.warning(f"Window '{window_name}' not found. Trying fallbacks.")
        fallback_names = ["Manager", "BANE", "Walkthrough", "Mozilla Firefox"] 
        for name in fallback_names:
            try:
                subprocess.run(
                    ["wmctrl", "-a", name],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"Focused fallback window: {name}")
                return True
            except subprocess.CalledProcessError:
                continue
        return False
        
def get_antigravity_geometry(window_name="Antigravity"):
    """
    Returns (x, y, width, height) of the Antigravity window.
    """
    try:
        output = subprocess.check_output(["wmctrl", "-lG"], text=True)
        # Try primary window first
        for line in output.splitlines():
            if window_name.lower() in line.lower():
                parts = line.split()
                return int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        
        # Try fallbacks
        fallback_names = ["Manager", "BANE", "Walkthrough", "Mozilla Firefox"]
        for name in fallback_names:
            for line in output.splitlines():
                if name.lower() in line.lower():
                    parts = line.split()
                    return int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                    
        return None
    except Exception as e:
        logger.error(f"Failed to get window geometry: {e}")
        return None

def is_point_in_safe_window(px, py):
    """
    Checks if the point (px, py) is within any of our 'safe' app windows.
    """
    try:
        output = subprocess.check_output(["wmctrl", "-lG"], text=True)
        safe_names = ["Antigravity", "Manager", "BANE", "Walkthrough", "Mozilla Firefox"]
        
        for line in output.splitlines():
            line_lower = line.lower()
            if any(name.lower() in line_lower for name in safe_names):
                parts = line.split()
                try:
                    wx = int(parts[2])
                    wy = int(parts[3])
                    ww = int(parts[4])
                    wh = int(parts[5])
                    
                    if wx <= px <= (wx + ww) and wy <= py <= (wy + wh):
                        return True
                except:
                    continue
        return False
    except:
        return False
