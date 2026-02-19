
# AI_SKILLS Sandbox Configuration
# This sandbox isolates experimental AI skills from the core system.

SANDBOX_ROOT = "/home/user/BANE_CORE/antigravity/AI_SKILLS_SANDBOX"

# Sandbox Rules:
# 1. NO access to /home/user/BANE_CORE/core
# 2. NO external network access (unless explicitly whitelisted)
# 3. NO sudo privileges
# 4. Storage limited to the SANDBOX_ROOT directory

def verify_sandbox_path(path):
    if not path.startswith(SANDBOX_ROOT):
        raise SecurityError(f"Access Denied: Is outside of Sandbox ({path})")
    return True
