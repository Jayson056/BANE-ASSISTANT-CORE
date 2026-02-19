# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import http.server
import socketserver
import json
import os
import psutil
import datetime
import subprocess
import time
import socket
import shutil
import cgi
import urllib.parse
import pyautogui
import io
from PIL import Image
import threading

PORT = 8081
BANE_CORE_DIR = "/home/user/BANE_CORE"
WORKSPACE_DIR = "/home/user/BANE_CORE_Workspaces"
SANDBOX_DIR = os.path.join(BANE_CORE_DIR, "antigravity/AI_SKILLS_SANDBOX")
SECRETS_FILE = os.path.join(BANE_CORE_DIR, "config/secrets.env")

try:
    import sys
    # CRITICAL: Prioritize local BANE directory to avoid conflict with system 'utils' package
    if BANE_CORE_DIR not in sys.path:
        sys.path.insert(0, BANE_CORE_DIR) 
    
    # Manual injection if needed
    if BANE_CORE_DIR not in sys.path: sys.path.insert(0, BANE_CORE_DIR)
    
    from antigravity.injector import send_to_antigravity
    from antigravity.quota_detector import extract_quota_details
    from antigravity.token_tracker import get_token_metrics
except ImportError as e:
    print(f"Warning: Failed to import Antigravity modules: {e}")
    send_to_antigravity = None
    extract_quota_details = None

def detect_quota_local():
    """Local implementation of detect_quota to avoid telegram dependency."""
    info = {
        "model": os.getenv("ANTIGRAVITY_MODEL", "Unknown"),
        "provider": "Antigravity",
    }
    quota_file = os.path.join(BANE_CORE_DIR, "config/quota.yaml")
    if os.path.exists(quota_file):
        try:
            with open(quota_file, "r") as f:
                info["notes"] = f.read().strip()
        except: pass
    return info

def get_maintenance_password():
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, 'r') as f:
            for line in f:
                if line.startswith("MAINTENANCE_PASSWORD="):
                    return line.split("=")[1].strip().strip('"')
    return "" # No fallback — password must be set in secrets.env

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class MonitorHandler(http.server.SimpleHTTPRequestHandler):
    chat_history = []
    pyautogui_lock = threading.Lock()
    
    proxy_lock = threading.Lock()

    def handle_webhook_proxy(self):
        if not self.path.startswith('/webhook'):
            return False
            
        try:
            import requests
            target_url = f"http://localhost:8082{self.path}"
            headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
            
            # Simple Proxy Logic
            if self.command == 'GET':
                resp = requests.get(target_url, headers=headers, timeout=5)
            elif self.command == 'POST':
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length)
                resp = requests.post(target_url, headers=headers, data=data, timeout=10)
            
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                    self.send_header(k, v)
            
            self.send_header('Content-Length', str(len(resp.content)))
            self.end_headers()
            self.wfile.write(resp.content)
            return True
        except Exception as e:
            print(f"Proxy Error: {e}")
            self.send_error(502, f"Proxy Error: {e}")
            return True

    def do_GET(self):
        if self.handle_webhook_proxy():
            return
        if self.path == '/api/status':
            self._json_response(self.get_bane_status())
        elif self.path.startswith('/api/logs'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            password = params.get('pwd', [''])[0]
            if password == get_maintenance_password():
                self._json_response(self.get_latest_logs())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', 'http://localhost:8081')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized: Maintenance Password Required"}).encode())
        elif self.path == '/api/backups':
            self._json_response(self.get_backups())
        elif self.path == '/api/workspaces':
            self._json_response(self.get_workspaces())
        elif self.path == '/api/telegram':
            self._json_response(self.get_telegram_status())
        elif self.path == '/api/skills':
            self._json_response(self.get_ai_skills())
        elif self.path == '/api/analytics':
            self._json_response(self.get_skill_analytics())
        elif self.path == '/api/maintenance/issues':
            self._json_response(self.get_maintenance_issues())
        elif self.path == '/api/network':
            self._json_response(self.get_network_status())
        elif self.path == '/api/security':
            self._json_response(self.get_security_status())
        elif self.path == '/api/stories':
            self._json_response(self.get_stories())
        elif self.path == '/api/quota':
            self._json_response(self.get_quota_status())
        elif self.path.startswith('/api/remote/screenshot'):
            self.send_screenshot()
        elif self.path.startswith('/api/remote/scroll'):
            self.handle_remote_scroll()
        elif self.path.startswith('/api/remote/control'):
            self.handle_remote_control()
        elif self.path == '/api/chat/history':
            self._json_response(self.get_chat_history())
        elif self.path.startswith('/api/remote/audio'):
            self.send_audio_stream()
        elif self.path.startswith('/api/audio/file'):
            self.serve_audio_file()
        elif self.path.startswith('/api/files'):
            self._json_response(self.get_workspace_files())
        elif self.path.startswith('/api/sandbox/files'):
            self.handle_sandbox_files()
        elif self.path.startswith('/api/sandbox/read'):
            self.handle_sandbox_read()
        else:
            super().do_GET()

    def do_POST(self):
        if self.handle_webhook_proxy():
            return
        """Handle file uploads"""
        if self.path == '/api/upload':
            try:
                content_type = self.headers.get('Content-Type')
                if not content_type:
                    self.send_error(400, "Content-Type header missing")
                    return
                
                # Parse form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                target_folder = form.getvalue("folder")
                if not target_folder:
                    self._json_response({"error": "No folder specified"})
                    return
                
                # Security check: prevent directory traversal
                safe_folder = os.path.basename(target_folder)
                upload_dir = os.path.join(WORKSPACE_DIR, safe_folder)
                
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                file_item = form['file']
                if file_item.filename:
                    fn = os.path.basename(file_item.filename)
                    with open(os.path.join(upload_dir, fn), 'wb') as f:
                        shutil.copyfileobj(file_item.file, f)
                    
                    self._json_response({"success": True, "message": f"Uploaded {fn} to {safe_folder}"})
                else:
                    self._json_response({"error": "No file content"})

            except Exception as e:
                print(f"Upload error: {e}")
                self._json_response({"error": str(e)})
        elif self.path == '/api/chat/send':
            self.handle_chat_send()
        elif self.path == '/api/remote/type':
            self.handle_remote_type()
        elif self.path == '/api/sandbox/write':
            self.handle_sandbox_write()
        elif self.path == '/api/sandbox/run':
            self.handle_sandbox_run()
        else:
            self.send_error(404, "Endpoint not found")

    CHAT_FILE = os.path.join(BANE_CORE_DIR, "dashboard/chat_history.json")

    def get_chat_history(self):
        if os.path.exists(self.CHAT_FILE):
            try:
                with open(self.CHAT_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_chat_history(self, history):
        try:
            with open(self.CHAT_FILE, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Failed to save chat history: {e}")

    def handle_chat_send(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(length).decode('utf-8')
            data = json.loads(post_data)
            msg = data.get('message', '')
            if msg:
                history = self.get_chat_history()
                
                # Add User Message
                history.append({"role": "user", "text": msg, "time": datetime.datetime.now().isoformat()})
                
                # Send to Antigravity (Real Injection)
                if send_to_antigravity:
                    with self.pyautogui_lock:
                        success, status = send_to_antigravity(msg)
                else:
                    success, status = False, "Antigravity module not loaded"

                if success:
                    # System confirmation only
                    pass
                else:
                    err_msg = f"Failed to send: {status}"
                    history.append({"role": "error", "text": err_msg, "time": datetime.datetime.now().isoformat()})
                
                # Limit history
                if len(history) > 100:
                    history = history[-100:]
                
                self.save_chat_history(history)
                self._json_response({"success": success, "status": status})
            else:
                self._json_response({"error": "Empty message"})
        except Exception as e:
            self._json_response({"error": str(e)})

    # --- SANDBOX HANDLERS ---
    def handle_sandbox_files(self):
        try:
            files = []
            if not os.path.exists(SANDBOX_DIR):
                os.makedirs(SANDBOX_DIR, exist_ok=True)
            for f in os.listdir(SANDBOX_DIR):
                if f.endswith('.py') or f.endswith('.sh') or f.endswith('.txt'):
                    path = os.path.join(SANDBOX_DIR, f)
                    files.append({
                        "name": f,
                        "size": os.path.getsize(path),
                        "mtime": os.path.getmtime(path)
                    })
            self._json_response(sorted(files, key=lambda x: x['mtime'], reverse=True))
        except Exception as e:
            self._json_response({"error": str(e)})

    def handle_sandbox_read(self):
        try:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            filename = params.get('file', [''])[0]
            if not filename or '..' in filename:
                self._json_response({"error": "Invalid filename"})
                return
            
            path = os.path.join(SANDBOX_DIR, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self._json_response({"content": f.read()})
            else:
                self._json_response({"error": "File not found"})
        except Exception as e:
            self._json_response({"error": str(e)})

    def handle_sandbox_write(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            filename = data.get('file')
            content = data.get('content', '')
            
            if not filename or '..' in filename:
                self._json_response({"error": "Invalid filename"})
                return

            path = os.path.join(SANDBOX_DIR, filename)
            # Ensure directory is writable during the write
            os.chmod(SANDBOX_DIR, 0o755)
            with open(path, 'w') as f:
                f.write(content)
            os.chmod(SANDBOX_DIR, 0o555) # Re-lock
            self._json_response({"success": True})
        except Exception as e:
            self._json_response({"error": str(e)})

    def handle_sandbox_run(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            filename = data.get('file')
            
            if not filename or '..' in filename:
                self._json_response({"error": "Invalid filename"})
                return

            launcher = os.path.join(SANDBOX_DIR, "sandbox_run.sh")
            script_path = os.path.join(SANDBOX_DIR, filename)
            
            # Execute bwrap via the launcher script
            process = subprocess.Popen(
                ['bash', launcher, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=30)
            
            self._json_response({
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode
            })
        except subprocess.TimeoutExpired:
            process.kill()
            self._json_response({"error": "Execution timed out (30s limit)"})
        except Exception as e:
            self._json_response({"error": str(e)})

    def handle_remote_type(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(length).decode('utf-8')
            data = json.loads(post_data)
            
            text = data.get('text')
            key = data.get('key')
            
            with self.pyautogui_lock:
                if text:
                    pyautogui.write(text)
                elif key:
                    key_map = {
                        "Enter": "enter", "Backspace": "backspace", "ArrowUp": "up", "ArrowDown": "down",
                        "ArrowLeft": "left", "ArrowRight": "right", "Escape": "esc", "Tab": "tab",
                        "Delete": "delete", "Home": "home", "End": "end", "PageUp": "pageup",
                        "PageDown": "pagedown", " ": "space"
                    }
                    if key.lower() in pyautogui.KEY_NAMES:
                         pyautogui.press(key.lower())
                    elif key in key_map:
                         pyautogui.press(key_map[key])
                    elif len(key) == 1:
                         pyautogui.press(key)
                        
            self._json_response({"success": True})
        except Exception as e:
            self._json_response({"error": str(e)})

    def send_screenshot(self):
        try:
            with self.pyautogui_lock:
                screenshot = pyautogui.screenshot()
                # Optional: resize for performance
                screenshot.thumbnail((1280, 720))
                
                img_byte_arr = io.BytesIO()
                screenshot.save(img_byte_arr, format='JPEG', quality=70)
                img_byte_arr = img_byte_arr.getvalue()

            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:8081')
            self.end_headers()
            self.wfile.write(img_byte_arr)
        except Exception as e:
            self.send_error(500, str(e))

    # Dead zones where clicks are BLOCKED to protect window controls
    # Format: (x_min%, y_min%, x_max%, y_max%) — percentage-based
    CLICK_DEAD_ZONES = [
        # Window control buttons — much smaller top-right corner (close button mostly)
        (98, 0, 100, 2),
        # VS Code / App top-right utility area (heavily reduced)
        (95, 0, 98, 2),
        # Title bar protection — reduced to a very thin line at the extreme top
        (0, 0, 100, 0.8),
    ]

    def _is_in_dead_zone(self, x_pct, y_pct):
        """Check if click coordinates fall within a protected dead zone."""
        for (x1, y1, x2, y2) in self.CLICK_DEAD_ZONES:
            if x1 <= x_pct <= x2 and y1 <= y_pct <= y2:
                return True
        return False

    def handle_remote_control(self):
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            # Check for absolute coordinates (touch screen style)
            x_pct = float(params.get('x', [0])[0]) if 'x' in params else None
            y_pct = float(params.get('y', [0])[0]) if 'y' in params else None
            
            # Check for relative movement (trackpad style)
            dx = float(params.get('dx', [0])[0])
            dy = float(params.get('dy', [0])[0])
            
            click = params.get('click', ['false'])[0].lower() == 'true'
            button = params.get('button', ['left'])[0].lower()  # 'left' or 'right'

            with self.pyautogui_lock:
                screen_width, screen_height = pyautogui.size()
                
                # Handling Movement
                if dx != 0 or dy != 0:
                    # Relative movement (Trackpad)
                    # Scale sensitivity as needed, maybe pass a sensitivity param later
                    pyautogui.moveRel(dx * 2, dy * 2) 
                    
                elif x_pct is not None and y_pct is not None:
                    # Absolute positioning (Touchscreen)
                    target_x = int((x_pct / 100) * screen_width)
                    target_y = int((y_pct / 100) * screen_height)
                    pyautogui.moveTo(target_x, target_y)
                
                if click:
                    # Only check dead zones for ABSOLUTE positioning clicks to be safe
                    # For relative clicks (trackpad), we assume the user positioned the mouse where they wanted
                    if x_pct is not None and y_pct is not None:
                        if self._is_in_dead_zone(x_pct, y_pct):
                            self._json_response({
                                "success": False, 
                                "blocked": True,
                                "reason": "Click blocked: protected zone (window controls / title bar)",
                                "pos": [target_x, target_y]
                            })
                            return
                            
                    if button == 'right':
                        pyautogui.rightClick()
                    elif button == 'double':
                        pyautogui.doubleClick()
                    else:
                        pyautogui.click()
            
            
            # Return current position for UI feedback
            cur_x, cur_y = pyautogui.position()
            self._json_response({"success": True, "pos": [cur_x, cur_y], "button": button})
        except Exception as e:
            self._json_response({"error": str(e)})

    def handle_remote_scroll(self):
        """Handle scroll requests from the dashboard (mouse wheel emulation)."""
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            direction = params.get('direction', ['down'])[0].lower()
            amount = int(params.get('amount', [3])[0])
            
            # Optional: scroll at specific cursor position
            x_pct = params.get('x', [None])[0]
            y_pct = params.get('y', [None])[0]

            with self.pyautogui_lock:
                # Move to position if provided
                if x_pct is not None and y_pct is not None:
                    screen_width, screen_height = pyautogui.size()
                    target_x = int((float(x_pct) / 100) * screen_width)
                    target_y = int((float(y_pct) / 100) * screen_height)
                    pyautogui.moveTo(target_x, target_y)
                
                # Scroll: positive = up, negative = down
                scroll_amount = amount if direction == 'up' else -amount
                pyautogui.scroll(scroll_amount)
            
            self._json_response({"success": True, "direction": direction, "amount": amount})
        except Exception as e:
            self._json_response({"error": str(e)})

    def send_audio_stream(self):
        """Stream system audio (monitor) as WAV via parec."""
        self.send_response(200)
        self.send_header('Content-type', 'audio/wav')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8081')
        self.end_headers()

        # Find monitor source
        monitor_source = None
        try:
            res = subprocess.run(['pactl', 'list', 'short', 'sources'], capture_output=True, text=True)
            for line in res.stdout.split('\n'):
                if '.monitor' in line:
                    monitor_source = line.split('\t')[1]
                    break
        except:
            pass

        cmd = ["parec", "--format=s16le", "--rate=44100", "--channels=2", "--file-format=wav"]
        if monitor_source:
            cmd.extend(["-d", monitor_source])

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                # Read chunks and write to stream
                data = process.stdout.read(8192)
                if not data:
                    break
                try:
                    self.wfile.write(data)
                except (ConnectionResetError, BrokenPipeError):
                    break
            process.terminate()
            process.wait()
        except Exception as e:
            print(f"Audio stream error: {e}")


    def serve_audio_file(self):
        """Serve a specific audio file from BANE_CORE_DIR."""
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            rel_path = params.get('path', [''])[0]
            
            if not rel_path:
                self.send_error(400, "Path parameter required")
                return
            
            # Security: ensure path is within BANE_CORE_DIR and is an audio file
            abs_path = os.path.abspath(os.path.join(BANE_CORE_DIR, rel_path))
            if not abs_path.startswith(BANE_CORE_DIR) or not os.path.exists(abs_path):
                self.send_error(403, "Access denied or file not found")
                return
                
            if not abs_path.endswith(('.ogg', '.mp3', '.wav', '.m4a')):
                self.send_error(403, "Unsupported file type")
                return

            self.send_response(200)
            mime = 'audio/ogg' if abs_path.endswith('.ogg') else 'audio/mpeg'
            self.send_header('Content-type', mime)
            self.send_header('Cache-Control', 'max-age=3600')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:8081')
            self.end_headers()

            with open(abs_path, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def _json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8081')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def get_public_url(self):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "lt.log")
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    import re
                    match = re.search(r'https://[^\s]+', f.read())
                    if match:
                        return match.group(0)
        except:
            pass
        return None

    def get_bane_status(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Detect BANE processes - deduplicated by role
        seen_roles = {}
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                role = None
                if "main.py" in cmdline and "BANE" in cmdline:
                    role = "Core Engine"
                elif "telegram" in cmdline.lower() and "bot" in cmdline.lower():
                    role = "Telegram Bot"
                elif "monitor_server" in cmdline.lower():
                    role = "Monitor Server"
                elif "antigravity" in cmdline.lower() and "node" in proc.info['name'].lower():
                    role = "Antigravity (Node)"
                elif "antigravity" in cmdline.lower():
                    role = "Antigravity"
                elif "watcher" in cmdline.lower() and "bane" in cmdline.lower():
                    role = "Watcher"
                elif "error_watchdog.py" in cmdline.lower():
                    role = "Error Watchdog"
                
                if role:
                    if role not in seen_roles:
                        mem = proc.info.get('memory_info')
                        mem_mb = round(mem.rss / (1024*1024), 1) if mem else 0
                        seen_roles[role] = {
                            "name": role,
                            "status": "Running",
                            "pid": proc.info['pid'],
                            "memory_mb": mem_mb
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Add defaults for key services not detected
        for svc in ["Core Engine", "Antigravity", "Monitor Server", "Error Watchdog"]:
            if svc not in seen_roles:
                seen_roles[svc] = {"name": svc, "status": "Stopped", "pid": None, "memory_mb": 0}

        return {
            "system": {
                "cpu": cpu_usage,
                "memory": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "uptime": subprocess.getoutput("uptime -p"),
                "load_avg": os.getloadavg()
            },
            "network": {
                "local_ip": self.get_local_ip(),
                "public_url": self.get_public_url(),
                "port": PORT
            },
            "processes": list(seen_roles.values()),
            "timestamp": datetime.datetime.now().isoformat()
        }

    def get_latest_logs(self):
        log_dir = os.path.join(BANE_CORE_DIR, "Debug/Console")
        if not os.path.exists(log_dir):
            return {"error": "Log directory not found", "lines": []}
        
        # Get all log files, prefer those with real content
        files = [f for f in os.listdir(log_dir) if f.endswith('.txt') or f.endswith('.log')]
        if not files:
            return {"filename": "none", "lines": ["No logs available"]}
        
        # Sort by modification time, pick the most recent file with actual content
        files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
        
        for fname in files:
            fpath = os.path.join(log_dir, fname)
            try:
                size = os.path.getsize(fpath)
                if size > 5:  # Skip near-empty files
                    with open(fpath, 'r', errors='replace') as f:
                        lines = f.readlines()
                        if len(lines) > 1:
                            return {"filename": fname, "lines": [l.rstrip() for l in lines[-80:]]}
            except Exception:
                continue
        
        return {"filename": files[0], "lines": ["Log files exist but contain no data."]}

    def get_backups(self):
        # Search workspace dir AND the BANE core dir for .zip files
        backups = []
        for search_dir in [WORKSPACE_DIR, BANE_CORE_DIR]:
            if not os.path.exists(search_dir):
                continue
            for f in os.listdir(search_dir):
                if f.endswith('.zip'):
                    path = os.path.join(search_dir, f)
                    stats = os.stat(path)
                    size_mb = stats.st_size / (1024*1024)
                    size_str = f"{size_mb:.2f} MB" if size_mb < 1024 else f"{size_mb/1024:.2f} GB"
                    backups.append({
                        "name": f,
                        "size": size_str,
                        "size_bytes": stats.st_size,
                        "date": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        "path": search_dir
                    })
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups

    def get_workspaces(self):
        """List all workspace projects including the active core"""
        projects = []
        
        # 1. Add the Active Core first
        if os.path.exists(BANE_CORE_DIR):
            projects.append({
                "name": "BANE Core (Active)",
                "path": BANE_CORE_DIR,
                "file_count": sum(1 for _, _, files in os.walk(BANE_CORE_DIR) for _ in files if not _.startswith('.')),
                "last_modified": datetime.datetime.fromtimestamp(
                    os.path.getmtime(BANE_CORE_DIR)
                ).isoformat(),
                "is_core": True
            })

        # 2. Add other workspaces
        if os.path.exists(WORKSPACE_DIR):
            for item in os.listdir(WORKSPACE_DIR):
                full_path = os.path.join(WORKSPACE_DIR, item)
                if os.path.isdir(full_path) and not item.startswith('.') and full_path != BANE_CORE_DIR:
                    # Skip the redundant BANE folder in workspaces if it exists
                    if item == "BANE": continue 
                    
                    try:
                        file_count = sum(1 for _, _, files in os.walk(full_path) for _ in files)
                        projects.append({
                            "name": item,
                            "path": full_path,
                            "file_count": file_count,
                            "last_modified": datetime.datetime.fromtimestamp(
                                os.path.getmtime(full_path)
                            ).isoformat(),
                            "is_core": False
                        })
                    except Exception:
                        pass
        
        projects.sort(key=lambda x: x['last_modified'], reverse=True)
        return projects

    def get_stories(self):
        """Get all text files from Creative_Writing folder"""
        stories_dir = os.path.join(WORKSPACE_DIR, "Creative_Writing")
        stories = []
        if os.path.exists(stories_dir):
            for f in os.listdir(stories_dir):
                if f.endswith('.txt'):
                    try:
                        with open(os.path.join(stories_dir, f), 'r') as file:
                            content = file.read()
                        stories.append({
                            "title": f.replace('.txt', '').replace('_', ' '),
                            "filename": f,
                            "content": content
                        })
                    except Exception:
                        pass
        return stories

    def get_workspace_files(self):
        """List files in a specific workspace folder (passed via query param)"""
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        folder = params.get('folder', [''])[0]
        
        if not folder:
            return {"error": "Folder parameter required"}
            
        # Handle the special "Core (Active)" folder name
        if folder == "BANE Core (Active)":
            target_path = BANE_CORE_DIR
            safe_folder = "BANE Core (Active)"
        else:
            # Security: ensure we only look inside WORKSPACE_DIR
            safe_folder = os.path.basename(folder)
            target_path = os.path.join(WORKSPACE_DIR, safe_folder)
        
        files = []
        if os.path.exists(target_path) and os.path.isdir(target_path):
            # Limit to top-level files for performance and clarity
            for f in os.listdir(target_path):
                fpath = os.path.join(target_path, f)
                if os.path.isfile(fpath):
                    size = os.path.getsize(fpath)
                    files.append({
                        "name": f,
                        "size": size,
                        "date": datetime.datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                    })
        
        # Sort files by date descending
        files.sort(key=lambda x: x['date'], reverse=True)
        return {"folder": safe_folder, "files": files}

    def get_telegram_status(self):
        """Check if Telegram bot is running.
        
        The bot runs INSIDE main.py (Core Engine) — not as a separate process.
        Detection strategy:
        1. Check if BANE main.py is running (bot is embedded in it)
        2. Verify via Telegram Bot API getMe for definitive status
        """
        bot_running = False
        bot_pid = None
        
        # Strategy 1: The bot is embedded in main.py — if Core Engine is running, bot is running
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                if "main.py" in cmdline and "BANE" in cmdline:
                    bot_running = True
                    bot_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Strategy 2: Verify via Telegram Bot API (optional, cached)
        api_reachable = False
        bot_username = None
        try:
            import requests
            # Load token from secrets.env instead of hardcoding
            token = ""
            if os.path.exists(SECRETS_FILE):
                with open(SECRETS_FILE, 'r') as sf:
                    for sline in sf:
                        if sline.startswith("TELEGRAM_BOT_TOKEN="):
                            token = sline.split("=", 1)[1].strip().strip('"')
            resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    api_reachable = True
                    bot_username = data["result"].get("username", "unknown")
        except Exception:
            pass
        
        return {
            "running": bot_running,
            "pid": bot_pid,
            "api_reachable": api_reachable,
            "bot_username": bot_username,
            "config_exists": os.path.exists(os.path.join(BANE_CORE_DIR, "telegram_interface")),
            "note": "Bot runs embedded in Core Engine (main.py)"
        }


    def get_ai_skills(self):
        """List available AI skills"""
        skills_dir = "/home/user/BANE_CORE/antigravity/AI_SKILLS_DIR"
        skills = []
        if os.path.exists(skills_dir):
            for f in os.listdir(skills_dir):
                if f.endswith('.skill'):
                    fpath = os.path.join(skills_dir, f)
                    try:
                        with open(fpath, 'r') as sf:
                            content = sf.read().strip()
                    except Exception:
                        content = "Unable to read"
                    skills.append({
                        "name": f.replace('.skill', ''),
                        "file": f,
                        "preview": content[:120]
                    })
        return skills

    def get_skill_analytics(self):
        """Fetch AI Persona usage and performance metrics, including recent errors."""
        analytics_file = "/home/user/BANE_CORE/antigravity/skill_analytics.json"
        log_file = "/home/user/BANE_CORE/antigravity/persona_evolution.log"
        
        # 1. Fetch Skill-Specific Errors from Log
        skill_errors = {}
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                    # Iterate backwards to find recent errors
                    for line in reversed(log_lines):
                        # Stop if we hit a resolution marker
                        if "[SYSTEM] [INFO] -- MATCHED ERROR LOGS RESOLVED --" in line:
                            break
                            
                        if "[ERROR]" in line:
                            parts = line.split("] ", 3)
                            # Assume format: [Timestamp] [Skill ID] [Event Type] Context
                            if len(parts) >= 4:
                                skill_id = parts[1].strip("[")
                                context = parts[3].strip()
                                
                                if skill_id not in skill_errors:
                                    skill_errors[skill_id] = []
                                
                                # Add unique errors up to a limit
                                if context not in skill_errors[skill_id] and len(skill_errors[skill_id]) < 5:
                                    skill_errors[skill_id].append(context)
            except Exception:
                pass

        if os.path.exists(analytics_file):
            try:
                with open(analytics_file, 'r') as f:
                    data = json.load(f)
                
                results = []
                for skill_id, stats in data.items():
                    score = stats["usage"] / (stats["errors"] + 1)
                    results.append({
                        "id": skill_id,
                        "score": round(score, 2),
                        "recent_errors": skill_errors.get(skill_id, []),
                        **stats
                    })
                
                results.sort(key=lambda x: x["score"], reverse=True)
                return results
            except Exception as e:
                return {"error": str(e)}
        return {"error": "Analytics data not found"}

    def get_maintenance_issues(self):
        """Fetch ongoing issues for Core Maintenance skill from the evolution log."""
        log_file = "/home/user/BANE_CORE/antigravity/persona_evolution.log"
        issues = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                # Find the last RESOLVED marker index
                resolved_idx = -1
                for i in range(len(lines) - 1, -1, -1):
                    if "[SYSTEM] [INFO] -- MATCHED ERROR LOGS RESOLVED --" in lines[i]:
                        resolved_idx = i
                        break
                
                # Filter for CORE_MAINTENANCE errors, ignoring those before resolution
                start_check = max(0, len(lines) - 100, resolved_idx + 1)
                for line in lines[start_check:]:
                    if "[CORE_MAINTENANCE] [ERROR]" in line or ("[ERROR]" in line and "CORE_MAINTENANCE" in line):
                        # Parse timestamp and context
                        parts = line.split("] ", 3)
                        if len(parts) >= 4:
                            timestamp = parts[0].strip("[")
                            context = parts[3].strip()
                            issues.append({
                                "timestamp": timestamp,
                                "issue": context,
                                "status": "Pending"
                            })
                        else:
                            issues.append({"timestamp": "Unknown", "issue": line.strip(), "status": "Pending"})

                # If no errors found recently, return default status
                if not issues:
                    return {"status": "Clean", "message": "No recent core maintenance errors detected.", "issues": []}
                
                return {"status": "Action Required", "issues": issues}
            except Exception as e:
                return {"error": str(e)}
        return {"status": "No Log", "message": "Evolution log not found.", "issues": []}

    def fix_skill_errors(self, skill_id):
        """Mark recent errors as fixed (increment fixed count)."""
        analytics_file = "/home/user/BANE_CORE/antigravity/skill_analytics.json"
        if os.path.exists(analytics_file):
            try:
                with open(analytics_file, 'r') as f:
                    data = json.load(f)
                
                if skill_id in data:
                    if "fixed_errors" not in data[skill_id]:
                        data[skill_id]["fixed_errors"] = 0
                    
                    # Logic: Increment fixed count. 
                    # We assume 1 fix action resolves 1 'unit' of trouble, or maybe clears recent errors?
                    # For now, just increment.
                    data[skill_id]["fixed_errors"] += 1
                    
                    with open(analytics_file, 'w') as f:
                        json.dump(data, f, indent=4)
                    
                    return {"success": True, "fixed_count": data[skill_id]["fixed_errors"]}
                else:
                    return {"error": "Skill ID not found"}
            except Exception as e:
                return {"error": str(e)}
        return {"error": "Analytics file not found"}

    def get_quota_status(self):
        """Returns detected quota information for all models with persistent caching."""
        if not extract_quota_details:
            return {"error": "Quota detector not loaded"}
        
        STATE_FILE = os.path.join(BANE_CORE_DIR, "storage/quota_state.json")
        try:
            # 1. Load existing state
            state = {"limited_models": {}, "timestamp": 0}
            if os.path.exists(STATE_FILE):
                try:
                    with open(STATE_FILE, 'r') as f:
                        state = json.load(f)
                except: pass

            # 2. Run fresh detection (visual)
            quota_data = extract_quota_details()
            q_info = detect_quota_local()
            
            # 3. Update state with new findings
            current_time = time.time()
            newly_detected = {m['name']: True for m in quota_data.get('models', []) if m['is_limited']}
            
            for mname in newly_detected:
                state["limited_models"][mname] = current_time
            
            # Optional: Remove limits that haven't been seen for 6 hours? 
            # Or keep them until manually cleared because accuracy is more important.
            # For now, let's keep them persistent for the session.

            # 4. Get latest model list
            from antigravity.model_selector import ALL_MODELS
            
            models = []
            for mname in ALL_MODELS:
                is_limited = mname in state["limited_models"]
                status = "Limit Exceeded" if is_limited else "Available"
                
                models.append({
                    "name": mname,
                    "status": status,
                    "limited": is_limited,
                    "last_seen_limited": state["limited_models"].get(mname)
                })

            # Save state
            state["timestamp"] = current_time
            try:
                os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
                with open(STATE_FILE, 'w') as f:
                    json.dump(state, f)
            except: pass

            return {
                "models": models,
                "notes": q_info.get("notes", ""),
                "tokens": get_token_metrics() if get_token_metrics else {},
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_network_status(self):
        """Comprehensive network status: speed, WiFi, interfaces, connectivity."""
        result = {
            "interfaces": [],
            "speed": {"download_kbps": 0, "upload_kbps": 0},
            "wifi": None,
            "internet": {"connected": False, "latency_ms": None, "dns_ok": False},
            "active_connections": 0
        }

        # ── 1. Network Interfaces ──
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            counters = psutil.net_io_counters(pernic=True)

            for iface_name in addrs:
                if iface_name == 'lo':
                    continue
                iface_info = {
                    "name": iface_name,
                    "is_up": False,
                    "speed_mbps": 0,
                    "mtu": 0,
                    "ipv4": None,
                    "ipv6": None,
                    "type": "ethernet",
                    "bytes_sent_mb": 0,
                    "bytes_recv_mb": 0
                }

                # Stats
                if iface_name in stats:
                    s = stats[iface_name]
                    iface_info["is_up"] = s.isup
                    iface_info["speed_mbps"] = s.speed
                    iface_info["mtu"] = s.mtu

                # Addresses
                for addr in addrs[iface_name]:
                    if addr.family == socket.AF_INET:
                        iface_info["ipv4"] = addr.address
                    elif addr.family == socket.AF_INET6 and not addr.address.startswith('fe80'):
                        iface_info["ipv6"] = addr.address

                # Traffic counters
                if iface_name in counters:
                    c = counters[iface_name]
                    iface_info["bytes_sent_mb"] = round(c.bytes_sent / (1024 * 1024), 1)
                    iface_info["bytes_recv_mb"] = round(c.bytes_recv / (1024 * 1024), 1)

                # Detect WiFi interface
                if iface_name.startswith('wl') or iface_name.startswith('wifi'):
                    iface_info["type"] = "wifi"
                elif iface_name.startswith('en') or iface_name.startswith('eth'):
                    iface_info["type"] = "ethernet"

                result["interfaces"].append(iface_info)
        except Exception as e:
            print(f"Interface detection error: {e}")

        # ── 2. Real-time Speed (1-second delta) ──
        try:
            c1 = psutil.net_io_counters()
            time.sleep(1)
            c2 = psutil.net_io_counters()
            dl = (c2.bytes_recv - c1.bytes_recv) * 8 / 1024  # kbps
            ul = (c2.bytes_sent - c1.bytes_sent) * 8 / 1024  # kbps
            result["speed"]["download_kbps"] = round(dl, 1)
            result["speed"]["upload_kbps"] = round(ul, 1)
        except Exception:
            pass

        # ── 3. WiFi Details (via iwconfig) ──
        try:
            iw = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=5)
            output = iw.stdout + iw.stderr
            wifi = {}
            for line in output.split('\n'):
                if 'ESSID:' in line:
                    essid = line.split('ESSID:')[1].strip().strip('"')
                    wifi['ssid'] = essid
                if 'Bit Rate=' in line:
                    rate = line.split('Bit Rate=')[1].split()[0]
                    wifi['bitrate'] = rate + ' Mb/s'
                if 'Signal level=' in line:
                    sig = line.split('Signal level=')[1].split()[0]
                    wifi['signal_dbm'] = sig + ' dBm'
                if 'Link Quality=' in line:
                    qual = line.split('Link Quality=')[1].split()[0]
                    wifi['link_quality'] = qual
                if 'Frequency:' in line:
                    freq = line.split('Frequency:')[1].split()[0]
                    wifi['frequency'] = freq + ' GHz'
                    # Determine band
                    try:
                        f_val = float(freq)
                        wifi['band'] = '5 GHz' if f_val > 4.0 else '2.4 GHz'
                    except:
                        wifi['band'] = 'Unknown'
            if wifi:
                result['wifi'] = wifi
        except Exception:
            pass

        # ── 4. Internet Connectivity Check ──
        try:
            ping = subprocess.run(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )
            if ping.returncode == 0:
                result['internet']['connected'] = True
                for line in ping.stdout.split('\n'):
                    if 'time=' in line:
                        t = line.split('time=')[1].split()[0]
                        result['internet']['latency_ms'] = float(t)
        except Exception:
            pass

        # DNS Check
        try:
            socket.setdefaulttimeout(3)
            socket.getaddrinfo('google.com', 80)
            result['internet']['dns_ok'] = True
        except Exception:
            pass

        # ── 5. Active Connections Count ──
        try:
            conns = psutil.net_connections(kind='inet')
            result['active_connections'] = len([c for c in conns if c.status == 'ESTABLISHED'])
        except Exception:
            pass

        return result

    def get_security_status(self):
        """Run or fetch the latest security audit report."""
        audit_script = "/home/user/BANE_CORE_Workspaces/Cybersecurity/security_audit.py"
        report_file = "/home/user/BANE_CORE_Workspaces/Cybersecurity/security_report.json"
        
        # Check if audit script exists
        if not os.path.exists(audit_script):
            return {"error": "Audit script not found", "status": "Not Configured"}

        # Force a run if report is old (older than 10 minutes) or doesn't exist
        should_run = True
        if os.path.exists(report_file):
            mtime = os.path.getmtime(report_file)
            if (time.time() - mtime) < 600:
                should_run = False
        
        if should_run:
            try:
                # Run audit script asynchronously to not block the server too much
                # But here we wait shortly or just return the old reporting while starting a new one
                subprocess.Popen(["python3", audit_script], 
                               cwd="/home/user/BANE_CORE_Workspaces/Cybersecurity",
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                # If we just started it, the old report (if any) is still there
            except Exception as e:
                print(f"Audit execution error: {e}")

        # Return the report data
        if os.path.exists(report_file):
            try:
                with open(report_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                return {"error": f"Failed to read report: {str(e)}", "status": "Error"}
        
        return {"status": "Scanning...", "message": "Security audit in progress"}

if __name__ == "__main__":
    # Log rotation: truncate monitor.log if > 1MB
    LOG_FILE = "monitor.log"
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 1024 * 1024:
        print("📄 Log too large, rotating...")
        with open(LOG_FILE, 'w') as f:
            f.write(f"--- Log rotated at {datetime.datetime.now()} ---\n")

    # Multi-threaded server for handling concurrent resilience tests and dashboard users
    with ThreadedTCPServer(("", PORT), MonitorHandler) as httpd:
        httpd.timeout = 5 # Set 5-second socket timeout for security
        print(f"⚡ BANE Hardened Multi-threaded Monitor Server active on port {PORT}")
        httpd.serve_forever()
