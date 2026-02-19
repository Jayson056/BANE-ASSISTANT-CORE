# Phase 3 — Agent Command Router

> *"AI optional. Control guaranteed."*

---

## Objective

Turn BANE into a real remote operator with independent slash commands that work without AI — deterministic system control alongside AI conversation.

---

## Core Design Rule

```
If message starts with /  →  Agent (deterministic)
Else                      →  Antigravity AI (reasoning)
```

**No ambiguity. No AI guessing commands.**

---

## Agent Commands

| Command | Script | Description |
|---------|--------|-------------|
| `/screen` | `agent/screen.py` | Capture and send screenshot |
| `/rules` | `agent/rules.py` | Display BANE usage rules |
| `/quota` | `agent/quota.py` | Check AI quota/limits |
| `/save` | `agent/save.py` | Export project snapshot |
| `/watch` | `agent/watch.py` | Record screen video |
| `/hear` | `agent/hear.py` | Record audio |
| `/turbo` | `agent/turbo.py` | Toggle auto-accept mode |
| `/search` | `agent/search.py` | Web search |
| `/select_model` | `agent/select_model.py` | Switch AI model |
| `/select_skill` | `agent/select_skill.py` | Switch AI persona |
| `/sysrest` | `agent/sysrest.py` | System restart |
| `/syslogout` | `agent/syslogout.py` | System logout |
| `/passkey` | `agent/passkey.py` | Secure password injection |

---

## Command Routing Flow

```
User: /screen
    ↓
bot.py → registered handler
    ↓
agent/screen.py → pyautogui.screenshot()
    ↓
Send screenshot back to user via sender.py
```

```
User: "Write me a poem"
    ↓
bot.py → no matching command handler
    ↓
core/router.py → UniversalProcessor
    ↓
Antigravity AI processes and responds
```

---

## Components Built

### `agent/router.py`
- Central dispatch for slash commands
- Maps command strings to agent scripts
- Handles unknown commands gracefully

### `agent/` Scripts
- Each command is one self-contained Python file
- No cross-dependencies between commands
- Each handles its own input validation and response

---

## Key Design Decisions

1. **One File = One Power** — Each command is isolated, testable, replaceable
2. **Clean Fallback** — Unknown commands are not errors — they go to AI
3. **Safe Expansion** — Adding a new command = adding one file + one handler registration

---

## Files Introduced

```
agent/
├── router.py
├── screen.py
├── rules.py
├── quota.py
├── save.py
├── watch.py
├── hear.py
├── turbo.py
├── search.py
├── select_model.py
├── select_skill.py
├── sysrest.py
├── syslogout.py
├── passkey.py
└── __init__.py
```

---

*Phase 3 makes BANE a dual-mode system: intelligent AI chat + deterministic system commands.*
