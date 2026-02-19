# Phase 4 — System Resilience

> *"Antigravity can die. BANE does not."*

---

## Objective

Ensure BANE survives AI crashes, network outages, and system reboots with automatic recovery and health monitoring — no human intervention required.

---

## Capabilities Added

### Auto-Recovery
- **Antigravity Watcher** (`core/watcher.py`) — Monitors if Antigravity is running; detects restarts
- **Network Watchdog** (`core/network_watchdog.py`) — Monitors internet connectivity; alerts on outages
- **Systemd Auto-Restart** — `Restart=always` with `RestartSec=5` in `bane.service`
- **Singleton Lock** — Prevents duplicate instances via `/tmp/bane_main.lock`

### Health Reporting (`/report`)
- System uptime and load average
- Memory and disk usage
- Antigravity process status
- Network connectivity state
- Active user count

### File System Access (`/ls <path>`)
- Remote directory listing via Telegram
- Restricted to authorized paths
- Formatted output with icons

---

## Startup Resilience Flow

```
System Boot
    ↓
systemd starts bane.service
    ↓
ExecStartPre: Kill lingering processes
    ↓
main.py:
    ├── Cleanup old processes on ports 8082, 5353, 5454
    ├── Start Antigravity watcher thread
    ├── Launch dashboard + ngrok
    ├── Launch Messenger gateway
    ├── Wait for Antigravity (polling every 5s)
    └── Start Telegram bot
```

### Crash Recovery

```
AI Crash Detected
    ↓
Watcher logs state change
    ↓
Watcher polls every 5s for AI return
    ↓
AI returns → re-map input box
    ↓
Resume normal operation
```

### Network Recovery

```
Network Lost
    ↓
Watchdog detects via DNS probe
    ↓
Log warning, pause outgoing requests
    ↓
Network returns → resume operations
    ↓
Notify admin via Telegram
```

---

## Components Built

### `core/watcher.py`
- Background thread monitoring Antigravity process
- Detects startup, shutdown, and restart events
- Triggers re-mapping when AI comes back online

### `core/network_watchdog.py`
- DNS probe to `api.telegram.org` every 30 seconds
- Logs connectivity events
- Prevents cascading failures during outages

### `core/self_fix.py`
- Auto-repair for known error patterns
- Can restart specific subsystems independently

---

## Key Design Decisions

1. **Watcher Thread, Not Process** — Lighter footprint, shared memory space
2. **Polling over Events** — More reliable than inotify for process monitoring
3. **Singleton Lock** — Prevents catastrophic state when systemd double-starts
4. **ExecStartPre Cleanup** — Kill old processes before starting new ones

---

## Files Introduced

```
core/
├── watcher.py
├── network_watchdog.py
└── self_fix.py
bane.service (systemd unit)
```

---

*Phase 4 makes BANE unkillable — it recovers from anything and keeps running.*
