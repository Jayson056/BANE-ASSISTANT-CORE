# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import os
import logging

logger = logging.getLogger(__name__)

# Define immutable core and mutable workspace
BANE_ROOT = "/home/son/BANE"
ALLOWED_PATHS = [
    "/home/son/BANE_Workspaces",
    "/home/son/BANE/storage",
    "/tmp",
    "/var/lib/bane"
]

def is_maintenance_mode():
    """
    Checks if the system is in maintenance mode.
    """
    return os.path.exists(os.path.join(BANE_ROOT, ".maintenance"))

def is_locked():
    """
    Checks if the system is in a global lockdown state.
    """
    return os.path.exists(os.path.join(BANE_ROOT, ".system_lock"))

def is_allowed_path(path):
    """
    Checks if a given path is within the allowed mutable workspaces.
    Blocks modifications t2001
    o Core System files if is_locked() is True.
    """
    if is_maintenance_mode():
        return True # All paths allowed in maintenance mode

    abs_path = os.path.abspath(path)

    # Check for System Lockdown
    if is_locked():
        # WORKSPACE PROTECTION: Allow full access to User Workspaces
        is_workspace = abs_path.startswith("/home/son/BANE_Workspaces")
        
        # SYSTEM WHITELIST: Allow logs, storage, and dashboard
        system_whitelist = [
            os.path.join(BANE_ROOT, "storage"),
            os.path.join(BANE_ROOT, "Debug"),
            os.path.join(BANE_ROOT, "dashboard"),
            os.path.join(BANE_ROOT, "logs"),
            "/tmp"
        ]
        is_system_whitelisted = any(abs_path.startswith(os.path.abspath(w)) for w in system_whitelist)

        if is_workspace:
            return True # Workplace is manageable
            
        if is_system_whitelisted:
            # Block core logic edits in whitelisted system dirs
            if "core/" in abs_path or "agent/" in abs_path:
                return False
            # Block critical scripts in system dirs
            blocked_exts = [".py", ".sh", ".skill", ".md", ".env"]
            if any(abs_path.endswith(ext) for ext in blocked_exts):
                return False
            return True
            
        # Block everything else (Core Files)
        return False

    # Standard check for non-locked state
    is_allowed = any(abs_path.startswith(os.path.abspath(p)) for p in ALLOWED_PATHS)
    
    if abs_path.startswith(os.path.abspath(BANE_ROOT)):
        if not is_allowed:
            return False

    return is_allowed

def check_core_integrity():
    """
    Checks if the BANE core directory is protected.
    """
    locked = is_locked()
    writable = os.access(BANE_ROOT, os.W_OK)
    
    if locked:
        logger.info("SYSTEM STATUS: [LOCKED] Core integrity enforced.")
        return True
    
    if writable:
        logger.warning(f"SECURITY ALERT: BANE core ({BANE_ROOT}) is writable!")
        return False
    return True
