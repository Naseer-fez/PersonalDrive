import os
import sys
import zipfile
import shutil
from pathlib import Path

try:
    from pckconfig import config, PYTHON_EXE, CLOUDFLARED_EXE, GITHUB_REPO
except ImportError:
    from package.pckconfig import config, PYTHON_EXE, CLOUDFLARED_EXE, GITHUB_REPO

PYTHON_VERSION = "3.12.4"

def get_workspace_dir():
    """Dynamically get the workspace directory path."""
    return config.get("workspace_path") or config.get("dir") or os.path.join(os.getcwd(), GITHUB_REPO)

def get_local_bin_dir():
    """Get the immutable AppData bin directory for portable binaries."""
    appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.normpath(os.path.join(appdata_dir, "NasCloud", "bin"))

def get_asset_path(filename):
    """Resolve offline asset filepath in development or PyInstaller frozen state."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    asset_path = os.path.join(base_dir, "assets", filename)
    if not os.path.exists(asset_path):
        asset_path = os.path.join(base_dir, filename)
    return asset_path

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
    # 0. Check AppData Local NasCloud bin check (portable Python environment)
    bin_py = os.path.join(get_local_bin_dir(), "python.exe")
    if os.path.exists(bin_py):
        return True, "local_python", os.path.normpath(bin_py)

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
    # 1. AppData Local NasCloud bin check
    local_cf = os.path.normpath(os.path.join(get_local_bin_dir(), CLOUDFLARED_EXE))
    if os.path.exists(local_cf) and os.path.getsize(local_cf) > 1000000:
        return True, "local_cloudflared", local_cf

    # 2. Workspace path check
    workspace_cf = os.path.join(get_workspace_dir(), CLOUDFLARED_EXE)
    if os.path.exists(workspace_cf) and os.path.getsize(workspace_cf) > 1000000:
        return True, "workspace_cloudflared", os.path.normpath(workspace_cf)
        
    # 3. PATH lookup
    exe = find_executable("cloudflared")
    if exe and os.path.getsize(exe) > 1000000:
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
    print(f"\rExtracting... {percent:.1f}%", end="")

def extractpython(reporthook=None):
    """Extract bundled python_env.zip into %LOCALAPPDATA%/NasCloud/bin/."""
    bin_dir = get_local_bin_dir()
    os.makedirs(bin_dir, exist_ok=True)
    zip_path = get_asset_path("python_env.zip")
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Bundled Python archive not found at: {zip_path}")
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        members = zip_ref.infolist()
        total_count = len(members)
        for idx, member in enumerate(members):
            zip_ref.extract(member, bin_dir)
            if reporthook and total_count > 0:
                reporthook(idx + 1, 1, total_count)
                
    python_exe = os.path.join(bin_dir, "python.exe")
    return python_exe

def extractcloudflared(reporthook=None):
    """Copy bundled cloudflared.exe directly into %LOCALAPPDATA%/NasCloud/bin/."""
    bin_dir = get_local_bin_dir()
    os.makedirs(bin_dir, exist_ok=True)
    src_path = get_asset_path(CLOUDFLARED_EXE)
    
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Bundled cloudflared binary not found at: {src_path}")
        
    target_path = os.path.join(bin_dir, CLOUDFLARED_EXE)
    shutil.copy2(src_path, target_path)
    if reporthook:
        reporthook(1, 1, 1)
        
    return target_path

def downloadpython(reporthook=None):
    """Offline alias for extractpython"""
    return extractpython(reporthook=reporthook)

def downloadcloudflared():
    """Offline alias for extractcloudflared"""
    return extractcloudflared()

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

