# Phase 6 — Deployment & Hardening

> *"Ship it. Lock it. Forget it."*

---

## Objective

Deploy BANE as a production-grade systemd service with auto-start, logging, ngrok tunnel management, and operational monitoring.

---

## Systemd Service (`bane.service`)

```ini
[Unit]
Description=B.A.N.E. Core - Behavioral Automation Network Engine
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=300
StartLimitBurst=10

[Service]
Type=simple
User=son
Group=son
WorkingDirectory=/home/son/BANE

Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/son/.Xauthority
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/home/son/BANE

ExecStartPre=-/bin/bash -c 'cleanup stale locks'
ExecStart=/home/son/BANE/.venv/bin/python3 /home/son/BANE/main.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Key Service Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `User=son` | Run as user, not root | Principle of least privilege |
| `DISPLAY=:0` | X11 display access | Required for OCR/screenshots |
| `Restart=always` | Auto-restart on any exit | Resilience |
| `RestartSec=5` | 5 second restart delay | Prevent rapid restart loops |
| `StartLimitBurst=10` | Max 10 restarts per 5 min | Prevent infinite restart storms |

---

## Dashboard & ngrok (`scripts/launch_dashboard.sh`)

### What It Does
1. Starts Flask dashboard on port **8081**
2. Launches ngrok tunnels for:
   - **Dashboard** → Public HTTPS URL
   - **Messenger** → Public HTTPS URL (webhook callback)
3. Waits for ngrok to establish tunnels
4. Sends **Telegram startup notification** with public URLs

### Startup Notification Format
```
🦅 BANE Multi-Channel Uplink Established

🚀 Dashboard (Port 8081)
🏠 Local: http://192.168.x.x:8081
🌐 Public: https://xxx.ngrok-free.dev

💬 Messenger Gateway (Port 8082)
🌐 Public: https://xxx.ngrok-free.dev

Action Required: If the Messenger URL changed,
update the Callback URL in your Meta Developer Console
```

---

## Logging Architecture

```
Debug/Console/
├── current_session_YYYYMMDD_HHMMSS.log  # Active session log
├── messenger_access.log                  # Gunicorn access log
├── messenger_error.log                   # Gunicorn error log
└── consoleLog-{start}_to_{end}.txt       # Archived sessions

logs/
└── consoleLog-{date}.txt                 # Rotated daily logs
```

- All Python logging goes to both **stdout** (journalctl) and **file**
- Messenger gateway logs via Gunicorn's built-in handlers
- Session logs are timestamped and archived on restart

---

## Service Management Commands

```bash
# Start
sudo systemctl start bane

# Stop
sudo systemctl stop bane

# Restart
sudo systemctl restart bane

# Status
sudo systemctl status bane

# View logs (live)
journalctl -u bane.service -f

# View recent logs
journalctl -u bane.service --since "30 min ago"

# Enable auto-start on boot
sudo systemctl enable bane
```

---

## Production Checklist

- [x] Systemd service with auto-restart
- [x] User-level execution (not root)
- [x] X11 environment variables set
- [x] Singleton process lock
- [x] Stale process cleanup on start
- [x] ngrok tunnel management
- [x] Startup notification via Telegram
- [x] Session log rotation
- [x] Core directory immutability

---

*Phase 6 turns BANE from a script into a production service that starts on boot and runs forever.*
