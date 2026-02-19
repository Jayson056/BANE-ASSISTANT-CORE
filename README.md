# 🦅 B.A.N.E. — Behavioral Automation Network Engine

> **AI assists. Humans decide. Systems obey.**

**Created by Jayson056 (Jayson Combate)**  
**Copyright © 2026 Jayson056. All rights reserved.**

---

## Overview

**BANE** (Behavioral Automation Network Engine) is a multi-platform AI command-and-control system that bridges human intent with AI execution through **Telegram** and **Meta Messenger**. It serves as an autonomous interface layer for **Antigravity AI**, enabling you to control your coding agent remotely via chat apps.

Unlike standard chatbots, BANE actively monitors your screen, injects prompts into your local AI environment, and captures the results using vision processing—allowing for true "Agentic" workflows even when you are away from your keyboard.

---

## 💻 System Requirements

To run the **BANE Core** (Control Plane), your host machine must meet these specifications:

| Component | Recommendation | Reason |
|-----------|----------------|--------|
| **OS** | Linux (Ubuntu/Debian) | Requires `xdotool`, `scrot`, and X11 for screen control |
| **Python** | 3.10 or higher | Core logic and type hinting |
| **Memory** | 4GB+ RAM | For OCR processing and running local AI models |
| **Display** | X11 Server | Headless mode requires Xvfb; standard Desktop recommended |

### 📦 Critical Dependencies
BANE relies on specific tools to function. These **must** be installed:

1.  **Antigravity AI** (VS Code Extension) — The core reasoning engine.
2.  **System Packages**:
    - `xdotool` (Keyboard/Mouse simulation)
    - `scrot` (Screen capture)
    - `tesseract-ocr` (Vision/Text recognition)
    - `mpv` (Audio playback)
    - `ffmpeg` (Media processing)
3.  **Ngrok** — For exposing the local webhook to the internet.

---

## 🚫 Limitations

Before deploying, understand these operational constraints:

1.  **Linux Only**: The core relies heavily on Linux-specific automation tools (`xdotool`, `bash` scripts). Windows/Mac support is experimental or non-existent.
2.  **Visual Dependency**: BANE "sees" the AI interface. If the Antigravity window is minimized, obscured, or closed, BANE cannot function. It must be visible on the primary screen.
3.  **Single Tunnel (Free Plan)**: If using Ngrok Free, only **one** tunnel is active at a time. BANE intelligently proxies Messenger Webhooks via the Dashboard tunnel to work around this.
4.  **Latency**: Response times depend on OCR speed and AI inference time. It is not real-time like a WebSocket game.

---

## 🛠️ Comprehensive Installation Tutorial

### Phase 1: Environment Setup

1.  **Clone the Repository**:
    ```bash
    cd ~
    git clone https://github.com/Jayson056/BANE-ASSISTANT-CORE.git BANE
    cd BANE
    ```

2.  **Install System Dependencies**:
    ```bash
    sudo apt update
    sudo apt install python3-venv xdotool scrot tesseract-ocr mpv ffmpeg -y
    ```

3.  **Setup Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

---

### Phase 2: Configuration

1.  **Secrets Configuration**:
    Copy the example template and edit it with your keys.
    ```bash
    cp config/secrets.env.example config/secrets.env
    nano config/secrets.env
    ```
    *Fill in your Telegram Bot Token, User ID, and Messenger Tokens.*

2.  **Ngrok Setup**:
    Authenticate ngrok if you haven't already:
    ```bash
    ngrok config add-authtoken YOUR_TOKEN
    ```

3.  **Service Installation** (Optional - for auto-start):
    ```bash
    sudo cp deployment/bane.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable bane
    ```

---

### Phase 3: Launch

**Manual Start** (Recommended for first run):
```bash
./scripts/launch_dashboard.sh
```
*This handles the unified tunnel creation and starts the monitor server.*

**Service Start**:
```bash
sudo systemctl start bane
```

---



## 📊 Features & Modules

| Module | Description |
|--------|-------------|
| **Cortex Recall** | Zero-token offline knowledge retrieval system. |
| **Shadow Protocol** | AES-256 Metadata Encryption for secure comms. |
| **Universal Processor** | Unified logic for Telegram & Messenger. |
| **School Helper** | Academic task tracking and scheduling. |
| **Security Monitor** | Integrity checking and user isolation. |

---

*B.A.N.E. — Behavioral Automation Network Engine*
