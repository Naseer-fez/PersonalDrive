import json
import os
import sys

# ──────────────────────────────────────────────
# BRANDING CONSTANTS — Single Source of Truth
# ──────────────────────────────────────────────
APP_NAME            = "PersonalDrive"
APP_DISPLAY_NAME    = "Personal Drive"
APP_DESCRIPTION     = "Self-hosted personal cloud storage server"

# Window Titles (used in root.title())
SETUP_TITLE         = f"{APP_DISPLAY_NAME} Setup"
SETUP_STEP1_TITLE   = f"{SETUP_TITLE} — Step 1: Workspace"
SETUP_STEP2_TITLE   = f"{SETUP_TITLE} — Step 2: Ngrok Auth"
SETUP_STEP3_TITLE   = f"{SETUP_TITLE} — Step 3: Code Server"
CONFIG_TITLE        = f"{APP_DISPLAY_NAME} — Server Configuration"
HELP_TITLE          = "Ngrok Authtoken Help"
CONFIG_HELP_TITLE   = "Configuration Guide"

# Section Labels (used inside LabelFrames)
LBL_WORKSPACE       = " Select Workspace "
LBL_INSTALL_OPTIONS  = " Installation Options "
LBL_NGROK_AUTH       = " Configure Ngrok Authentication "
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
# Resolve config directory (supports PyInstaller)
# ──────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller .exe — use the directory containing the .exe
    _CONFIG_DIR = os.path.dirname(sys.executable)
else:
    # Running as a normal Python script
    _CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

_CONFIG_PATH = os.path.join(_CONFIG_DIR, PACKAGE_CONFIG_FILE)

# Default configuration template (created on first run if missing)
_DEFAULT_CONFIG = {
    "dir": "",
    "python": "",
    "ngrok": "",
    "ngrok_token": "",
    "config_path": "",
    "DestinationFolder": "",
    "Userfolder": "",
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
    "Resettime": DEFAULT_RESET_SEC,
    "cooldowntime": DEFAULT_COOLDOWN_SEC,
    "host": DEFAULT_HOST,
    "port": DEFAULT_PORT,
    "threads": DEFAULT_THREADS,
    "initial_username": "",
    "initial_email": "",
    "initial_password": ""
}


# ──────────────────────────────────────────────
# Package Config Helper
# ──────────────────────────────────────────────
class Config:
    def __init__(self):
        # Auto-create config file with defaults if it doesn't exist
        if not os.path.exists(_CONFIG_PATH):
            with open(_CONFIG_PATH, "w") as file:
                json.dump(_DEFAULT_CONFIG, file, indent=4)
        self.reload()

    def reload(self):
        with open(_CONFIG_PATH) as file:
            self.data = json.load(file)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        with open(_CONFIG_PATH, "w") as file:
            json.dump(self.data, file, indent=4)

config = Config()
