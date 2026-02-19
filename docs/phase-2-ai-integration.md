# Phase 2 — AI Integration (Dynamic UI Mapping)

> *"The UI moves. BANE adapts."*

---

## Objective

Reliably locate and interact with the Antigravity AI input interface, even as the UI repositions, resizes, or changes behavior. **No fixed coordinates. Ever.**

---

## Strategy: 3-Tier Detection

### Tier 1 — Window Targeting (FAST)
- Find Antigravity window via `wmctrl` / X11
- Bring to foreground and focus
- Narrow OCR search area to window bounds

### Tier 2 — OCR Anchor Scan (SMART)
- Screenshot the Antigravity window region
- OCR scan for anchor keywords:
  - `"Ask anything"`
  - `"Type your question"`
- Extract bounding box coordinates

### Tier 3 — Heuristic Input Offset (SAFE)
- Input box is positioned below the label text
- Click center-bottom offset from anchor
- Verify cursor focus state

**If all tiers fail** → log error + notify user.

---

## Components Built

### `antigravity/window.py`
- `get_antigravity_geometry()` — Returns `(x, y, width, height)` of the Antigravity window
- Uses `wmctrl -lG` to find window by name
- Handles window not found gracefully

### `antigravity/mapper.py`
- `find_input_box()` — Locates the "Ask anything" input coordinates
- Implements the 3-tier detection strategy
- Returns `(x, y)` click coordinates

### `antigravity/injector.py`
- `inject_text(text)` — Types text into the AI input box
- Calls mapper to find input → clicks → types → submits
- Handles focus loss and re-focus

### `antigravity/monitor.py`
- `get_ai_state()` — Returns current AI state: `idle`, `busy`, `error`
- OCR-based state detection from UI status indicators
- Used by the wait loop to know when AI is done processing

### `utils/ocr_helper.py`
- `run_optimized_ocr()` — Centralized OCR with:
  - Cross-process file locking (`/tmp/bane_ocr.lock`)
  - Image downscaling for speed
  - Window cropping for accuracy
  - Grayscale conversion

---

## Key Design Decisions

1. **OCR over Accessibility API** — More robust across UI changes, no API dependency
2. **Cross-Process Lock** — Prevents Tesseract race conditions between Gunicorn workers and main process
3. **Downscaling (0.3x)** — 70% faster OCR with minimal accuracy loss
4. **Window Cropping** — Only OCR the relevant window, not the full screen

---

## Files Introduced

```
antigravity/
├── window.py
├── mapper.py
├── injector.py
├── monitor.py
└── __init__.py
utils/
└── ocr_helper.py
```

---

*Phase 2 gives BANE eyes — it can see, find, and interact with Antigravity regardless of where the UI moves.*
