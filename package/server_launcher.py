"""
PersonalDrive — Server Launcher

Reads all paths from packageconfig.json, sets up the virtual environment
if needed, starts the Flask/Waitress server, configures and launches
ngrok for public tunneling, and displays everything in a clean GUI.
"""
import os
import sys
import json
import time
import threading
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from pckconfig import (
        config, APP_DISPLAY_NAME, APP_NAME,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS, CENTRAL_SERVER_URL
    )
    from packages import packages
    from GUIconfig import ServerConfigApp
except ImportError:
    from package.pckconfig import (
        config, APP_DISPLAY_NAME, APP_NAME,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS, CENTRAL_SERVER_URL
    )
    from package.packages import packages
    from package.GUIconfig import ServerConfigApp


class ServerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_DISPLAY_NAME} — Server")
        self.root.geometry("600x520")
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.style = ttk.Style()
        self.style.theme_use('vista' if 'vista' in self.style.theme_names() else 'clam')

        # Process handles
        self.server_process = None
        self.ngrok_process = None
        self.is_running = False
        self.log_thread_active = False

        # Load config
        self.workspace = config.get("dir", "")
        self.python_path = config.get("python", "")
        self.ngrok_path = config.get("ngrok", "")
        self.ngrok_token = config.get("ngrok_token", "")
        self.host = config.get("host", DEFAULT_HOST)
        self.port = config.get("port", DEFAULT_PORT)
        self.threads = config.get("threads", DEFAULT_THREADS)

        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    # ── GUI Layout ─────────────────────────────────────────
    def create_widgets(self):
        main = ttk.Frame(self.root, padding="15")
        main.pack(fill=tk.BOTH, expand=True)

        # ── Header ──
        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            header,
            text=f"⚡ {APP_DISPLAY_NAME} Server",
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)

        # ── Status Section ──
        status_frame = ttk.LabelFrame(main, text=" Server Status ", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(status_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Status:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Stopped")
        self.status_lbl = ttk.Label(
            row1, textvariable=self.status_var,
            font=("Segoe UI", 10), foreground="gray"
        )
        self.status_lbl.pack(side=tk.LEFT, padx=(8, 0))

        row2 = ttk.Frame(status_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Local:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.local_var = tk.StringVar(value="—")
        ttk.Label(row2, textvariable=self.local_var,
                  font=("Segoe UI", 9), foreground="#555").pack(side=tk.LEFT, padx=(8, 0))

        row3 = ttk.Frame(status_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Workspace:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ws_display = self.workspace if self.workspace else "Not configured"
        ttk.Label(row3, text=ws_display,
                  font=("Segoe UI", 9), foreground="#555").pack(side=tk.LEFT, padx=(8, 0))

        # ── Public Access Section ──
        url_frame = ttk.LabelFrame(main, text=" Public Access (Ngrok) ", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        url_row = ttk.Frame(url_frame)
        url_row.pack(fill=tk.X)

        self.url_var = tk.StringVar(value="Not connected")
        self.url_entry = ttk.Entry(
            url_row, textvariable=self.url_var,
            state="readonly", width=50,
            font=("Consolas", 10)
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.copy_btn = ttk.Button(url_row, text="Copy URL", command=self.copy_url, state="disabled")
        self.copy_btn.pack(side=tk.RIGHT)

        # ── Log Section ──
        log_frame = ttk.LabelFrame(main, text=" Server Log ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=10,
            state="disabled",
            background="#1e1e1e",
            foreground="#d4d4d4",
            insertbackground="#d4d4d4",
            selectbackground="#264f78",
            borderwidth=0,
            highlightthickness=0,
            padx=8, pady=6
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Tag configs for colored log output
        self.log_text.tag_config("info", foreground="#d4d4d4")
        self.log_text.tag_config("success", foreground="#4ec9b0")
        self.log_text.tag_config("warning", foreground="#dcdcaa")
        self.log_text.tag_config("error", foreground="#f44747")
        self.log_text.tag_config("url", foreground="#569cd6", underline=True)

        # ── Button Bar ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(
            btn_frame, text="▶  Start Server",
            command=self.start_all
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(
            btn_frame, text="■  Stop Server",
            command=self.stop_all, state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT)

        self.config_btn = ttk.Button(
            btn_frame, text="⚙  Configure",
            command=self.open_config_gui
        )
        self.config_btn.pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(
            btn_frame, text="Exit",
            command=self.on_close
        ).pack(side=tk.RIGHT)

    # ── Logging ────────────────────────────────────────────
    def log(self, message, tag="info"):
        """Thread-safe log to the GUI text widget."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, line, tag)
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")

        self.root.after(0, _append)

    # ── Status Updates ─────────────────────────────────────
    def set_status(self, text, color):
        def _update():
            self.status_var.set(text)
            self.status_lbl.config(foreground=color)
        self.root.after(0, _update)

    def set_url(self, url):
        def _update():
            self.url_var.set(url)
            self.copy_btn.config(state="normal")
        self.root.after(0, _update)

    def copy_url(self):
        url = self.url_var.get()
        if url and url != "Not connected":
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.log("URL copied to clipboard!", "success")

    # ── Virtual Environment Setup ──────────────────────────
    def _ensure_venv(self):
        """Create virtual environment and install dependencies if needed."""
        venv_python = os.path.join(self.workspace, "env", "Scripts", "python.exe")

        if os.path.exists(venv_python):
            self.log("Virtual environment found.", "success")
            return venv_python

        self.log("Creating virtual environment...", "warning")

        # Use the configured system python to create venv
        python = self.python_path
        if not python or not os.path.exists(python):
            self.log("ERROR: Python path not configured. Run Setup first.", "error")
            return None

        try:
            subprocess.run(
                [python, "-m", "venv", os.path.join(self.workspace, "env")],
                check=True, capture_output=True, text=True
            )
            self.log("Virtual environment created.", "success")
        except subprocess.CalledProcessError as e:
            self.log(f"ERROR: Failed to create venv: {e}", "error")
            return None

        # Ensure pip is available
        self.log("Upgrading pip...", "info")
        try:
            subprocess.run(
                [venv_python, "-m", "ensurepip", "--upgrade"],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError:
            self.log("WARNING: ensurepip failed, continuing anyway.", "warning")

        # Install server dependencies
        self.log("Installing server dependencies (this may take a minute)...", "info")
        req_file = os.path.join(self.workspace, "requirements.txt")
        try:
            if os.path.exists(req_file):
                subprocess.run(
                    [venv_python, "-m", "pip", "install", "-r", req_file],
                    check=True, capture_output=True, text=True,
                    cwd=self.workspace
                )
            else:
                subprocess.run(
                    [venv_python, "-m", "pip", "install", *packages],
                    check=True, capture_output=True, text=True,
                    cwd=self.workspace
                )
            self.log("Dependencies installed successfully.", "success")
        except subprocess.CalledProcessError as e:
            self.log(f"ERROR: Failed to install dependencies: {e}", "error")
            return None

        return venv_python

    # ── Ngrok URL Discovery ────────────────────────────────
    def _get_ngrok_url(self, retries=10, delay=2):
        """Poll ngrok's local API to get the public tunnel URL."""
        api_url = "http://localhost:4040/api/tunnels"
        for attempt in range(retries):
            try:
                req = urllib.request.Request(api_url)
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode())
                    tunnels = data.get("tunnels", [])
                    for tunnel in tunnels:
                        public_url = tunnel.get("public_url", "")
                        if public_url.startswith("https://"):
                            return public_url
                    # If no https, return any URL
                    if tunnels:
                        return tunnels[0].get("public_url", "")
            except Exception:
                pass
            time.sleep(delay)
        return None

    # ── Start Sequence ─────────────────────────────────────
    def start_all(self):
        """Launch the full start sequence in a background thread."""
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self._start_sequence, daemon=True).start()

    def _start_sequence(self):
        self.log(f"Starting {APP_DISPLAY_NAME} server...", "info")

        # ── Validate Config ──
        if not self.workspace or not os.path.isdir(self.workspace):
            self.log("ERROR: Workspace directory not found.", "error")
            self.log(f"  Path: {self.workspace}", "error")
            self.log("Run PersonalDriveSetup.exe first to configure.", "error")
            self.set_status("Configuration Error", "#f44747")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        app_py = os.path.join(self.workspace, "app.py")
        if not os.path.exists(app_py):
            self.log(f"ERROR: app.py not found in workspace.", "error")
            self.log(f"  Expected: {app_py}", "error")
            self.set_status("Configuration Error", "#f44747")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # ── Step 1: Setup Virtual Environment ──
        self.set_status("Setting up environment...", "#dcdcaa")
        venv_python = self._ensure_venv()
        if not venv_python:
            self.set_status("Setup Failed", "#f44747")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # ── Step 2: Start Waitress Server ──
        self.set_status("Starting server...", "#dcdcaa")
        bind_host = config.get("bind_host")
        local_host = config.get("local_host")
        register_host = local_host if self.host == bind_host else self.host
        local_url = f"http://{register_host}:{self.port}"
        self.root.after(0, lambda: self.local_var.set(local_url))
        self.log(f"Starting Waitress on {self.host}:{self.port}...", "info")

        # Copy current environment and explicitly inject configured api_key as 'accesstooken'
        env_vars = os.environ.copy()
        env_vars["PYTHONUNBUFFERED"] = "1"
        api_key = config.get("api_key", "")
        if api_key:
            env_vars["accesstooken"] = api_key

        try:
            self.server_process = subprocess.Popen(
                [venv_python, "-m", "waitress",
                 f"--host={self.host}",
                 f"--port={self.port}",
                 f"--threads={self.threads}",
                 "app:app"],
                cwd=self.workspace,
                env=env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        except FileNotFoundError:
            self.log("ERROR: Could not start server — venv python not found.", "error")
            self.set_status("Start Failed", "#f44747")
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        # Give the server a moment to start (or fail)
        time.sleep(3)
        if self.server_process.poll() is not None:
            # Process already exited — read output for error
            out = self.server_process.stdout.read() if self.server_process.stdout else ""
            self.log(f"ERROR: Server exited immediately.", "error")
            if out:
                for line in out.strip().split("\n"):
                    self.log(f"  {line}", "error")
            self.set_status("Server Crashed", "#f44747")
            self.server_process = None
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            return

        self.log("Server started successfully!", "success")
        self.is_running = True

        # Start log streaming thread
        self.log_thread_active = True
        threading.Thread(target=self._stream_server_logs, daemon=True).start()

        # ── Step 3: Configure Ngrok Auth ──
        if self.ngrok_path and os.path.exists(self.ngrok_path) and self.ngrok_token:
            self.set_status("Connecting ngrok...", "#dcdcaa")
            self.log("Configuring ngrok authtoken...", "info")

            try:
                subprocess.run(
                    [self.ngrok_path, "config", "add-authtoken", self.ngrok_token],
                    capture_output=True, text=True, check=True
                )
                self.log("Ngrok authtoken configured.", "success")
            except subprocess.CalledProcessError as e:
                self.log(f"WARNING: ngrok auth config failed: {e}", "warning")

            # ── Step 4: Start Ngrok Tunnel ──
            self.log(f"Starting ngrok tunnel → port {self.port}...", "info")
            try:
                self.ngrok_process = subprocess.Popen(
                    [self.ngrok_path, "http", f"{register_host}:{self.port}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
            except FileNotFoundError:
                self.log("WARNING: ngrok executable not found.", "warning")
                self.ngrok_process = None

            # ── Step 5: Retrieve Public URL ──
            if self.ngrok_process:
                self.log("Waiting for ngrok to establish tunnel...", "info")
                public_url = self._get_ngrok_url()
                if public_url:
                    self.set_url(public_url)
                    self.log(f"Public URL: {public_url}", "success")
                else:
                    self.log("WARNING: Could not retrieve ngrok public URL.", "warning")
                    self.log("  Check http://localhost:4040 manually.", "warning")
        else:
            if not self.ngrok_path or not os.path.exists(self.ngrok_path):
                self.log("Ngrok not configured — skipping tunnel.", "warning")
            elif not self.ngrok_token:
                self.log("Ngrok authtoken not set — skipping tunnel.", "warning")

        # Fallback check: See if an active ngrok tunnel is already running (e.g. started by app.py)
        if self.url_var.get() == "Not connected":
            public_url = self._get_ngrok_url(retries=3, delay=1)
            if public_url:
                self.set_url(public_url)
                self.log(f"Detected active ngrok tunnel: {public_url}", "success")

        # ── Done ──
        self.set_status("● Running", "#4ec9b0")
        self.log("─" * 45, "info")
        self.log(f"{APP_DISPLAY_NAME} is ready!", "success")
        self.log(f"  Local:  {local_url}", "info")
        if self.url_var.get() != "Not connected":
            self.log(f"  Public: {self.url_var.get()}", "info")
        self.log("─" * 45, "info")

        # ── Notify Central Server ──
        final_url = self.url_var.get()
        if final_url == "Not connected":
            final_url = local_url
        self.notify_central_server(final_url)

    # ── Log Streaming ──────────────────────────────────────
    def _stream_server_logs(self):
        """Read server stdout line-by-line and display in log."""
        try:
            while self.log_thread_active and self.server_process:
                line = self.server_process.stdout.readline()
                if not line:
                    if self.server_process.poll() is not None:
                        break
                    continue
                stripped = line.strip()
                if stripped:
                    self.log(f"[server] {stripped}", "info")
        except Exception:
            pass

    # ── Stop Sequence ──────────────────────────────────────
    def stop_all(self):
        """Stop server and ngrok processes."""
        self.log("Stopping server...", "warning")
        self.log_thread_active = False
        self.is_running = False

        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                self.log("Ngrok tunnel closed.", "info")
            except Exception:
                self.ngrok_process.kill()
            self.ngrok_process = None

        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.log("Server stopped.", "info")
            except Exception:
                self.server_process.kill()
            self.server_process = None

        self.set_status("Stopped", "gray")
        self.url_var.set("Not connected")
        self.local_var.set("—")
        self.copy_btn.config(state="disabled")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("All processes terminated.", "success")

    def notify_central_server(self, server_url):
        """Send an HTTP GET request to the Central Server with our URL and API Key."""
        api_key = config.get("api_key", "")
        access_code = config.get("access_code", "")
        opt_password = config.get("opt_password", "")
        # If CENTRAL_SERVER_URL is not set or placeholder, skip
        if not CENTRAL_SERVER_URL or "example.com" in CENTRAL_SERVER_URL:
            self.log("Skipping Central Server notification: CENTRAL_SERVER_URL is a placeholder.", "info")
            return

        def task():
            import urllib.parse
            self.log(f"Notifying Central Server ({CENTRAL_SERVER_URL})...", "info")
            base_url = CENTRAL_SERVER_URL.rstrip('/')
            payload = json.dumps({
                "api": api_key,
                "link": server_url,
                "users": config.get("allowusers", False)
            }).encode('utf-8')
            try:
                req = urllib.request.Request(
                    f"{base_url}/register/api/",
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'PersonalDrive-Server/1.0'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    status = resp.status
                    body = resp.read().decode('utf-8')
                    self.log(f"Central Server notified successfully (Status {status}).", "success")
            except Exception as e:
                self.log(f"Failed to notify Central Server: {e}", "warning")

            if access_code:
                self.log("Registering Frontend Access Code...", "info")
                try:
                    payload = json.dumps({
                        "api": api_key,
                        "code": access_code,
                        "userpassword": opt_password if opt_password else None
                    }).encode('utf-8')
                    
                    req_user = urllib.request.Request(
                        f"{base_url}/register/user/",
                        data=payload,
                        headers={
                            'Content-Type': 'application/json',
                            'User-Agent': 'PersonalDrive-Server/1.0'
                        },
                        method='POST'
                    )
                    with urllib.request.urlopen(req_user, timeout=8) as resp:
                        self.log("Frontend access code registered successfully.", "success")
                except Exception as e:
                    self.log(f"Failed to register access code: {e}", "warning")

        # Run in a background thread so we don't freeze the GUI
        threading.Thread(target=task, daemon=True).start()

    def open_config_gui(self):
        """Open the Server Configuration GUI in a new window."""
        config_win = tk.Toplevel(self.root)
        
        def on_complete(combined_config):
            config_win.destroy()
            config.reload()
            self.workspace = config.get("dir", "")
            self.python_path = config.get("python", "")
            self.ngrok_path = config.get("ngrok", "")
            self.ngrok_token = config.get("ngrok_token", "")
            self.host = config.get("host", DEFAULT_HOST)
            self.port = config.get("port", DEFAULT_PORT)
            self.threads = config.get("threads", DEFAULT_THREADS)
            self.log("Server settings reloaded.", "success")
            
        ServerConfigApp(config_win, on_complete=on_complete, on_cancel=config_win.destroy)

    # ── Window Close ───────────────────────────────────────
    def on_close(self):
        if self.is_running:
            confirm = messagebox.askyesno(
                "Stop Server?",
                f"The {APP_DISPLAY_NAME} server is still running.\n\n"
                "Stop the server and exit?",
                parent=self.root
            )
            if not confirm:
                return
            self.stop_all()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerLauncher(root)
    root.mainloop()
