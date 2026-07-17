import json
import os
import sys
import re
import shutil

# ──────────────────────────────────────────────
# BRANDING CONSTANTS — Single Source of Truth
# ──────────────────────────────────────────────
APP_NAME            = "PersonalDrive"
APP_DISPLAY_NAME    = "Personal Drive"
APP_DESCRIPTION     = "Self-hosted personal cloud storage server"

# Window Titles (used in root.title())
SETUP_TITLE         = f"{APP_DISPLAY_NAME} Setup"
SETUP_STEP1_TITLE   = f"{SETUP_TITLE} — Step 1: Workspace"
SETUP_STEP2_TITLE   = f"{SETUP_TITLE} — Step 2: Cloud Tunnel Setup"
SETUP_STEP3_TITLE   = f"{SETUP_TITLE} — Step 3: Code Server"
CONFIG_TITLE        = f"{APP_DISPLAY_NAME} — Server Configuration"
HELP_TITLE          = "Cloud Tunnel Help"
CONFIG_HELP_TITLE   = "Configuration Guide"

# Section Labels (used inside LabelFrames)
LBL_WORKSPACE       = " Select Workspace "
LBL_INSTALL_OPTIONS  = " Installation Options "
LBL_NGROK_AUTH       = " Configure Cloud Tunnel "
LBL_CODE_SERVER      = " Code Server Setup "
LBL_DIRECTORIES      = " Storage Directories "
LBL_LIMITS           = " Storage & Bandwidth Limits "
LBL_SECURITY         = " Security & Authentication "
LBL_RATE_LIMITER     = " Rate Limiting Settings "
LBL_NETWORK          = " Connections & Network URLs "

# GitHub Source & URLs (Loaded from local urls.py inside package directory)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

try:
    import urls
except ImportError:
    try:
        from package import urls
    except ImportError:
        urls = None

HELP_WEBSITE_URL     = urls.HELP_WEBSITE_URL if urls else "https://example.com/help"
CENTRAL_SERVER_URL   = urls.CENTRAL_SERVER_URL if urls else "https://example.com/api"
DEFAULT_FRONTEND_URL = urls.DEFAULT_FRONTEND_URL if urls else "http://localhost:5174"
DEFAULT_CORS_ORIGIN  = urls.DEFAULT_CORS_ORIGIN if urls else "*"
NGROK_SIGNUP_URL     = urls.NGROK_SIGNUP_URL if urls else "https://ngrok.com"
NGROK_DASHBOARD_URL  = urls.NGROK_DASHBOARD_URL if urls else "https://dashboard.ngrok.com"

GITHUB_OWNER         = urls.GITHUB_OWNER if urls else "Naseer-fez"
GITHUB_REPO          = urls.GITHUB_REPO if urls else "PersonalDrive"
GITHUB_BRANCH        = urls.GITHUB_BRANCH if urls else "main"
GITHUB_ZIP_URL       = urls.GITHUB_ZIP_URL if urls else f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
GITHUB_EXTRACTED_DIR = f"{GITHUB_REPO}-{GITHUB_BRANCH}"

# File Names
PACKAGE_CONFIG_FILE  = "packageconfig.json"
SERVER_CONFIG_FILE   = "config.json"
CODE_CONFIG_SCRIPT   = "config.py"

# Dependency Names
PYTHON_EXE           = "python.exe"
CLOUDFLARED_EXE      = "cloudflared.exe"
NGROK_EXE            = "ngrok.exe"

# Default Values (used when no prior config exists)
DEFAULT_BANDWIDTH    = 100
DEFAULT_USER_SPACE   = 10
DEFAULT_JWT_MINUTES  = 30
DEFAULT_FREQUENCY    = 50
DEFAULT_RESET_SEC    = 60
DEFAULT_COOLDOWN_SEC = 30
DEFAULT_ALLOW_USERS  = False
DEFAULT_LOGIN        = DEFAULT_ALLOW_USERS  # Alias for backward compatibility
DEFAULT_RATE_LIMITER = False
DEFAULT_HOST         = "0.0.0.0"
DEFAULT_PORT         = 5000
DEFAULT_THREADS      = 4


# ──────────────────────────────────────────────
# Resolve config directory (supports PyInstaller & AppData)
# ──────────────────────────────────────────────
_APPDATA_DIR = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
_CONFIG_DIR = os.path.join(_APPDATA_DIR, "PersonalDrive")
try:
    os.makedirs(_CONFIG_DIR, exist_ok=True)
except Exception:
    pass

_CONFIG_PATH = os.path.join(_CONFIG_DIR, PACKAGE_CONFIG_FILE)

# For migration from older setup/codebase paths
if getattr(sys, 'frozen', False):
    _OLD_CONFIG_DIR = os.path.dirname(sys.executable)
else:
    _OLD_CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OLD_CONFIG_PATH = os.path.join(_OLD_CONFIG_DIR, PACKAGE_CONFIG_FILE)

# Default configuration template (created on first run if missing)
_DEFAULT_CONFIG = {
    "dir": "",
    "workspace_path": "",
    "python": "",
    "cloudflared": "",
    "ngrok": "",
    "ngrok_token": "",
    "config_path": "",
    "DestinationFolder": "",
    "Userfolder": "",
    "trash": "trash",
    "stats": "stats.json",
    "file": "files.json",
    "trashfile": "trash.json",
    "size": DEFAULT_BANDWIDTH,
    "basic": DEFAULT_USER_SPACE,
    "backend": "",
    "allowusers": DEFAULT_ALLOW_USERS,
    "api_key": "",
    "jwtduration": DEFAULT_JWT_MINUTES,
    "ratelimiter": "",
    "FrontendURL": DEFAULT_CORS_ORIGIN,
    "URL": DEFAULT_FRONTEND_URL,
    "Ratelimiter": DEFAULT_RATE_LIMITER,
    "Allowfreq": DEFAULT_FREQUENCY,
    "resettime": DEFAULT_RESET_SEC,
    "cooldowntime": DEFAULT_COOLDOWN_SEC,
    "host": DEFAULT_HOST,
    "port": DEFAULT_PORT,
    "threads": DEFAULT_THREADS,
    "initial_username": "",
    "initial_email": "",
    "initial_password": "",
    "bind_host": "0.0.0.0",
    "local_host": "127.0.0.1"
}


# ──────────────────────────────────────────────
# Package Config Helper
# ──────────────────────────────────────────────
class Config:
    def __init__(self):
        # Migrate old config if AppData config missing but old config exists
        if not os.path.exists(_CONFIG_PATH) and os.path.exists(_OLD_CONFIG_PATH) and _OLD_CONFIG_PATH != _CONFIG_PATH:
            try:
                shutil.copy2(_OLD_CONFIG_PATH, _CONFIG_PATH)
            except Exception:
                pass

        # Auto-create config file with defaults if it doesn't exist
        if not os.path.exists(_CONFIG_PATH):
            try:
                with open(_CONFIG_PATH, "w", encoding="utf-8") as file:
                    json.dump(_DEFAULT_CONFIG, file, indent=4)
            except Exception:
                pass
        self.reload()

    def reload(self):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except Exception:
            self.data = dict(_DEFAULT_CONFIG)
            try:
                with open(_CONFIG_PATH, "w", encoding="utf-8") as file:
                    json.dump(self.data, file, indent=4)
            except Exception:
                pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        try:
            with open(_CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)
        except Exception as e:
            print(f"Warning: Failed to save to {_CONFIG_PATH}: {e}", file=sys.stderr)
        self.sync_to_server_config()

    def sync_to_server_config(self):
        """Bidirectionally sync between AppData packageconfig.json and <dir>/config.json"""
        target_dir = self.get("dir", "")
        if not target_dir or not isinstance(target_dir, str):
            return False
        target_dir = target_dir.strip()
        if not target_dir or not os.path.exists(target_dir):
            return False

        server_config_path = os.path.normpath(os.path.join(target_dir, SERVER_CONFIG_FILE))
        
        server_data = dict(_DEFAULT_CONFIG)
        if os.path.exists(server_config_path):
            try:
                with open(server_config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        server_data.update(loaded)
            except Exception:
                pass

        # Package keys to always push from packageconfig into server config
        package_keys = ["dir", "python", "cloudflared", "ngrok", "ngrok_token", "config_path"]
        for k in package_keys:
            val = self.get(k)
            if val is not None and val != "":
                server_data[k] = val

        server_data["config_path"] = server_config_path

        # Ensure critical storage folders are never empty strings to avoid falling back to root
        if not server_data.get("DestinationFolder"):
            server_data["DestinationFolder"] = os.path.normpath(os.path.join(target_dir, "test"))
        if not server_data.get("Userfolder"):
            server_data["Userfolder"] = os.path.normpath(os.path.join(target_dir, "userdetails"))
        if not server_data.get("ratelimiter"):
            server_data["ratelimiter"] = os.path.normpath(os.path.join(target_dir, "data"))

        # Mirror server GUI keys back to packageconfig so both are 100% exact mirrors
        mirror_keys = [
            "DestinationFolder", "Userfolder", "size", "basic", "backend",
            "allowusers", "Allowlogin", "api_key", "jwtduration", "ratelimiter",
            "FrontendURL", "URL", "Ratelimiter", "Allowfreq", "resettime",
            "cooldowntime", "host", "port", "threads", "access_code",
            "opt_password", "trash", "stats", "file", "trashfile"
        ]
        for k in mirror_keys:
            if k in server_data and server_data[k] is not None:
                self.data[k] = server_data[k]

        self.data["config_path"] = server_config_path

        # Ensure all default keys exist in server_data and self.data so config.json is ALWAYS full and complete
        for k, default_val in _DEFAULT_CONFIG.items():
            if k not in server_data or server_data[k] is None:
                server_data[k] = self.data.get(k) if self.data.get(k) is not None else default_val
            if k not in self.data or self.data[k] is None:
                self.data[k] = server_data.get(k) if server_data.get(k) is not None else default_val

        # Write out both files safely
        try:
            with open(server_config_path, "w", encoding="utf-8") as f:
                json.dump(server_data, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not sync to server config {server_config_path}: {e}", file=sys.stderr)
            return False

        try:
            with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

        # Update config.py PATH or self.path variable inside target_dir if config.py exists
        config_py_path = os.path.join(target_dir, CODE_CONFIG_SCRIPT)
        if os.path.exists(config_py_path):
            try:
                with open(config_py_path, "r", encoding="utf-8") as f:
                    content = f.read()
                pattern = r'((?:^\s*PATH|self\.path)\s*=\s*[\'"]).*?([\'"])'
                normalized_path = server_config_path.replace("\\", "/")
                replacement = rf'\g<1>{normalized_path}\g<2>'
                new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
                if count > 0 and new_content != content:
                    with open(config_py_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Warning: Could not update {config_py_path}: {e}", file=sys.stderr)

        return True

config = Config()

def apply_google_light_theme(style, root):
    """Applies a premium, Google-inspired Light Theme (typical Windows installation white) to standard ttk widgets and root window."""
    root.configure(bg="#ffffff")
    
    # Check if 'clam' theme is available and use it
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    # Configure base style options
    style.configure(".", 
                    background="#ffffff", 
                    foreground="#202124", 
                    font=("Segoe UI", 10),
                    troughcolor="#f1f3f4")
                    
    # TFrame
    style.configure("TFrame", background="#ffffff")
    
    # TLabelframe
    style.configure("TLabelframe", background="#f8f9fa", bordercolor="#dadce0", lightcolor="#dadce0", darkcolor="#dadce0")
    style.configure("TLabelframe.Label", background="#f8f9fa", foreground="#1a73e8", font=("Segoe UI", 10, "bold"))
    
    # TLabel
    style.configure("TLabel", background="#ffffff", foreground="#202124")
    
    # Standard Button
    style.configure("TButton", 
                    background="#f1f3f4", 
                    foreground="#202124", 
                    bordercolor="#dadce0", 
                    lightcolor="#f1f3f4", 
                    darkcolor="#f1f3f4",
                    font=("Segoe UI", 10, "bold"),
                    focuscolor="none",
                    padding=(10, 5))
    style.map("TButton",
              background=[("active", "#e8eaed"), ("disabled", "#f8f9fa")],
              foreground=[("active", "#202124"), ("disabled", "#b0b4b9")],
              bordercolor=[("active", "#bdc1c6"), ("disabled", "#e8eaed")])
              
    # Accent Button (Primary Button)
    style.configure("Accent.TButton", 
                    background="#1a73e8", 
                    foreground="#ffffff", 
                    bordercolor="#1a73e8", 
                    lightcolor="#1a73e8", 
                    darkcolor="#1a73e8",
                    font=("Segoe UI", 10, "bold"),
                    focuscolor="none",
                    padding=(10, 5))
    style.map("Accent.TButton",
              background=[("active", "#1557b0"), ("disabled", "#f8f9fa")],
              foreground=[("active", "#ffffff"), ("disabled", "#b0b4b9")],
              bordercolor=[("active", "#1557b0"), ("disabled", "#e8eaed")])
              
    # Checkbuttons (Toolbutton style)
    style.configure("Toolbutton", 
                    background="#f1f3f4", 
                    foreground="#202124",
                    bordercolor="#dadce0",
                    padding=(8, 4))
    style.map("Toolbutton",
              background=[("selected", "#e8f0fe"), ("active", "#e8eaed")],
              foreground=[("selected", "#1a73e8"), ("active", "#202124")],
              bordercolor=[("selected", "#1a73e8"), ("active", "#bdc1c6")])
              
    # Standard Checkbutton (non-toolbutton style)
    style.configure("TCheckbutton",
                    background="#ffffff",
                    foreground="#202124",
                    focuscolor="none")
    style.map("TCheckbutton",
              background=[("active", "#ffffff")],
              foreground=[("active", "#202124")])
              
    # Entries
    style.configure("TEntry", 
                    fieldbackground="#ffffff", 
                    foreground="#202124",
                    bordercolor="#dadce0",
                    lightcolor="#ffffff",
                    darkcolor="#ffffff",
                    insertcolor="#202124",
                    padding=5)
    style.map("TEntry",
              bordercolor=[("focus", "#1a73e8")])
              
    # Spinboxes
    style.configure("TSpinbox", 
                    fieldbackground="#ffffff", 
                    foreground="#202124",
                    bordercolor="#dadce0",
                    lightcolor="#ffffff",
                    darkcolor="#ffffff",
                    arrowcolor="#202124",
                    padding=4)
    style.map("TSpinbox",
              bordercolor=[("focus", "#1a73e8")])
                    
    # Progressbar
    style.configure("Horizontal.TProgressbar", 
                    troughcolor="#f1f3f4", 
                    background="#1a73e8",
                    bordercolor="#dadce0",
                    lightcolor="#ffffff",
                    darkcolor="#ffffff")


