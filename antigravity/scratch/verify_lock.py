
import sys
import os
sys.path.append("/home/user/BANE_CORE")
from core.security import is_locked, is_allowed_path

workspace_path = "/home/user/BANE_CORE_Workspaces/USER-DATA/USER_INSTANCE_ID/School/test.txt"
core_path = "/home/user/BANE_CORE/core/router.py"

print(f"System Locked: {is_locked()}")
print(f"Can edit workplace? ({workspace_path}): {is_allowed_path(workspace_path)}")
print(f"Can edit core logic? ({core_path}): {is_allowed_path(core_path)}")
