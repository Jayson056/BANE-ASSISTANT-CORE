# Phase 5 — Security & Privilege Control

> *"Trust nothing. Verify everything."*

---

## Objective

Implement secure privilege escalation, password handling, and core immutability protection to ensure BANE cannot be exploited or misused.

---

## Security Architecture

### Core Immutability
```
/home/son/BANE/        ← READ-ONLY (dr-xr-xr-x)
├── core/              ← Protected
├── antigravity/       ← Protected
├── utils/             ← Protected
├── storage/           ← WRITABLE (user data)
├── Debug/             ← WRITABLE (logs)
└── config/            ← Protected (secrets)

/home/son/BANE_Workspaces/  ← WRITABLE (user projects)
└── USER-DATA/{hash}/       ← Per-user isolation
```

### Access Control Layers

| Layer | Mechanism |
|-------|-----------|
| **User Auth** | Telegram user ID whitelist / Messenger ASID whitelist |
| **Role Access** | Admin vs Guest privileges |
| **Path Restrictions** | Allowed paths list in `security.py` |
| **System Lock** | `.system_lock` file enables strict mode |
| **Maintenance Mode** | `.maintenance` file relaxes restrictions |

---

## Components Built

### `core/security.py`
- `is_locked()` — Checks if system is in lockdown
- `is_maintenance_mode()` — Checks for maintenance override
- `is_allowed_path(path)` — Validates file access requests
- `check_core_integrity()` — Verifies BANE root is protected

### `security/password_flow.py`
- Secure password injection for sudo/keyring prompts
- Memory-only storage (never written to disk)
- Immediate wipe after use
- Telegram inline confirmation required

### `security/sudo_flow.py`
- Sudo proxy for privileged operations
- Requires explicit user approval via inline buttons
- Timeout-based auto-cancel

### `security/confirm.py`
- Inline keyboard confirmation dialogs
- Yes/No/Cancel with callback handling
- Used for destructive operations

### `security/detector.py`
- Pattern detection for sudo/password prompts in AI output
- Triggers secure handling flow when detected

---

## Security Monitor

Runs every **30 seconds** via APScheduler:

```python
# Checks performed:
1. Core directory write permissions
2. Unauthorized process detection
3. File integrity snapshots
4. Lock file validation
```

---

## Password Flow

```
AI encounters sudo prompt
    ↓
detector.py identifies password request
    ↓
Telegram sends inline keyboard: "Inject Password?"
    ↓
User taps "Yes"
    ↓
password_flow.py injects password into terminal
    ↓
Password wiped from memory immediately
    ↓
Operation proceeds
```

---

## Key Design Decisions

1. **Filesystem-Level Protection** — `chmod` on directories, not application-level blocks
2. **No Stored Passwords** — Transient memory only, never persisted
3. **Whitelist over Blacklist** — Only explicitly allowed paths are accessible
4. **30-Second Monitor Cycle** — Fast enough to catch issues, light enough for CPU

---

## Files Introduced

```
core/
└── security.py
security/
├── confirm.py
├── detector.py
├── password_flow.py
└── sudo_flow.py
```

---

*Phase 5 hardens BANE against unauthorized access, accidental corruption, and privilege escalation.*
