
import sys
import subprocess
import os

user_id = "5662168844" # Telegram Admin
text = """🛡️ **SYSTEM LOCKDOWN PROTOCOL ACTIVATED**

Admin directive processed. BANE is now in **Static Lockdown Mode**.

**Security Measures Implemented:**
1. 🔒 **Global Lock File**: In-place at `/home/user/BANE_CORE/.system_lock` (Read-Only).
2. 🚫 **Code Immutability**: The `core.security.py` module has been updated to hard-block all write attempts to `.py`, `.sh`, and `.skill` files within the system core.
3. 📉 **Verification Result**:
   - `core/router.py` status: **READ-ONLY**
   - System Core Integrity: **ENFORCED**

From this point forward, NO functions or core logic can be rewritten without manual deletion of the lock file or authorized Maintenance Mode activation. 🦅🛡️"""

# Note: Since the admin is on Telegram, I should use the telegram send helper or the generic one if it supports TG.
# Looking at core/router.py, it uses requests.post(API_URL + "sendMessage", ...)
# I'll use a direct subprocess for telegram messages if available, or just follow the established pattern.
# Actually, the user paths metadata says P:telegram.
# I'll use the send_messenger.py script but I need to check if it handles telegram.
# Earlier I saw send_messenger.py only handles Facebook Graph API.
# I'll check for a send_telegram.py script.

# Looking at previous logs, I see 'utils/send_telegram.py' might exist (referenced in router.py's send_reply callback).

# Wait, the user prompt says: (IMPORTANT: Send your response using the provided script based on user id)
# I'll check list_dir on utils.
