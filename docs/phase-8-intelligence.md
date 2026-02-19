# Phase 8 — Intelligence Layer

> *"Think offline. Encrypt everything. Adapt always."*

---

## Objective

Add advanced intelligence capabilities: encrypted communications, offline AI, AI persona management, and token-efficient processing — making BANE smarter, safer, and more autonomous.

---

## Shadow Protocol (Encryption)

### Overview
Shadow Protocol provides **ENC[AES256]** envelope encryption for all communications between users and BANE's AI engine.

### States
| State | Behavior |
|-------|----------|
| `S:OFF` | Metadata only encrypted (user IDs, platform tags) |
| `S:ON` | Full message body encryption (input & output) |

### How It Works
```
User sends: "What is the meaning of life?"
    ↓
Shadow Protocol wraps:
    ENC[AES256]::base64(encrypted_context)
    [CTX|U:hash|P:telegram|S:OFF]
    What is the meaning of life?
    ENC[AES256]::base64(encrypted_context)
    ↓
AI receives wrapped message with encrypted metadata
    ↓
AI responds, sender.py delivers clean text to user
```

### Components
- **`antigravity/shadow_encryptor.py`** — AES-256 encryption/decryption
- **`shadow_state.json`** — Persistent ON/OFF state per user
- **`shadow_history.enc`** — Encrypted audit log
- Toggle: `/shadow_ON`, `/shadow_OFF` commands

---

## Cortex Recall (Zero-Token AI)

### Overview
Cortex Recall is BANE's **offline response engine** — it answers common queries without consuming AI tokens by using semantic similarity matching against a local knowledge base.

### Architecture
```
User message
    ↓
Cortex Recall checks similarity against stored Q&A pairs
    ↓
If confidence > threshold → Return stored answer (zero tokens)
If confidence < threshold → Forward to Antigravity AI (normal flow)
```

### `core/cortex_recall.py`
- TF-IDF vectorization with cosine similarity
- Configurable confidence thresholds:
  - `static` — Exact match patterns (greetings, commands)
  - `cortex_recall` — Semantic similarity threshold
  - `school_fallback` — Academic query patterns
- Knowledge base stored in `storage/cortex/`

### Benefits
- **Instant responses** for common queries
- **Zero API cost** for known answers
- **Graceful degradation** when AI quota is exhausted
- **Customizable** knowledge base

---

## AI Skill Manager

### `antigravity/skill_manager.py`
- Manages AI persona files (`AI_SKILLS_DIR/*.skill`)
- Switches between specialized AI behaviors
- Current skill is injected into every AI context

### Available Skills
- **Core Maintenance** — System administration and code management
- **Creative Writing** — Essays, stories, academic content
- **Coding** — Programming assistance
- Custom skills can be added as `.skill` files

### Skill Switching
```
/select_skill → Shows available skills
User selects "Creative Writing"
    ↓
skill_manager switches active persona
    ↓
All subsequent AI interactions use creative writing persona
```

---

## Model Selector

### `antigravity/model_selector.py`
- Lists available AI models in Antigravity
- Switches between models via UI automation
- Supports Gemini, Claude, GPT variants

---

## Token Tracker

### `antigravity/token_tracker.py`
- Monitors AI token usage per session
- Tracks input/output token counts
- Used by `/quota` command for reporting

---

## Quota Detector

### `antigravity/quota_detector.py`
- OCR-based detection of AI quota limit popups
- Detects "Rate limit", "Quota exceeded" messages
- Triggers Cortex Recall fallback when quota is hit
- Notifies user of quota state

---

## Key Design Decisions

1. **AES-256 for Shadow Protocol** — Military-grade encryption, proven and fast
2. **TF-IDF over Embeddings** — Lighter weight, no GPU required, good enough for known Q&A
3. **Skill Files over Config** — Each persona is a self-contained instruction file, easy to swap
4. **OCR Quota Detection** — Works without API access, reads the UI directly

---

## Files Introduced

```
antigravity/
├── shadow_encryptor.py
├── skill_manager.py
├── model_selector.py
├── quota_detector.py
├── token_tracker.py
└── AI_SKILLS_DIR/
    └── *.skill

core/
└── cortex_recall.py

storage/
└── cortex/
    └── knowledge_base.json
```

---

*Phase 8 gives BANE a brain that works offline, communicates secretly, and adapts its personality on demand.*
