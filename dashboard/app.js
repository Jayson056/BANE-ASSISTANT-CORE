/* ═══════════════════════════════════════════════════════════
   BANE Dashboard — Application Logic
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    const APP_START = Date.now();
    const LOCAL_IP = window.location.hostname;
    const PORT = 8081;

    // ─── DOM References ───────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    // ─── Tab Navigation ───────────────────────────────
    function initTabs() {
        $$('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                $$('.nav-tab').forEach(t => t.classList.remove('active'));
                $$('.tab-content').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                const panel = $(`#panel-${tab.dataset.tab}`);
                if (panel) panel.classList.add('active');
            });
        });
    }

    // ─── Clock & Greeting ─────────────────────────────
    function updateClock() {
        const now = new Date();
        const hours = now.getHours();
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
        const dateStr = now.toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });

        $('#time-display').textContent = timeStr;
        $('#date-display').textContent = dateStr;

        let greeting = 'Good Morning ☀️';
        if (hours >= 12 && hours < 17) greeting = 'Good Afternoon 🌤️';
        else if (hours >= 17 && hours < 21) greeting = 'Good Evening 🌇';
        else if (hours >= 21 || hours < 5) greeting = 'Good Night 🌙';
        $('#greeting-text').textContent = greeting;
    }

    // ─── Uptime Tracker ───────────────────────────────
    function updateUptime() {
        const elapsed = Date.now() - APP_START;
        const sec = Math.floor(elapsed / 1000);
        const min = Math.floor(sec / 60);
        const hrs = Math.floor(min / 60);

        let uptimeStr;
        if (hrs > 0) uptimeStr = `${hrs}h ${min % 60}m`;
        else if (min > 0) uptimeStr = `${min}m ${sec % 60}s`;
        else uptimeStr = `${sec}s`;

        $('#uptime-value').textContent = uptimeStr;
        $('#footer-time-running').textContent = `Running for ${uptimeStr}`;

        // Animate bar (max at 24h)
        const pct = Math.min((elapsed / (24 * 60 * 60 * 1000)) * 100, 100);
        $('#uptime-bar').style.width = `${pct}%`;
    }

    // ─── Weather (Open-Meteo free API) ────────────────
    async function loadWeather() {
        try {
            // Default to Manila, PH (rough location based on timezone +08:00)
            const lat = 14.5995;
            const lon = 120.9842;
            const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&timezone=auto`;
            const res = await fetch(url);
            const data = await res.json();
            const cw = data.current_weather;

            const weatherCodes = {
                0: '☀️ Clear Sky', 1: '🌤️ Mostly Clear', 2: '⛅ Partly Cloudy',
                3: '☁️ Overcast', 45: '🌫️ Foggy', 48: '🌫️ Rime Fog',
                51: '🌦️ Light Drizzle', 53: '🌧️ Drizzle', 55: '🌧️ Heavy Drizzle',
                61: '🌧️ Light Rain', 63: '🌧️ Rain', 65: '🌧️ Heavy Rain',
                71: '🌨️ Light Snow', 73: '🌨️ Snow', 75: '🌨️ Heavy Snow',
                80: '🌦️ Light Showers', 81: '🌧️ Showers', 82: '⛈️ Heavy Showers',
                95: '⛈️ Thunderstorm', 96: '⛈️ Hail Storm', 99: '⛈️ Heavy Hail'
            };

            const wInfo = weatherCodes[cw.weathercode] || '🌡️ Unknown';
            const emoji = wInfo.split(' ')[0];
            const desc = wInfo.substring(emoji.length + 1);

            $('#weather-icon').textContent = emoji;
            $('#weather-temp').textContent = `${Math.round(cw.temperature)}°C`;
            $('#weather-desc').textContent = desc;
            $('#weather-location').textContent = '📍 Philippines';
        } catch (err) {
            $('#weather-desc').textContent = 'Weather unavailable';
            $('#weather-location').textContent = '📍 Offline mode';
        }
    }

    // ─── Network Info ─────────────────────────────────
    function updateNetworkInfo() {
        $('#network-value').textContent = 'LAN';
        $('#footer-ip').textContent = `LAN: ${LOCAL_IP}:${PORT}`;

        const publicUrl = 'https://stale-ways-fetch.loca.lt';
        if (publicUrl) {
            $('#welcome-msg').innerHTML = `this is your BANE dashboard in local<br><span style="color: var(--accent-primary)">Public: <a href="${publicUrl}" target="_blank" style="color: inherit;">${publicUrl}</a></span>`;
            $('#footer-ip').innerHTML = `LAN: ${LOCAL_IP}:${PORT} | <span style="color: var(--accent-primary)">Public: ${publicUrl}</span>`;
        }
    }

    // ─── Theme Toggle ─────────────────────────────────
    function initTheme() {
        const saved = localStorage.getItem('cb-theme') || 'dark';
        if (saved === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            $('#theme-toggle').textContent = '☀️';
        }

        $('#theme-toggle').addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            if (current === 'light') {
                document.documentElement.removeAttribute('data-theme');
                $('#theme-toggle').textContent = '🌙';
                localStorage.setItem('cb-theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                $('#theme-toggle').textContent = '☀️';
                localStorage.setItem('cb-theme', 'light');
            }
        });
    }

    // ─── Pomodoro Timer ───────────────────────────────
    function initPomodoro() {
        let totalSec = 25 * 60;
        let remainSec = totalSec;
        let timerInterval = null;
        let isRunning = false;

        const CIRCUMFERENCE = 2 * Math.PI * 88;
        const ringFill = $('#pomodoro-ring-fill');
        ringFill.style.strokeDasharray = CIRCUMFERENCE;
        ringFill.style.strokeDashoffset = 0;

        function formatTime(sec) {
            const m = Math.floor(sec / 60).toString().padStart(2, '0');
            const s = (sec % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function render() {
            $('#pomodoro-time').textContent = formatTime(remainSec);
            const pct = (totalSec - remainSec) / totalSec;
            ringFill.style.strokeDashoffset = pct * CIRCUMFERENCE;
        }

        function start() {
            if (isRunning) return;
            isRunning = true;
            timerInterval = setInterval(() => {
                remainSec--;
                if (remainSec <= 0) {
                    clearInterval(timerInterval);
                    isRunning = false;
                    remainSec = 0;
                    showToast('🍅 Time is up! Great focus session!');
                    // Increment tasks done
                    const tv = $('#tasks-value');
                    tv.textContent = parseInt(tv.textContent) + 1;
                    const bar = $('#tasks-bar');
                    bar.style.width = Math.min(parseInt(tv.textContent) * 10, 100) + '%';
                }
                render();
            }, 1000);
        }

        function pause() {
            clearInterval(timerInterval);
            isRunning = false;
        }

        function reset() {
            pause();
            remainSec = totalSec;
            render();
        }

        $('#pomo-start').addEventListener('click', start);
        $('#pomo-pause').addEventListener('click', pause);
        $('#pomo-reset').addEventListener('click', reset);

        $$('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                $$('.preset-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                totalSec = parseInt(btn.dataset.minutes) * 60;
                remainSec = totalSec;
                pause();
                render();
            });
        });

        render();
    }

    // ─── Calculator ───────────────────────────────────
    function initCalculator() {
        const input = $('#calc-input');
        let expression = '';
        let lastResult = '';

        $$('#calc-grid .calc-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const val = btn.dataset.val;

                if (val === 'C') {
                    expression = '';
                    input.value = '0';
                } else if (val === '±') {
                    if (expression.startsWith('-')) expression = expression.slice(1);
                    else if (expression) expression = '-' + expression;
                    input.value = expression || '0';
                } else if (val === '%') {
                    try {
                        expression = String(parseFloat(expression) / 100);
                        input.value = expression;
                    } catch (_) { }
                } else if (val === '=') {
                    try {
                        // Safe eval
                        const result = Function('"use strict";return (' + expression + ')')();
                        lastResult = String(result);
                        input.value = lastResult;
                        expression = lastResult;
                    } catch (_) {
                        input.value = 'Error';
                        expression = '';
                    }
                } else {
                    expression += val;
                    input.value = expression;
                }
            });
        });
    }

    // ─── Unit Converter ───────────────────────────────
    function initConverter() {
        const typeUnits = {
            length: {
                units: [
                    { val: 'm', label: 'Meters' }, { val: 'km', label: 'Kilometers' },
                    { val: 'ft', label: 'Feet' }, { val: 'mi', label: 'Miles' }
                ],
                toBase: { m: 1, km: 1000, ft: 0.3048, mi: 1609.34 }
            },
            weight: {
                units: [
                    { val: 'kg', label: 'Kilograms' }, { val: 'g', label: 'Grams' },
                    { val: 'lb', label: 'Pounds' }, { val: 'oz', label: 'Ounces' }
                ],
                toBase: { kg: 1, g: 0.001, lb: 0.453592, oz: 0.0283495 }
            },
            temp: {
                units: [
                    { val: 'c', label: 'Celsius' }, { val: 'f', label: 'Fahrenheit' },
                    { val: 'k', label: 'Kelvin' }
                ],
                convert: (val, from, to) => {
                    let celsius;
                    if (from === 'c') celsius = val;
                    else if (from === 'f') celsius = (val - 32) * 5 / 9;
                    else celsius = val - 273.15;

                    if (to === 'c') return celsius;
                    if (to === 'f') return celsius * 9 / 5 + 32;
                    return celsius + 273.15;
                }
            }
        };

        const typeSelect = $('#convert-type');
        const fromUnit = $('#convert-from-unit');
        const toUnit = $('#convert-to-unit');
        const fromInput = $('#convert-from');
        const toInput = $('#convert-to');

        function populateUnits() {
            const data = typeUnits[typeSelect.value];
            fromUnit.innerHTML = data.units.map(u => `<option value="${u.val}">${u.label}</option>`).join('');
            toUnit.innerHTML = data.units.map(u => `<option value="${u.val}">${u.label}</option>`).join('');
            if (data.units.length > 1) toUnit.selectedIndex = 1;
            doConvert();
        }

        function doConvert() {
            const t = typeSelect.value;
            const data = typeUnits[t];
            const val = parseFloat(fromInput.value);
            if (isNaN(val)) { toInput.value = ''; return; }

            if (t === 'temp') {
                toInput.value = data.convert(val, fromUnit.value, toUnit.value).toFixed(4);
            } else {
                const base = val * data.toBase[fromUnit.value];
                toInput.value = (base / data.toBase[toUnit.value]).toFixed(6);
            }
        }

        typeSelect.addEventListener('change', populateUnits);
        fromInput.addEventListener('input', doConvert);
        fromUnit.addEventListener('change', doConvert);
        toUnit.addEventListener('change', doConvert);

        populateUnits();
    }

    // ─── Color Picker ─────────────────────────────────
    function initColorPicker() {
        const input = $('#color-input');
        const preview = $('#color-preview');
        const hexLabel = $('#color-hex');
        const rgbLabel = $('#color-rgb');

        function hexToRgb(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgb(${r}, ${g}, ${b})`;
        }

        function update() {
            const hex = input.value;
            preview.style.background = hex;
            hexLabel.textContent = hex;
            rgbLabel.textContent = hexToRgb(hex);
        }

        input.addEventListener('input', update);

        $('#copy-color').addEventListener('click', () => {
            navigator.clipboard.writeText(input.value).then(() => {
                showToast(`📋 Copied ${input.value}`);
            });
        });
    }

    // ─── Password Generator ──────────────────────────
    function initPassword() {
        const display = $('#password-display');
        const lengthSlider = $('#pw-length');
        const lengthLabel = $('#pw-length-label');

        lengthSlider.addEventListener('input', () => {
            lengthLabel.textContent = `${lengthSlider.value} chars`;
        });

        function generate() {
            const len = parseInt(lengthSlider.value);
            let charset = '';
            if ($('#pw-upper').checked) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            if ($('#pw-lower').checked) charset += 'abcdefghijklmnopqrstuvwxyz';
            if ($('#pw-digits').checked) charset += '0123456789';
            if ($('#pw-symbols').checked) charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';

            if (!charset) { display.textContent = 'Select at least one option'; return; }

            let pw = '';
            const arr = new Uint32Array(len);
            crypto.getRandomValues(arr);
            for (let i = 0; i < len; i++) {
                pw += charset[arr[i] % charset.length];
            }
            display.textContent = pw;
        }

        $('#pw-generate').addEventListener('click', generate);
        $('#pw-copy').addEventListener('click', () => {
            const pw = display.textContent;
            if (pw && pw !== 'Click Generate' && pw !== 'Select at least one option') {
                navigator.clipboard.writeText(pw).then(() => {
                    showToast('📋 Password copied!');
                });
            }
        });
    }

    // ─── Notes System ─────────────────────────────────
    function initNotes() {
        const STORAGE_KEY = 'cb-notes';
        let notes = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        let activeId = null;

        function save() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        function renderList() {
            const list = $('#notes-list');
            if (notes.length === 0) {
                list.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8rem; padding: 12px;">No notes yet. Click "+ New" to create one.</p>';
                return;
            }

            list.innerHTML = notes.map(n => `
                <div class="note-item${n.id === activeId ? ' active' : ''}" data-id="${n.id}">
                    <div class="note-item-title">${n.title || 'Untitled'}</div>
                    <div class="note-item-date">${new Date(n.updated).toLocaleString()}</div>
                </div>
            `).join('');

            list.querySelectorAll('.note-item').forEach(item => {
                item.addEventListener('click', () => {
                    activeId = item.dataset.id;
                    loadNote(activeId);
                    renderList();
                });
            });
        }

        function loadNote(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            $('#note-title').value = note.title;
            $('#note-body').value = note.body;
            updateCharCount();
        }

        function updateCharCount() {
            const len = ($('#note-body').value || '').length;
            $('#note-char-count').textContent = `${len} character${len !== 1 ? 's' : ''}`;
        }

        $('#note-body').addEventListener('input', updateCharCount);

        $('#add-note-btn').addEventListener('click', () => {
            const newNote = {
                id: Date.now().toString(),
                title: '',
                body: '',
                created: Date.now(),
                updated: Date.now()
            };
            notes.unshift(newNote);
            activeId = newNote.id;
            save();
            renderList();
            loadNote(activeId);
            $('#note-title').focus();
        });

        $('#save-note-btn').addEventListener('click', () => {
            if (!activeId) {
                showToast('⚠️ Create a note first!');
                return;
            }
            const note = notes.find(n => n.id === activeId);
            if (!note) return;
            note.title = $('#note-title').value;
            note.body = $('#note-body').value;
            note.updated = Date.now();
            save();
            renderList();
            showToast('💾 Note saved!');
        });

        renderList();
        if (notes.length > 0) {
            activeId = notes[0].id;
            loadNote(activeId);
            renderList();
        }
    }

    // ─── Toast Notification ──────────────────────────
    function showToast(message) {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, 3000);
    }

    // ─── Monitoring System ────────────────────────────
    function initMonitoring() {
        const STATS_INTERVAL = 3000;
        const LOGS_INTERVAL = 5000;
        const BACKUPS_INTERVAL = 30000;
        const MISC_INTERVAL = 15000;

        // ── Fetchers ──
        async function fetchJSON(url) {
            const res = await fetch(url);
            return res.json();
        }

        async function fetchStats() {
            try { updateStatsUI(await fetchJSON('/api/status')); }
            catch (e) { console.error("Stats:", e); }
        }
        async function fetchLogs() {
            const pwd = localStorage.getItem('cb-maint-pwd') || '';
            try {
                const res = await fetch(`/api/logs?pwd=${encodeURIComponent(pwd)}`);
                if (res.status === 401) {
                    if (pwd) $('#maint-pwd-error').textContent = '❌ Incorrect Password. Access Denied.';
                    $('#log-auth-overlay').style.display = 'flex';
                    $('#log-display').style.opacity = '0.3';
                    return;
                }
                const data = await res.json();
                $('#log-auth-overlay').style.display = 'none';
                $('#log-display').style.opacity = '1';
                $('#maint-pwd-error').textContent = '';
                updateLogsUI(data);
            } catch (e) {
                console.error("Logs:", e);
            }
        }

        // ── Auth Handling ──
        if ($('#maint-pwd-submit')) {
            $('#maint-pwd-submit').addEventListener('click', () => {
                const pwd = $('#maint-pwd-input').value;
                if (!pwd) return;
                localStorage.setItem('cb-maint-pwd', pwd);
                $('#maint-pwd-error').textContent = '';
                fetchLogs();
            });

            $('#maint-pwd-input').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') $('#maint-pwd-submit').click();
            });
        }
        async function fetchBackups() {
            try { updateBackupsUI(await fetchJSON('/api/backups')); }
            catch (e) { console.error("Backups:", e); }
        }
        async function fetchWorkspaces() {
            try { updateWorkspacesUI(await fetchJSON('/api/workspaces')); }
            catch (e) { console.error("Workspaces:", e); }
        }
        async function fetchTelegram() {
            try { updateTelegramUI(await fetchJSON('/api/telegram')); }
            catch (e) { console.error("Telegram:", e); }
        }
        async function fetchSkills() {
            try { updateSkillsUI(await fetchJSON('/api/skills')); }
            catch (e) { console.error("Skills:", e); }
        }
        async function fetchNetwork() {
            try { updateNetworkUI(await fetchJSON('/api/network')); }
            catch (e) { console.error("Network:", e); }
        }
        async function fetchSecurity() {
            try { updateSecurityUI(await fetchJSON('/api/security')); }
            catch (e) { console.error("Security:", e); }
        }
        async function fetchQuota() {
            try { updateQuotaUI(await fetchJSON('/api/quota')); }
            catch (e) { console.error("Quota:", e); }
        }

        // ── UI Updaters ──
        function updateStatsUI(data) {
            const s = data.system;

            // CPU
            $('#cpu-bar').style.width = `${s.cpu}%`;
            $('#cpu-value').textContent = `${Math.round(s.cpu)}%`;

            // RAM
            $('#ram-bar').style.width = `${s.memory}%`;
            $('#ram-value').textContent = `${Math.round(s.memory)}%`;
            if (s.memory_used_gb !== undefined) {
                const rd = $('#ram-detail');
                if (rd) rd.textContent = `(${s.memory_used_gb}/${s.memory_total_gb} GB)`;
            }

            // Disk
            $('#disk-bar').style.width = `${s.disk}%`;
            $('#disk-value').textContent = `${Math.round(s.disk)}%`;
            if (s.disk_used_gb !== undefined) {
                const dd = $('#disk-detail');
                if (dd) dd.textContent = `(${s.disk_used_gb}/${s.disk_total_gb} GB)`;
            }

            // Uptime + Load
            $('#monitor-uptime').textContent = `Uptime: ${s.uptime}`;
            if (s.load_avg) {
                const la = $('#load-avg');
                if (la) la.textContent = `Load: ${s.load_avg.map(v => v.toFixed(2)).join(' / ')}`;
            }

            // Color bars based on threshold
            setBarColor('#cpu-bar', s.cpu);
            setBarColor('#ram-bar', s.memory);
            setBarColor('#disk-bar', s.disk);

            // Processes
            const procList = $('#process-list');
            procList.innerHTML = data.processes.map(p => `
                <div class="process-item">
                    <span class="proc-name">${p.name}</span>
                    <span class="proc-status ${p.status === 'Running' || p.status === 'Active' ? 'status-running' : 'status-stopped'}">
                        ${p.status}${p.pid ? ` (PID: ${p.pid})` : ''}${p.memory_mb ? ` • ${p.memory_mb} MB` : ''}
                    </span>
                </div>
            `).join('');

            // Dynamic Network Updates
            if (data.network) {
                const { local_ip, public_url, port } = data.network;
                const netVal = $('#network-value');
                if (netVal) netVal.textContent = local_ip;

                const footerIp = $('#footer-ip');
                if (footerIp) {
                    footerIp.innerHTML = `LAN: ${local_ip}:${port} | <span style="color: var(--accent-primary)">Public: ${public_url || 'Offline'}</span>`;
                }

                const welcomeMsg = $('#welcome-msg');
                if (welcomeMsg) {
                    welcomeMsg.innerHTML = `this is your BANE dashboard in local<br><span style="color: var(--accent-primary)">Public: <a href="${public_url}" target="_blank" style="color: inherit;">${public_url || 'N/A'}</a></span>`;
                }
            }
        }

        function setBarColor(selector, value) {
            const bar = $(selector);
            if (!bar) return;
            if (value > 85) bar.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
            else if (value > 60) bar.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
            else bar.style.background = 'var(--accent-gradient)';
        }

        function updateLogsUI(data) {
            if (data.error) {
                $('#log-display').innerHTML = `<div class="log-line" style="color: var(--accent-red)">${data.error}</div>`;
                return;
            }
            $('#log-filename').textContent = data.filename || 'unknown';
            const container = $('#log-display');
            const isAtBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 20;
            container.innerHTML = (data.lines || []).map(line => {
                let cls = 'log-line';
                if (line.includes('ERROR') || line.includes('error')) cls += ' log-error';
                else if (line.includes('WARNING') || line.includes('warning')) cls += ' log-warn';
                return `<div class="${cls}">${line}</div>`;
            }).join('');
            if (isAtBottom) container.scrollTop = container.scrollHeight;
        }

        function updateBackupsUI(data) {
            const list = $('#backup-list');
            if (!data || data.length === 0) {
                list.innerHTML = '<tr><td colspan="4" style="text-align:center">No snapshots found.</td></tr>';
                return;
            }
            list.innerHTML = data.map(b => `
                <tr>
                    <td><b>${b.name}</b></td>
                    <td>${b.size}</td>
                    <td>${new Date(b.date).toLocaleString()}</td>
                    <td><button class="backup-action-btn" title="View details">📋 Info</button></td>
                </tr>
            `).join('');
        }

        function updateWorkspacesUI(data) {
            const grid = $('#workspace-grid');
            if (!data || data.length === 0) {
                grid.innerHTML = '<div class="loading-spinner">No projects found.</div>';
                return;
            }
            grid.innerHTML = data.map(w => `
                <div class="workspace-item">
                    <div class="ws-name">📂 ${w.name}</div>
                    <div class="ws-meta">
                        <span>📄 ${w.file_count} files</span>
                        <span>🕐 ${new Date(w.last_modified).toLocaleDateString()}</span>
                    </div>
                </div>
            `).join('');
        }

        function updateTelegramUI(data) {
            const el = $('#tg-status-value');
            if (!el) return;
            if (data.running) {
                let label = `Online (PID: ${data.pid})`;
                if (data.bot_username) label += ` @${data.bot_username}`;
                el.textContent = label;
                el.className = 'tg-value online';
            } else if (data.api_reachable) {
                el.textContent = 'API OK (Process Not Found)';
                el.className = 'tg-value online';
            } else {
                el.textContent = 'Offline';
                el.className = 'tg-value offline';
            }
        }


        function updateNetworkUI(data) {
            // ── Connectivity Status ──
            const connEl = $('#net-connectivity');
            if (connEl) {
                const dot = connEl.querySelector('.net-status-dot');
                const label = connEl.querySelector('.net-status-label');
                if (data.internet.connected) {
                    dot.className = 'net-status-dot online';
                    const latStr = data.internet.latency_ms ? ` • ${data.internet.latency_ms}ms latency` : '';
                    const dnsStr = data.internet.dns_ok ? ' • DNS ✓' : ' • DNS ✗';
                    label.textContent = `Internet Connected${latStr}${dnsStr}`;
                } else {
                    dot.className = 'net-status-dot offline';
                    label.textContent = 'No Internet Connection';
                }
            }

            // ── Speed Gauges ──
            function formatSpeed(kbps) {
                if (kbps >= 1024) return { val: (kbps / 1024).toFixed(1), unit: 'Mbps' };
                return { val: Math.round(kbps), unit: 'kbps' };
            }
            const dl = formatSpeed(data.speed.download_kbps);
            const ul = formatSpeed(data.speed.upload_kbps);

            const dlEl = $('#net-dl-speed');
            const ulEl = $('#net-ul-speed');
            if (dlEl) {
                dlEl.textContent = dl.val;
                dlEl.parentElement.querySelector('.net-speed-unit').textContent = dl.unit;
            }
            if (ulEl) {
                ulEl.textContent = ul.val;
                ulEl.parentElement.querySelector('.net-speed-unit').textContent = ul.unit;
            }

            const latEl = $('#net-latency');
            if (latEl) latEl.textContent = data.internet.latency_ms ? Math.round(data.internet.latency_ms) : '—';

            // ── WiFi Info ──
            const wifi = data.wifi;
            if (wifi) {
                const ssidEl = $('#net-wifi-ssid');
                if (ssidEl) ssidEl.textContent = wifi.ssid || 'Unknown';
                const bandEl = $('#net-wifi-band');
                if (bandEl) {
                    bandEl.textContent = wifi.band || '';
                    bandEl.style.display = wifi.band ? 'inline' : 'none';
                }
                const sigEl = $('#net-wifi-signal');
                if (sigEl) sigEl.textContent = wifi.signal_dbm || '—';
                const qualEl = $('#net-wifi-quality');
                if (qualEl) qualEl.textContent = wifi.link_quality || '—';
                const brEl = $('#net-wifi-bitrate');
                if (brEl) brEl.textContent = wifi.bitrate || '—';
                const freqEl = $('#net-wifi-freq');
                if (freqEl) freqEl.textContent = wifi.frequency || '—';

                // Signal Bar
                let sigPct = 0;
                if (wifi.link_quality) {
                    const parts = wifi.link_quality.split('/');
                    if (parts.length === 2) sigPct = Math.round((parseInt(parts[0]) / parseInt(parts[1])) * 100);
                }
                const sigBar = $('#net-signal-bar');
                if (sigBar) {
                    sigBar.style.width = sigPct + '%';
                    if (sigPct > 70) sigBar.style.background = 'linear-gradient(90deg, #22c55e, #4ade80)';
                    else if (sigPct > 40) sigBar.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
                    else sigBar.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
                }
                const sigPctEl = $('#net-signal-pct');
                if (sigPctEl) sigPctEl.textContent = sigPct + '%';

                $('#net-wifi-info').style.display = 'block';
            } else {
                const wifiEl = $('#net-wifi-info');
                if (wifiEl) wifiEl.style.display = 'none';
            }

            // ── Interfaces ──
            const ifaceEl = $('#net-interfaces');
            if (ifaceEl && data.interfaces) {
                const typeIcons = { wifi: '📶', ethernet: '🔌' };
                ifaceEl.innerHTML = `
                    <div class="net-iface-header">Network Interfaces</div>
                    ${data.interfaces.map(iface => `
                        <div class="net-iface-card">
                            <div class="net-iface-left">
                                <span class="net-iface-status ${iface.is_up ? 'up' : 'down'}"></span>
                                <div>
                                    <div class="net-iface-name">${typeIcons[iface.type] || '🌐'} ${iface.name}</div>
                                    <div class="net-iface-type">${iface.type} • ${iface.is_up ? 'UP' : 'DOWN'}${iface.speed_mbps ? ' • ' + iface.speed_mbps + ' Mbps' : ''}</div>
                                </div>
                            </div>
                            <div style="text-align: right">
                                <div class="net-iface-ip">${iface.ipv4 || 'No IP'}</div>
                                <div class="net-iface-traffic">↑${iface.bytes_sent_mb}MB ↓${iface.bytes_recv_mb}MB</div>
                            </div>
                        </div>
                    `).join('')}
                `;
            }

            // ── Connections ──
            const connBadge = $('#net-connections');
            if (connBadge) connBadge.textContent = `🔗 Active connections: ${data.active_connections || 0}`;
        }

        function updateQuotaUI(data) {
            const list = $('#quota-list');
            const notes = $('#quota-notes');
            const sessionTotal = $('#token-session-total');
            const lastDelta = $('#token-last-delta');
            if (!list) return;

            if (data.error) {
                list.innerHTML = `<div style="color:var(--accent-red); padding:10px;">Error: ${data.error}</div>`;
                return;
            }

            // Update Token Numbers
            if (data.tokens) {
                if (sessionTotal) sessionTotal.textContent = data.tokens.session_total.toLocaleString();
                if (lastDelta) {
                    lastDelta.textContent = `+${data.tokens.last_delta.toLocaleString()} tokens last activity`;
                    lastDelta.style.color = data.tokens.last_delta > 0 ? 'var(--accent-green)' : 'var(--text-muted)';
                }
            }

            if (!data.models || data.models.length === 0) {
                list.innerHTML = '<div>No models found.</div>';
                return;
            }

            list.innerHTML = data.models.map(m => `
                <div class="process-item" style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                        <span class="proc-name" style="font-weight: 500;">${m.name}</span>
                        <span class="proc-status ${m.limited ? 'status-stopped' : 'status-running'}" style="font-size: 0.75rem; padding: 2px 8px; border-radius: 10px;">
                            ${m.status}
                        </span>
                    </div>
                </div>
            `).join('');

            if (notes && data.notes) {
                notes.textContent = data.notes;
            }
        }

        function updateSecurityUI(data) {
            const runner = $('#run-security-scan');
            if (data.status === "Scanning...") {
                runner.textContent = "⌛ Scanning";
                runner.disabled = true;
                return;
            } else {
                runner.textContent = "🔍 Scan";
                runner.disabled = false;
            }

            if (data.error) {
                $('#sec-status-label').textContent = data.error;
                return;
            }

            const summary = data.summary;
            const scoreEl = $('#sec-score');
            const labelEl = $('#sec-status-label');

            scoreEl.textContent = summary.system_status === "Healthy" ? "A+" : (summary.system_status === "Warning" ? "B" : "F");
            labelEl.textContent = summary.system_status;

            // Color status
            if (summary.system_status === "Healthy") {
                scoreEl.style.color = "var(--accent-green)";
            } else if (summary.system_status === "Warning") {
                scoreEl.style.color = "var(--accent-yellow)";
            } else {
                scoreEl.style.color = "var(--accent-red)";
            }

            $('#sec-open-ports').textContent = summary.ports_open;
            $('#sec-vulns').textContent = summary.vulnerabilities_found;
            $('#last-scan-time').textContent = `Last scan: ${new Date(data.timestamp).toLocaleString()}`;

            const list = $('#security-issues-list');
            const issues = [];

            // Collect issues
            if (data.details.open_ports.length > 0) {
                data.details.open_ports.forEach(p => {
                    issues.push({ severity: 'Low', path: `Port ${p.port}`, issue: `Exposed service: ${p.service}` });
                });
            }
            if (data.details.file_permissions.length > 0) {
                issues.push(...data.details.file_permissions);
            }
            if (data.details.exposed_secrets.length > 0) {
                issues.push(...data.details.exposed_secrets);
            }

            if (issues.length === 0) {
                list.innerHTML = '<div style="padding:10px; text-align:center; color:var(--text-muted)">No issues detected ✨</div>';
            } else {
                list.innerHTML = issues.map(iss => `
                    <div class="sec-issue ${iss.severity}">
                        <div class="sec-issue-header">
                            <span class="sec-issue-severity severity-${iss.severity}">${iss.severity}</span>
                            <span class="sec-issue-text">${iss.issue}</span>
                        </div>
                        <div class="sec-issue-path">${iss.path}</div>
                    </div>
                `).join('');
            }
        }

        const skillIcons = {
            'WORKSPACE': '🏗️', 'CORE_MAINTENANCE': '🔧', 'RESEARCH_PAPER': '📑',
            'SCHOOL': '🎓', 'STUDENT': '📝', 'PROGRAMMING_TASK': '💻',
            'DATA_ANALYSIS': '📊', 'CYBERSECURITY': '🛡️', 'BUG_HUNTER': '🐛',
            'CODE_REVIEWER': '🔍', 'CREATIVE_WRITER': '✍️', 'AI_ARCHITECT': '🏛️',
            'PROJECT_LEAD': '📋', 'TECH_WRITER': '📚', 'ASSIGNMENT': '✅'
        };

        function updateSkillsUI(data) {
            const list = $('#skills-list');
            if (!data || data.length === 0) {
                list.innerHTML = '<div class="loading-spinner">No skills configured.</div>';
                return;
            }
            list.innerHTML = data.map(s => {
                const icon = skillIcons[s.name] || '🧩';
                return `<div class="skill-tag"><span class="skill-icon">${icon}</span>${s.name}</div>`;
            }).join('');
        }

        async function fetchAnalytics() {
            try {
                const res = await fetch('/api/analytics');
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                updateAnalyticsUI(data);
            } catch (e) {
                console.error("Analytics fetch error:", e);
                $('#analytics-display').innerHTML = `<div style="color:var(--accent-red); padding:10px;">Failed to load analytics: ${e.message}</div>`;
            }
        }

        function updateAnalyticsUI(data) {
            const container = $('#analytics-display');
            $('#analytics-timestamp').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;

            if (!data || data.length === 0) {
                container.innerHTML = '<div class="loading-spinner">No analytics data available.</div>';
                return;
            }

            container.innerHTML = data.map((s, index) => {
                const icon = skillIcons[s.id] || '🧩';
                const rank = index + 1;
                const reliability = Math.min(100, Math.max(0, (s.score * 5))).toFixed(0);

                let errorsHtml = '';
                const fixedCount = s.fixed_errors || 0;

                if (s.recent_errors && s.recent_errors.length > 0) {
                    const errorList = s.recent_errors.slice(0, 3).map(err => `<div class="ana-error-item">${err}</div>`).join('');
                    errorsHtml = `
                        <div class="ana-errors-section">
                            <div class="ana-error-title">
                                <span>Recent Faults</span>
                                <button class="ana-fix-btn" onclick="fixSkillError('${s.id}')">✅ Resolve</button>
                            </div>
                            <div class="ana-error-list">${errorList}</div>
                        </div>
                    `;
                }

                return `
                    <div class="analytics-item rank-${rank}">
                        <div class="ana-rank-badge">RANK #${rank}</div>
                        
                        <div class="ana-header">
                            <div class="ana-icon-box">${icon}</div>
                            <div class="ana-id-group">
                                <div class="ana-name">${s.id}</div>
                                <div class="ana-best-use">Best for: ${s.best_use}</div>
                            </div>
                        </div>

                        <div class="ana-mission">${s.mission}</div>

                        <div class="ana-metric-container">
                            <div class="ana-metric-header">
                                <span>Reliability Score</span>
                                <span class="ana-score-val">${reliability}%</span>
                            </div>
                            <div class="ana-progress-bg">
                                <div class="ana-progress-fill" style="width: ${reliability}%"></div>
                            </div>
                        </div>

                        ${errorsHtml}

                        <div class="ana-footer">
                            <div class="ana-stat-pair">
                                <div class="ana-stat-item">
                                    <span class="ana-stat-label">Usage</span>
                                    <span class="ana-stat-value usage">${s.usage}</span>
                                </div>
                                <div class="ana-stat-item">
                                    <span class="ana-stat-label">Errors</span>
                                    <span class="ana-stat-value errors">${s.errors}</span>
                                </div>
                                <div class="ana-stat-item">
                                    <span class="ana-stat-label">Fixed</span>
                                    <span class="ana-stat-value fixed">${fixedCount}</span>
                                </div>
                            </div>
                            <div class="ana-role">${s.responsibilities}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        window.fixSkillError = async (skillId) => {
            try {
                const res = await fetch('/api/analytics/fix', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ skill_id: skillId })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`✅ Error resolved for ${skillId}. Fixed count: ${data.fixed_count}`);
                    fetchAnalytics(); // Refresh UI
                } else {
                    showToast(`❌ Failed: ${data.error}`);
                }
            } catch (e) {
                console.error(e);
            }
        };

        async function fetchMaintenanceIssues() {
            try {
                const list = $('#maintenance-list');
                const hero = $('#maint-hero');
                const count = $('#maint-count');

                const res = await fetch('/api/maintenance/issues');
                const data = await res.json();

                if (data.status === "Clean") {
                    hero.style.display = 'none';
                    list.innerHTML = '<div style="padding:15px; text-align:center; color:var(--accent-green);">✅ Core System Healthy. No recent errors.</div>';
                    return;
                }

                if (data.issues && data.issues.length > 0) {
                    hero.style.display = 'flex';
                    count.textContent = data.issues.length;

                    list.innerHTML = data.issues.map(iss => `
                        <div class="sec-issue High">
                            <div class="sec-issue-header">
                                <span class="sec-issue-severity severity-High">ERROR</span>
                                <span class="sec-issue-text">${iss.timestamp}</span>
                            </div>
                            <div class="sec-issue-path" style="margin-top:4px;">${iss.issue}</div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<div style="padding:15px; text-align:center; color:var(--text-muted);">Log file empty or not found.</div>';
                }

            } catch (e) {
                console.error("Maintenance fetch error:", e);
                $('#maintenance-list').innerHTML = `<div style="color:var(--accent-red);">Failed to check core health: ${e.message}</div>`;
            }
        }

        // ── Initial Load ──
        fetchStats();
        fetchLogs();
        fetchBackups();
        fetchWorkspaces();
        fetchTelegram();
        fetchSkills();
        fetchAnalytics();
        fetchNetwork();
        fetchSecurity();
        fetchMaintenanceIssues();
        fetchQuota();

        // ── Intervals ──
        setInterval(fetchStats, STATS_INTERVAL);
        setInterval(fetchLogs, LOGS_INTERVAL);
        setInterval(fetchBackups, BACKUPS_INTERVAL);
        setInterval(fetchWorkspaces, MISC_INTERVAL);
        setInterval(fetchTelegram, MISC_INTERVAL);
        setInterval(fetchAnalytics, 120000); // AI Analytics every 2 minutes
        setInterval(fetchNetwork, 5000);  // Network speed every 5s
        setInterval(fetchSecurity, 60000); // Security scan info every minute
        setInterval(fetchMaintenanceIssues, 30000); // Check core health every 30s
        setInterval(fetchQuota, 60000); // Refresh quota every minute

        $('#refresh-maintenance').addEventListener('click', fetchMaintenanceIssues);

        // Event listener for manual scan
        $('#run-security-scan').addEventListener('click', async () => {
            showToast('🔍 Initiating security audit...');
            await fetchSecurity();
        });
    }

    // ─── Stories System ──────────────────────────────
    function initStories() {
        const listContainer = $('#story-list');
        const contentView = $('#story-content-view');
        const playerControls = $('#story-player-controls');
        const status = $('#story-status');
        let currentStoryText = '';
        let synth = window.speechSynthesis;
        let utterance = null;

        async function loadStories() {
            try {
                const res = await fetch('/api/stories');
                const stories = await res.json();

                if (!stories || stories.length === 0) {
                    listContainer.innerHTML = '<div style="padding:10px; color:#888;">No stories found.</div>';
                    return;
                }

                listContainer.innerHTML = stories.map((s, i) => `
                    <div class="note-item story-item" data-index="${i}">
                        <div class="note-item-title">${s.title}</div>
                        <div class="note-item-date">${s.filename}</div>
                    </div>
                `).join('');

                $$('.story-item').forEach(el => {
                    el.addEventListener('click', () => {
                        $$('.story-item').forEach(x => x.classList.remove('active'));
                        el.classList.add('active');
                        const story = stories[el.dataset.index];
                        openStory(story);
                    });
                });
            } catch (e) {
                listContainer.innerHTML = '<div style="padding:10px; color:red;">Error loading stories.</div>';
            }
        }

        function openStory(story) {
            currentStoryText = story.content;
            contentView.textContent = story.content;
            playerControls.style.display = 'flex';
            stopSpeaking();
            status.textContent = 'Ready to read';
        }

        function speak() {
            if (synth.speaking) {
                synth.resume();
                status.textContent = 'Reading...';
                return;
            }
            if (!currentStoryText) return;

            utterance = new SpeechSynthesisUtterance(currentStoryText);
            utterance.onend = () => { status.textContent = 'Finished'; };
            synth.speak(utterance);
            status.textContent = 'Reading...';
        }

        function stopSpeaking() {
            if (synth.speaking) synth.cancel();
            status.textContent = 'Stopped';
        }

        $('#btn-speak-story').addEventListener('click', speak);
        $('#btn-stop-story').addEventListener('click', stopSpeaking);

        // Load initially
        loadStories();
    }

    // ─── File Manager ────────────────────────────────
    function initFileManager() {
        const folderList = $('#folder-list');
        const fileListBody = $('#file-list-body');
        const currentFolderLabel = $('#current-upload-folder');
        const uploadStatus = $('#upload-status');
        const fileInput = $('#file-upload-input');
        let activeFolder = null;

        async function loadFolders() {
            try {
                const res = await fetch('/api/workspaces'); // Reuse workspace list as top-level folders
                const folders = await res.json();

                folderList.innerHTML = folders.map(f => `
                    <div class="note-item folder-item" data-name="${f.name}">
                        <div class="note-item-title">📂 ${f.name}</div>
                        <div class="note-item-date">${f.file_count} files</div>
                    </div>
                `).join('');

                // Add click handlers
                $$('.folder-item').forEach(el => {
                    el.addEventListener('click', () => {
                        $$('.folder-item').forEach(x => x.classList.remove('active'));
                        el.classList.add('active');
                        activeFolder = el.dataset.name;
                        currentFolderLabel.textContent = activeFolder;
                        loadFiles(activeFolder);
                    });
                });
            } catch (e) {
                folderList.innerHTML = '<div style="padding:10px;">Error loading folders.</div>';
            }
        }

        async function loadFiles(folder) {
            fileListBody.innerHTML = '<tr><td colspan="3" style="text-align:center;">Loading...</td></tr>';
            $('#files-header').textContent = `Files in ${folder}`;

            try {
                const res = await fetch(`/api/files?folder=${encodeURIComponent(folder)}`);
                const data = await res.json();

                if (!data.files || data.files.length === 0) {
                    fileListBody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:20px; color:gray;">Empty folder</td></tr>';
                    return;
                }

                fileListBody.innerHTML = data.files.map(f => `
                    <tr>
                        <td>📄 ${f.name}</td>
                        <td>${formatSize(f.size)}</td>
                        <td>${new Date(f.date).toLocaleString()}</td>
                    </tr>
                `).join('');
            } catch (e) {
                fileListBody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:red;">Error loading files</td></tr>';
            }
        }

        function formatSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // Upload Logic
        fileInput.addEventListener('change', async () => {
            if (!activeFolder) {
                showToast('⚠️ Select a folder first!');
                return;
            }
            if (fileInput.files.length === 0) return;

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('folder', activeFolder);

            uploadStatus.textContent = 'Uploading...';

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await res.json();

                if (result.success) {
                    showToast(`✅ Uploaded ${file.name}`);
                    uploadStatus.textContent = 'Done!';
                    loadFiles(activeFolder); // Refresh list
                    setTimeout(() => { uploadStatus.textContent = ''; }, 2000);
                } else {
                    uploadStatus.textContent = 'Error!';
                    showToast(`❌ ${result.error}`);
                }
            } catch (e) {
                uploadStatus.textContent = 'Failed';
                showToast('❌ Upload failed');
            }
            fileInput.value = ''; // Reset
        });

        $('#refresh-files').addEventListener('click', () => {
            if (activeFolder) loadFiles(activeFolder);
        });

        loadFolders();
    }

    // ─── Connect System (Remote & Chat) ───────────────
    // ─── Connect System (Remote & Chat) ───────────────
    function initConnect() {
        let isRemoteControlEnabled = false;
        let isKeyboardEnabled = false;
        let isAudioEnabled = false;
        let isTrackpadMode = false;
        let audioStream = null;

        const screenImg = $('#remote-screen-img');
        const screenContainer = $('#remote-screen-container');
        const remoteCard = $('.remote-view-card');
        const controlBtn = $('#toggle-remote-control');
        const keyboardBtn = $('#toggle-keyboard');
        const audioBtn = $('#toggle-audio');
        const fullscreenBtn = $('#toggle-fullscreen');
        const keyboardInput = $('#remote-keyboard-input');
        const chatInput = $('#chat-input');
        const chatSend = $('#chat-send');
        const chatMessages = $('#chat-messages');

        // Fullscreen Overlay & Floating Controls
        const fsOverlay = $('#fullscreen-overlay');
        const fsClose = $('#fs-close');
        const fsControl = $('#fs-control');
        const fsKeyboard = $('#fs-keyboard');
        const fsAudio = $('#fs-audio');

        // Real-time Streaming Logic
        function requestNextFrame() {
            const panel = $('#panel-connect');
            if (panel && (panel.classList.contains('active') || remoteCard.classList.contains('fullscreen'))) {
                // Fetch next frame
                const timestamp = Date.now();
                screenImg.src = `/api/remote/screenshot?t=${timestamp}`;
                const statusBadge = $('#remote-status');
                if (statusBadge) statusBadge.innerHTML = `<span class="pulse-dot"></span><span>Live (LAN)</span>`;
            } else {
                // Background polling when tab inactive (save bandwidth)
                setTimeout(requestNextFrame, 1000);
            }
        }

        if (screenImg) {
            screenImg.onload = () => {
                setTimeout(requestNextFrame, 30);
            };
            screenImg.onerror = () => {
                setTimeout(requestNextFrame, 2000);
            };
        }

        requestNextFrame();

        // Remote Control Toggle
        function toggleControl(enable) {
            isRemoteControlEnabled = (enable !== undefined) ? enable : !isRemoteControlEnabled;
            // Default to Trackpad mode on mobile if enabling
            if (isRemoteControlEnabled && isTouchDevice()) {
                isTrackpadMode = true;
                updateControlModeUI();
            }

            const label = isRemoteControlEnabled ? '🖱️ Disable Control' : '🖱️ Enable Control';
            if (controlBtn) {
                controlBtn.textContent = label;
                controlBtn.style.background = isRemoteControlEnabled ? 'var(--accent-red)' : 'var(--accent-primary)';
            }
            if (fsControl) {
                fsControl.style.background = isRemoteControlEnabled ? 'var(--accent-red)' : 'rgba(255,255,255,0.1)';
            }
            showToast(isRemoteControlEnabled ? '🖱️ Remote control enabled' : '🖱️ Remote control disabled');
        }

        if (controlBtn) controlBtn.addEventListener('click', () => toggleControl());
        if (fsControl) fsControl.addEventListener('click', () => toggleControl());

        // Keyboard Toggle
        function toggleKeyboard() {
            if (!isRemoteControlEnabled) {
                showToast('⚠️ Enable Remote Control first!');
                return;
            }
            isKeyboardEnabled = !isKeyboardEnabled;
            const color = isKeyboardEnabled ? 'var(--accent-red)' : 'var(--accent-primary)';
            if (keyboardBtn) keyboardBtn.style.background = color;
            if (fsKeyboard) fsKeyboard.style.background = isKeyboardEnabled ? 'var(--accent-red)' : 'rgba(255,255,255,0.1)';

            if (isKeyboardEnabled) {
                keyboardInput.focus();
                showToast('⌨️ Keyboard Active. Start typing...');
                keyboardInput.addEventListener('blur', () => {
                    if (isKeyboardEnabled) setTimeout(() => keyboardInput.focus(), 10);
                }, { once: true });
            } else {
                keyboardInput.blur();
            }
        }

        if (keyboardBtn) keyboardBtn.addEventListener('click', toggleKeyboard);
        if (fsKeyboard) fsKeyboard.addEventListener('click', toggleKeyboard);

        // Audio Toggle
        function toggleAudio() {
            isAudioEnabled = !isAudioEnabled;

            if (isAudioEnabled) {
                // Create audio element for streaming
                if (!audioStream) {
                    audioStream = new Audio(`/api/remote/audio?t=${Date.now()}`);
                    audioStream.onerror = () => {
                        showToast('❌ Audio stream error');
                        isAudioEnabled = false;
                        updateAudioUI();
                    };
                }
                audioStream.play().catch(e => console.error("Audio play failed", e));
                showToast('🔊 Audio Streaming Started');
            } else {
                if (audioStream) {
                    audioStream.pause();
                    audioStream.src = '';
                    audioStream = null;
                }
                showToast('🔇 Audio Muted');
            }
            updateAudioUI();
        }

        function updateAudioUI() {
            const label = isAudioEnabled ? '🔊 Mute Audio' : '🔇 Unmute Audio';
            if (audioBtn) audioBtn.textContent = label;
            if (fsAudio) {
                fsAudio.textContent = isAudioEnabled ? '🔊' : '🔇';
                fsAudio.style.background = isAudioEnabled ? 'var(--accent-green)' : 'rgba(255,255,255,0.1)';
            }
        }

        if (audioBtn) audioBtn.addEventListener('click', toggleAudio);
        if (fsAudio) fsAudio.addEventListener('click', toggleAudio);

        // Fullscreen Toggle
        function toggleFullscreen(enable) {
            const isFS = remoteCard.classList.contains('fullscreen');
            const shouldFS = (enable !== undefined) ? enable : !isFS;

            if (shouldFS) {
                remoteCard.classList.add('fullscreen');
                fsOverlay.style.display = 'block';
                document.body.style.overflow = 'hidden';
                showToast('📺 Fullscreen Mode Active');
            } else {
                remoteCard.classList.remove('fullscreen');
                fsOverlay.style.display = 'none';
                document.body.style.overflow = '';
            }
        }

        if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => toggleFullscreen(true));
        if (fsClose) fsClose.addEventListener('click', () => toggleFullscreen(false));

        // Keyboard Input Handling
        if (keyboardInput) {
            keyboardInput.addEventListener('input', async (e) => {
                if (!isKeyboardEnabled) return;
                const char = e.data;
                if (char) await sendType({ text: char });
                keyboardInput.value = '';
            });
            keyboardInput.addEventListener('keydown', async (e) => {
                if (!isKeyboardEnabled) return;
                if (['Backspace', 'Enter', 'Tab', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                    e.preventDefault();
                    await sendType({ key: e.key });
                }
            });
        }

        async function sendType(payload) {
            try {
                await fetch('/api/remote/type', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } catch (err) { console.error("Type error:", err); }
        }

        // ── Click Mode for mobile: 'left' or 'right' ──
        let clickMode = 'left';
        let lastTouchX = null;
        let lastTouchY = null;

        // ── Helper: is mobile / touch device? ──
        function isTouchDevice() {
            return window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
        }

        // ── Helper: Send delta movement (Trackpad) ──
        async function sendMove(dx, dy) {
            try {
                // Ensure small movements are sent
                await fetch(`/api/remote/control?dx=${dx.toFixed(2)}&dy=${dy.toFixed(2)}`);
            } catch (err) { console.error("Move error:", err); }
        }

        // ── Helper: send scroll to server ──
        async function sendScroll(direction, amount = 3, x = null, y = null) {
            try {
                let url = `/api/remote/scroll?direction=${direction}&amount=${amount}`;
                if (x !== null && y !== null) {
                    url += `&x=${x.toFixed(4)}&y=${y.toFixed(4)}`;
                }
                await fetch(url);
            } catch (err) { console.error("Scroll error:", err); }
        }

        // ── Helper: show scroll indicator ──
        function showScrollIndicator(text) {
            const indicator = document.getElementById('scroll-indicator');
            if (!indicator) return;
            indicator.textContent = text;
            indicator.classList.add('show');
            clearTimeout(indicator._hideTimeout);
            indicator._hideTimeout = setTimeout(() => indicator.classList.remove('show'), 600);
        }

        // ── Helper: send click to server ──
        // ── Helper: send click to server ──
        async function sendClick(x, y, button = 'left', isRelative = false) {
            try {
                let url = `/api/remote/control?click=true&button=${button}`;
                if (isRelative) {
                    // For trackpad clicks, x/y are ignored by server if not provided, or we pass 0
                    // But we want to preserve the "pos" return from server if possible
                    // Server logic handles relative clicks if x/y are missing
                } else {
                    url += `&x=${x.toFixed(4)}&y=${y.toFixed(4)}`;
                }

                const res = await fetch(url);
                const result = await res.json();

                if (result.blocked) {
                    showToast(`🛡️ ${result.reason}`);
                    return;
                }
                // Show cursor feedback
                const cursor = document.getElementById('remote-cursor');
                if (cursor && result.pos) {
                    // Convert server pixels back to % if possible, or just use returned pos if we had screen dimensions
                    // Note: result.pos is [x, y] in pixels. We need to convert to % relative to the image?
                    // It's hard to map back to local CSS % without current screen dimensions from server.
                    // For now, only show feedback if we sent X/Y (Direct Mode)
                    if (!isRelative) {
                        cursor.style.left = `${x.toFixed(4)}%`;
                        cursor.style.top = `${y.toFixed(4)}%`;
                        cursor.style.display = 'block';
                        cursor.style.background = button === 'right' ? 'var(--accent-cyan)' : 'var(--accent-red)';
                        setTimeout(() => cursor.style.display = 'none', 500);
                    }
                }
            } catch (err) { console.error("Control error:", err); }
        }

        // ── Mouse Left Click on screen image ──
        if (screenImg) {
            screenImg.addEventListener('click', async (e) => {
                if (!isRemoteControlEnabled) return;
                // If this click was triggered by a touch event we already handled, skip it
                if (e.detail === 0 && isTouchDevice()) return;
                // In trackpad mode, only handle clicks via taps in touchend
                if (isTrackpadMode) return;

                if (isKeyboardEnabled && keyboardInput) keyboardInput.focus();

                const rect = screenImg.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                await sendClick(x, y, 'left');
            });

            // ── Mouse Right Click on screen image ──
            screenImg.addEventListener('contextmenu', async (e) => {
                e.preventDefault();
                if (!isRemoteControlEnabled) return;

                const rect = screenImg.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                await sendClick(x, y, 'right');
            });

            // ── Mouse Wheel Scroll on screen image ──
            screenImg.addEventListener('wheel', async (e) => {
                if (!isRemoteControlEnabled) return;
                e.preventDefault();

                const rect = screenImg.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;

                const direction = e.deltaY > 0 ? 'down' : 'up';
                const amount = Math.max(1, Math.min(10, Math.abs(Math.round(e.deltaY / 40))));

                showScrollIndicator(direction === 'up' ? '⬆️ Scroll Up' : '⬇️ Scroll Down');
                await sendScroll(direction, amount, x, y);
            }, { passive: false });

            // ── Touch Events for Mobile ──
            // ── Touch Events for Mobile ──
            let touchStartX = 0;
            let touchStartY = 0;
            let totalMoveX = 0;
            let totalMoveY = 0;
            let lastMoveTime = 0;
            let isDragging = false;

            screenImg.addEventListener('touchstart', (e) => {
                if (!isRemoteControlEnabled) return;
                if (e.touches.length === 1) {
                    const touch = e.touches[0];
                    const rect = screenImg.getBoundingClientRect();

                    if (isTrackpadMode) {
                        touchStartX = touch.clientX;
                        touchStartY = touch.clientY;
                        totalMoveX = 0;
                        totalMoveY = 0;
                        isDragging = false;
                    } else {
                        // Direct Mode
                        lastTouchX = ((touch.clientX - rect.left) / rect.width) * 100;
                        lastTouchY = ((touch.clientY - rect.top) / rect.height) * 100;
                    }
                }
            }, { passive: true });

            screenImg.addEventListener('touchmove', (e) => {
                if (!isRemoteControlEnabled || !isTrackpadMode) return;
                // Prevent scrolling page while controlling desktop
                e.preventDefault();

                const touch = e.touches[0];
                const dx = touch.clientX - touchStartX;
                const dy = touch.clientY - touchStartY;

                touchStartX = touch.clientX;
                touchStartY = touch.clientY;

                totalMoveX += Math.abs(dx);
                totalMoveY += Math.abs(dy);

                if (totalMoveX > 5 || totalMoveY > 5) isDragging = true;

                // Throttle sending moves
                const now = Date.now();
                if (now - lastMoveTime > 30) {
                    sendMove(dx, dy);
                    lastMoveTime = now;
                }
            }, { passive: false });

            screenImg.addEventListener('touchend', async (e) => {
                if (!isRemoteControlEnabled) return;

                if (isTrackpadMode) {
                    // If tap didn't move much -> Click
                    if (!isDragging && totalMoveX < 8 && totalMoveY < 8) {
                        e.preventDefault(); // Stop synthesized click
                        await sendClick(0, 0, clickMode, true);
                        if (isKeyboardEnabled && keyboardInput) keyboardInput.focus();

                        // Visual Feedback for tap
                        showToast(clickMode === 'left' ? '👆 Click' : '👇 Right Click');
                    }
                } else {
                    // Direct Mode
                    if (lastTouchX !== null && lastTouchY !== null && !isDragging) {
                        e.preventDefault(); // Stop synthesized click
                        await sendClick(lastTouchX, lastTouchY, clickMode);
                        if (isKeyboardEnabled && keyboardInput) keyboardInput.focus();
                    }
                }
                lastTouchX = null;
                lastTouchY = null;
                isDragging = false;
            }, { passive: false });

            // Prevent default touch behaviors on the screen container
            screenContainer.addEventListener('touchmove', (e) => {
                if (isRemoteControlEnabled) e.preventDefault();
            }, { passive: false });
        }

        // ── Mobile Action Overlay Logic ──
        const mobileOverlay = document.getElementById('mouse-action-overlay');
        const mobLeftClick = document.getElementById('mob-left-click');
        const mobRightClick = document.getElementById('mob-right-click');
        const mobScrollUp = document.getElementById('mob-scroll-up');
        const mobScrollDown = document.getElementById('mob-scroll-down');

        function updateMobileOverlay() {
            if (!mobileOverlay) return;
            const panel = document.getElementById('panel-connect');
            const isConnectActive = panel && panel.classList.contains('active');
            const shouldShow = isRemoteControlEnabled && isTouchDevice() && isConnectActive;
            mobileOverlay.classList.toggle('visible', shouldShow);
        }

        function updateControlModeUI() {
            // Update button text or state if we add a dedicated toggle button later
            // For now just toast
            if (isTrackpadMode) showToast('📱 Trackpad Mode Active');
            else showToast('👆 Direct Touch Mode Active');

            // Add visual class to overlay
            if (mobileOverlay) {
                mobileOverlay.classList.toggle('trackpad-mode', isTrackpadMode);
            }
        }

        function updateClickModeUI() {
            if (mobLeftClick) mobLeftClick.classList.toggle('active-mode', clickMode === 'left');
            if (mobRightClick) mobRightClick.classList.toggle('active-mode', clickMode === 'right');
            const mobDouble = document.getElementById('mob-double-click');
            if (mobDouble) mobDouble.classList.toggle('active-mode', clickMode === 'double');
        }

        if (mobLeftClick) {
            mobLeftClick.addEventListener('click', () => {
                clickMode = 'left';
                updateClickModeUI();
                showToast('👆 Left Click mode');
            });
            // Default active
            mobLeftClick.classList.add('active-mode');
        }

        // Add Double Click Button
        if (!document.getElementById('mob-double-click')) {
            const doubleBtn = document.createElement('button');
            doubleBtn.id = 'mob-double-click';
            doubleBtn.className = 'mouse-action-btn';
            doubleBtn.title = 'Double Click Mode';
            doubleBtn.innerHTML = '2x';
            doubleBtn.onclick = () => {
                clickMode = 'double';
                updateClickModeUI();
                showToast('✌️ Double Click mode');
            };
            // Insert after right click
            if (mobRightClick) mobRightClick.after(doubleBtn);
        }

        if (mobRightClick) {
            mobRightClick.addEventListener('click', () => {
                clickMode = 'right';
                updateClickModeUI();
                showToast('👇 Right Click mode');
            });
        }

        if (mobScrollUp) {
            mobScrollUp.addEventListener('click', async () => {
                showScrollIndicator('⬆️ Scroll Up');
                await sendScroll('up', 5);
            });
        }

        if (mobScrollDown) {
            mobScrollDown.addEventListener('click', async () => {
                showScrollIndicator('⬇️ Scroll Down');
                await sendScroll('down', 5);
            });
        }

        // Add Mode Toggle Button to Mobile Overlay
        // We'll inject it if it doesn't exist since we can't easily edit HTML
        // Check if we already added it
        if (!document.getElementById('mob-mode-toggle')) {
            const modeBtn = document.createElement('button');
            modeBtn.id = 'mob-mode-toggle';
            modeBtn.className = 'mouse-action-btn';
            modeBtn.title = 'Switch Mode';
            modeBtn.innerHTML = '🎯'; // Target vs Trackpad
            modeBtn.onclick = () => {
                isTrackpadMode = !isTrackpadMode;
                modeBtn.innerHTML = isTrackpadMode ? '🖱️' : '🎯';
                showToast(isTrackpadMode ? 'Mode: Trackpad' : 'Mode: Direct Touch');
            };

            // Insert before the divider
            const divider = mobileOverlay.querySelector('.mouse-action-divider');
            if (divider) mobileOverlay.insertBefore(modeBtn, divider);
            else mobileOverlay.prepend(modeBtn);
        }

        // Update overlay when control toggles or tab changes
        // Use a MutationObserver on the control button to detect state changes
        // (avoids duplicating event listeners which caused toggle to fire multiple times)
        if (controlBtn) {
            const observer = new MutationObserver(() => setTimeout(updateMobileOverlay, 50));
            observer.observe(controlBtn, { childList: true, characterData: true, subtree: true });
        }

        // Listen for tab changes to show/hide mobile overlay
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => setTimeout(updateMobileOverlay, 100));
        });

        // Initial state
        updateMobileOverlay();

        // Chat logic
        async function fetchChatHistory() {
            const panel = $('#panel-connect');
            if (!panel || (!panel.classList.contains('active') && !remoteCard.classList.contains('fullscreen'))) return;

            try {
                const res = await fetch('/api/chat/history');
                const history = await res.json();
                renderChat(history);
            } catch (err) { console.error("Chat history error:", err); }
        }

        const playedVoices = new Set();

        function renderChat(history) {
            if (!chatMessages) return;
            const isScrolledToBottom = (chatMessages.scrollHeight - chatMessages.scrollTop <= chatMessages.clientHeight + 100);

            chatMessages.innerHTML = history.map(msg => {
                let content = escapeHtml(msg.text);
                const roleLabel = (msg.role === 'user') ? '👤 User' : '🦅 BANE Agent';

                // Voice Message Detection & Player
                if (msg.text && msg.text.includes('[VOICE_MESSAGE]:')) {
                    const path = msg.text.split('[VOICE_MESSAGE]:')[1].trim();
                    const audioUrl = `/api/audio/file?path=${encodeURIComponent(path)}`;

                    // Auto-play if not already played
                    if (!playedVoices.has(path)) {
                        playedVoices.add(path);
                        const audio = new Audio(audioUrl);
                        audio.play().catch(e => console.log("Auto-play prevented by browser policy. Click to play."));
                    }

                    content = `<div class="voice-player">
                        <span class="voice-icon">🔊</span>
                        <audio controls src="${audioUrl}" style="height: 30px"></audio>
                    </div>`;
                } else {
                    content = content.replace(/\n/g, '<br>');
                }

                return `
                <div class="chat-msg ${msg.role}">
                    <div class="msg-wrapper">
                        <div class="msg-label">${roleLabel}</div>
                        <div class="msg-bubble">${content}</div>
                    </div>
                </div>
            `}).join('');

            if (isScrolledToBottom || history.length < 5) {
                setTimeout(() => { chatMessages.scrollTop = chatMessages.scrollHeight; }, 50);
            }
        }

        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        async function sendMessage() {
            const msg = chatInput.value.trim();
            if (!msg) return;
            chatInput.value = '';
            try {
                const res = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg })
                });
                const result = await res.json();
                if (result.success) {
                    const historyRes = await fetch('/api/chat/history');
                    const history = await historyRes.json();
                    renderChat(history);
                }
            } catch (err) { showToast('❌ Failed to send message'); }
        }

        if (chatSend) chatSend.addEventListener('click', sendMessage);
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        }

        setInterval(fetchChatHistory, 5000);
        fetchChatHistory();
    }



    function initSandbox() {
        const fileList = $('#sandbox-file-list');
        const editor = $('#sandbox-editor');
        const currentFileName = $('#sandbox-current-filename');
        const saveBtn = $('#sandbox-save-file');
        const runBtn = $('#sandbox-run-script');
        const refreshBtn = $('#sandbox-refresh');
        const newBtn = $('#sandbox-new-file');
        const clearBtn = $('#sandbox-clear-output');
        const output = $('#sandbox-output');

        let activeFile = null;

        async function loadSandboxFiles() {
            try {
                const res = await fetch('/api/sandbox/files');
                const files = await res.json();
                if (files.error) {
                    fileList.innerHTML = `<div class="error">Error: ${files.error}</div>`;
                    return;
                }

                if (files.length === 0) {
                    fileList.innerHTML = `<div class="text-muted" style="padding:10px;">No payloads found.</div>`;
                    return;
                }

                fileList.innerHTML = files.map(f => `
                    <div class="sandbox-file-item ${activeFile === f.name ? 'active' : ''}" data-name="${f.name}">
                        <span>${f.name.endsWith('.py') ? '🐍' : '📄'}</span>
                        <div style="flex:1;">
                            <div style="font-weight:500;">${f.name}</div>
                            <div style="font-size:0.7rem; color:var(--text-muted);">${(f.size / 1024).toFixed(1)} KB</div>
                        </div>
                    </div>
                `).join('');

                fileList.querySelectorAll('.sandbox-file-item').forEach(item => {
                    item.addEventListener('click', () => selectFile(item.dataset.name));
                });
            } catch (err) { console.error("Sandbox list error:", err); }
        }

        async function selectFile(name) {
            activeFile = name;
            currentFileName.innerText = name;
            editor.value = 'Loading content...';
            saveBtn.disabled = true;
            runBtn.disabled = true;

            // Highlight in list
            fileList.querySelectorAll('.sandbox-file-item').forEach(item => {
                item.classList.toggle('active', item.dataset.name === name);
            });

            try {
                const res = await fetch(`/api/sandbox/read?file=${name}`);
                const data = await res.json();
                if (data.error) {
                    showToast(`❌ ${data.error}`);
                    editor.value = '';
                } else {
                    editor.value = data.content;
                    saveBtn.disabled = false;
                    runBtn.disabled = !name.endsWith('.py');
                }
            } catch (err) { showToast('❌ Read error'); }
        }

        async function saveFile() {
            if (!activeFile) return;
            saveBtn.innerText = '⏳ saving...';
            try {
                const res = await fetch('/api/sandbox/write', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file: activeFile, content: editor.value })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('✅ Saved');
                } else {
                    showToast(`❌ ${data.error}`);
                }
            } catch (err) { showToast('❌ Save failed'); }
            saveBtn.innerText = '💾 Save';
        }

        async function runScript() {
            if (!activeFile) return;
            output.innerHTML = `<div class="log-line out-info">>>> Initializing sandbox for ${activeFile}...</div>`;
            runBtn.disabled = true;

            try {
                const res = await fetch('/api/sandbox/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file: activeFile })
                });
                const data = await res.json();

                if (data.error) {
                    output.innerHTML += `<div class="log-line out-stderr">❌ System Error: ${data.error}</div>`;
                } else {
                    if (data.stdout) {
                        output.innerHTML += data.stdout.split('\n').map(line =>
                            `<div class="log-line out-stdout">${escapeHtml(line)}</div>`
                        ).join('');
                    }
                    if (data.stderr) {
                        output.innerHTML += data.stderr.split('\n').map(line =>
                            `<div class="log-line out-stderr">${escapeHtml(line)}</div>`
                        ).join('');
                    }
                    output.innerHTML += `<div class="log-line out-info">>>> Process exited with code ${data.exit_code}</div>`;
                }
                output.scrollTop = output.scrollHeight;
            } catch (err) {
                output.innerHTML += `<div class="log-line out-stderr">❌ Execution failed: ${err.message}</div>`;
            }
            runBtn.disabled = false;
        }

        refreshBtn.addEventListener('click', loadSandboxFiles);
        saveBtn.addEventListener('click', saveFile);
        runBtn.addEventListener('click', runScript);
        clearBtn.addEventListener('click', () => output.innerHTML = '<span class="text-muted">Output cleared.</span>');

        newBtn.addEventListener('click', () => {
            const name = prompt('Enter filename (e.g. payload.py):');
            if (name) {
                activeFile = name;
                currentFileName.innerText = name;
                editor.value = '# New Payload content\n\nprint("Hello from BANE Sandbox!")\n';
                saveBtn.disabled = false;
                runBtn.disabled = !name.endsWith('.py');
                saveFile().then(loadSandboxFiles);
            }
        });

        // Initial Load
        loadSandboxFiles();
    }

    // ─── Initialize Everything ────────────────────────
    function init() {
        initTabs();
        initTheme();
        initPomodoro();
        initCalculator();
        initConverter();
        initColorPicker();
        initPassword();
        initNotes();
        initMonitoring();
        initStories();
        initFileManager();
        initConnect();
        initSandbox();

        updateClock();
        updateUptime();
        updateNetworkInfo();
        loadWeather();

        // Intervals
        setInterval(updateClock, 1000);
        setInterval(updateUptime, 1000);

        // Refresh weather every 30 minutes
        setInterval(loadWeather, 30 * 60 * 1000);

        showToast('⚡ BANE Dashboard loaded!');
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
