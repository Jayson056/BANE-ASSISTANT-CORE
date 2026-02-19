# Phase 7 — Multi-Platform Communication

> *"One brain. Multiple channels."*

---

## Objective

Extend BANE beyond Telegram to support **Meta Messenger** as a second communication platform, while maintaining a single unified processing pipeline for all platforms.

---

## Architecture

```
┌─────────────┐    ┌──────────────────┐
│  Telegram   │    │  Meta Messenger  │
│  (Polling)  │    │  (Webhook :8082) │
└──────┬──────┘    └────────┬─────────┘
       │                    │
       ▼                    ▼
┌─────────────────────────────────────┐
│        UniversalProcessor          │
│   (core/router.py)                  │
│                                     │
│  1. Platform detection              │
│  2. User initialization             │
│  3. Concurrency control             │
│  4. Cortex Recall bypass            │
│  5. Context injection → AI          │
│  6. Wait loop                       │
│  7. Response via sender.py          │
└─────────────────────────────────────┘
```

---

## Messenger Integration

### `messenger_interface/app.py`
- **Flask webhook** server running on port 8082
- Handles Meta's verification challenge (`GET /webhook`)
- Processes incoming messages (`POST /webhook`)
- Supports: text, images, audio, video, files, stickers

### Webhook Setup
```
Meta Developer Console → Your App → Webhooks
Callback URL: https://{ngrok-url}/webhook
Verify Token: (from config/secrets.env)
Subscriptions: messages, messaging_postbacks
```

### Message Types Supported

| Type | Telegram | Messenger |
|------|----------|-----------|
| Text | ✅ | ✅ |
| Photos | ✅ | ✅ |
| Documents | ✅ | ✅ |
| Voice/Audio | ✅ | ✅ |
| Video | ✅ | ✅ |
| Stickers | ✅ | ✅ |
| Location | ✅ | — |
| Reactions | — | ✅ (auto) |

---

## Unified Sender (`utils/sender.py`)

Single entry point for all message delivery:

```bash
# Telegram
python3 utils/sender.py --platform telegram --recipient_id 123456 --text "Hello"

# Messenger
python3 utils/sender.py --platform messenger --recipient_id 10087... --text "Hello"

# With attachment
python3 utils/sender.py --platform messenger --recipient_id 10087... --file /path/to/file.pdf
```

### Features
- **Auto text splitting** — Telegram: 4096 chars, Messenger: 2000 chars
- **Markdown support** — Telegram: native Markdown, Messenger: plain text
- **Shadow Protocol** — Automatic encryption when enabled
- **File attachments** — Photos, documents, audio, video
- **Message reactions** — Messenger emoji reactions

---

## Multi-User Isolation

```
/home/son/BANE/storage/users/
├── {telegram_hash}/           # Telegram user
│   ├── identity.json
│   ├── conversation_history.txt
│   ├── received_files/
│   └── PRIVACY_NOTICE_ACK.txt
│
└── {messenger_hash}/          # Messenger user (different hash)
    ├── identity.json
    ├── conversation_history.txt
    ├── received_files/
    └── PRIVACY_NOTICE_ACK.txt

/home/son/BANE_Workspaces/USER-DATA/
├── {telegram_hash}/           # Telegram workspace
└── {messenger_hash}/          # Messenger workspace
```

### Hashing Strategy
- **Telegram**: `sha256(user_id)[:16]`
- **Messenger**: `sha256("messenger:" + asid)[:16]`
- Different hash namespaces prevent collision

---

## Emotion Engine

### `utils/emotion_lexicon.py`
- Detects emotions in AI responses
- Supports: English, Filipino, Tagalog
- Maps emotions to Messenger reactions: 😍❤️😂😮😢😡👍

### Auto-Reactions (Messenger Only)
```
AI says "I love this!" → 😍 reaction
AI says "Haha!"        → 😂 reaction
AI says "I'm sorry"    → 😢 reaction
```

---

## Key Design Decisions

1. **Unified Processor** — One pipeline, not duplicated per platform
2. **Platform-Agnostic Context** — `[CTX|U:{id}|P:{platform}|S:{state}]` tag format
3. **Webhook + Polling Hybrid** — Messenger uses webhooks, Telegram uses polling (each platform's strength)
4. **Gunicorn for Messenger** — Multi-worker, production-grade WSGI server (2 workers, 4 threads)

---

## Files Introduced

```
messenger_interface/
├── app.py
├── templates/
│   ├── privacy.html
│   └── terms.html
└── __init__.py
utils/
├── sender.py (unified)
├── user_manager.py
├── emotion_lexicon.py
└── message_history.py
```

---

*Phase 7 transforms BANE from a Telegram-only tool into a true multi-channel communication platform.*
