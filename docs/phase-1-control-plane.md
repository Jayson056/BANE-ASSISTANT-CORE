# Phase 1 — Control Plane

> **B.A.N.E.** — Behavioral Automation Network Engine
> *"Vibe coding meets remote AI control."*

---

## Objective

Establish the foundational Telegram-driven control layer that:

- Forwards user messages into Antigravity AI's input interface
- Tracks Antigravity's dynamic UI in real-time
- Streams real-time AI activity (progress, errors, status)
- Executes system and agent commands independently of AI
- Survives Antigravity restarts, crashes, and system reboots

---

## Core Concept

### Message Flow (Normal Chat)

```
Telegram User
    ↓
Telegram Bot (python-telegram-bot)
    ↓
BANE Router (core/router.py)
    ↓
Context Injector (antigravity/injector.py)
    ↓
Antigravity "Ask anything" Input Box
    ↓
Antigravity AI Processing
    ↓
Response Delivery via sender.py
    ↓
User receives response
```

### Command Flow (`/command`)

```
Telegram User
    ↓
Command Parser (agent/router.py)
    ↓
Agent Script (Independent of AI)
    ↓
Direct response to Telegram
```

---

## Components Built

### `telegram_interface/bot.py`
- Bot initialization with `python-telegram-bot`
- Long polling for message reception
- Command handler registration (`/screen`, `/quota`, `/save`, etc.)
- User authentication via `auth.py`

### `telegram_interface/auth.py`
- Whitelist-based user authorization
- Admin vs guest role differentiation
- Unauthorized access blocking with logging

### `core/router.py` (Initial)
- Message routing: commands → agent, text → AI
- Telegram-specific message handler
- Reply callback for sending responses

### `utils/sender.py` (Initial)
- Telegram message delivery
- Text splitting for long messages (4096 char limit)
- Error handling and retry logic

---

## Key Design Decisions

1. **Polling over Webhooks (Telegram)** — Simpler for local deployment, no SSL required
2. **User ID Authorization** — No password, no session tokens — Telegram user ID is the identity
3. **Command Isolation** — Each `/command` maps to one agent script file
4. **AI Fallback** — Non-command messages always route to Antigravity AI

---

## Files Introduced

```
main.py
telegram_interface/
├── bot.py
├── auth.py
└── __init__.py
core/
├── router.py
└── __init__.py
utils/
├── sender.py (initial Telegram-only)
└── __init__.py
```

---

*Phase 1 establishes BANE as a reliable, always-on control surface for AI interaction.*
