import urllib.request as DOWNLOAD
import os
import sys
import zipfile
from pathlib import Path

try:
    from pckconfig import config, PYTHON_EXE, CLOUDFLARED_EXE, GITHUB_REPO
except ImportError:
    from package.pckconfig import config, PYTHON_EXE, CLOUDFLARED_EXE, GITHUB_REPO

PYTHON_VERSION = "3.12.4"

def get_workspace_dir():
    """Dynamically get the workspace directory path."""
    return config.get("workspace_path") or config.get("dir") or os.path.join(os.getcwd(), GITHUB_REPO)

def find_executable(name):
    """Fast check for executable in system PATH without spawning subprocesses."""
    path_env = os.environ.get("PATH", "")
    for path in path_env.split(os.pathsep):
        candidate = os.path.join(path, name)
        if os.name == "nt" and not candidate.lower().endswith(".exe"):
            candidate += ".exe"
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return os.path.normpath(candidate)
    return None

def checkpython():
    # 1. Instant check: use the currently running Python interpreter path
    #    Skip this when running as a PyInstaller .exe (sys.executable is the bundle)
    if not getattr(sys, 'frozen', False):
        if sys.executable and os.path.exists(sys.executable):
            return True, "python", os.path.normpath(sys.executable)
        
    # 2. PATH lookup
    for command in ("python", "py"):
        exe = find_executable(command)
        if exe:
            return True, command, exe

    # 3. Direct Windows standard installation directories search
    # (Crucial for detecting Python right after installing it before env PATH is reloaded)
    if os.name == "nt":
        user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        local_appdata = os.environ.get("LOCALAPPDATA") or os.path.join(user_profile, "AppData", "Local")
        program_files = os.environ.get("ProgramFiles") or r"C:\Program Files"
        program_files_x86 = os.environ.get("ProgramFiles(x86)") or r"C:\Program Files (x86)"
        
        search_dirs = []
        if local_appdata:
            programs_py = os.path.join(local_appdata, "Programs", "Python")
            if os.path.exists(programs_py):
                search_dirs.append(programs_py)
        if os.path.exists(r"C:\Python312"):
            search_dirs.append(r"C:\Python312")
            
        pf_py = os.path.join(program_files, "Python")
        if os.path.exists(pf_py):
            search_dirs.append(pf_py)
        pf_x86_py = os.path.join(program_files_x86, "Python")
        if os.path.exists(pf_x86_py):
            search_dirs.append(pf_x86_py)
            
        # Search direct subdirectories (e.g. Python312, Python311 etc.)
        for base_dir in search_dirs:
            if os.path.isdir(base_dir):
                try:
                    for entry in os.listdir(base_dir):
                        full_entry = os.path.join(base_dir, entry)
                        if os.path.isdir(full_entry) and entry.lower().startswith("python"):
                            py_exe = os.path.join(full_entry, "python.exe")
                            if os.path.exists(py_exe):
                                return True, "python", os.path.normpath(py_exe)
                except Exception:
                    pass
                    
        # Check root C:\ drive folders starting with Python
        try:
            for entry in os.listdir("C:\\"):
                if entry.lower().startswith("python"):
                    py_exe = os.path.normpath(os.path.join("C:\\", entry, "python.exe"))
                    if os.path.exists(py_exe):
                        return True, "python", py_exe
        except Exception:
            pass

    return False, None, None

def checkcloudflared():
    # 1. AppData Local PersonalDrive bin check
    appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    local_cf = os.path.normpath(os.path.join(appdata_dir, "PersonalDrive", "bin", CLOUDFLARED_EXE))
    if os.path.exists(local_cf):
        return True, "local_cloudflared", local_cf

    # 2. Workspace path check
    workspace_cf = os.path.join(get_workspace_dir(), CLOUDFLARED_EXE)
    if os.path.exists(workspace_cf):
        return True, "workspace_cloudflared", os.path.normpath(workspace_cf)
        
    # 3. PATH lookup
    exe = find_executable("cloudflared")
    if exe:
        return True, "cloudflared", exe
        
    return False, None, None

def checkngrok():
    """Deprecated alias for checkcloudflared"""
    return checkcloudflared()

def getarch():
    arch = os.environ.get("PROCESSOR_ARCHITEW6432")
    if arch:
        return arch.upper()
    return os.environ.get("PROCESSOR_ARCHITECTURE", "AMD64").upper()

def progress(block_num, block_size, total_size):
    if total_size <= 0:
        return
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    print(f"\rDownloading... {percent:.1f}%", end="")

def downloadpython():
    """Download Python installer. Returns the installer path for the user to run."""
    arch = getarch()
    if arch == "AMD64":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
    elif arch == "x86":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}.exe"
    elif arch == "ARM64":
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-arm64.exe"
    else:
        URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
       
    Filename = os.path.join(get_workspace_dir(), "python-installer.exe")
    DOWNLOAD.urlretrieve(URL, Filename, reporthook=progress)
    return Filename

def downloadcloudflared():
    """Download cloudflared directly into the AppData local bin directory."""
    appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    bin_dir = os.path.join(appdata_dir, "PersonalDrive", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    
    target_path = os.path.join(bin_dir, CLOUDFLARED_EXE)
    URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    
    DOWNLOAD.urlretrieve(URL, target_path, reporthook=progress)
    return target_path

def downloadngrok():
    """Deprecated alias for downloadcloudflared"""
    return downloadcloudflared()

def PYTHON():
    """Returns [command, path] on success, [0, 0] on failure."""
    output, command, path = checkpython()
    if output:
        try:
            config.set("python", path)
        except Exception:
            pass
        return [command, path]
    else:
        return [0, 0]
    
def CLOUDFLARED():
    """Returns [command, path] on success, [0, 0] on failure."""
    output, command, path = checkcloudflared()
    if output:
        try:
            config.set("cloudflared", path)
        except Exception:
            pass
        return [command, path]
    else:
        return [0, 0]

def NGROK():
    """Deprecated alias for CLOUDFLARED"""
    return CLOUDFLARED()
