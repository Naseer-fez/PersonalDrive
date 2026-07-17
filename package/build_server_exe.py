"""
PersonalDrive — Build Script (Server.exe)

Packages the Server Launcher GUI into a single standalone .exe using PyInstaller.

Usage:
    python build_server_exe.py

Output:
    dist/PersonalDriveServer.exe
"""
import subprocess
import sys
import os
import shutil


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRY_POINT = os.path.join(SCRIPT_DIR, "server_launcher.py")
EXE_NAME = "PersonalDriveServer"
DIST_DIR = os.path.join(SCRIPT_DIR, "dist")
BUILD_DIR = os.path.join(SCRIPT_DIR, "build")
SPEC_FILE = os.path.join(SCRIPT_DIR, f"{EXE_NAME}.spec")


def check_pyinstaller():
    """Check if PyInstaller is available."""
    try:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} found.")
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller via pip."""
    print("  Installing PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: Failed to install PyInstaller:\n{result.stderr}")
        return False
    print("  PyInstaller installed successfully.")
    return True


def build():
    """Run the PyInstaller build for the server launcher."""
    print(f"\n{'='*50}")
    print(f"  Building {EXE_NAME}.exe")
    print(f"{'='*50}\n")

    # Step 1: Check PyInstaller
    print("[1/3] Checking for PyInstaller...")
    if not check_pyinstaller():
        print("  PyInstaller not found.")
        if not install_pyinstaller():
            sys.exit(1)

    # Step 2: Clean previous build artifacts (specifically the ones for this exe, or build/dist dir contents)
    print("[2/3] Cleaning previous server build artifacts...")
    
    # Delete spec file if exists
    if os.path.exists(SPEC_FILE):
        try:
            os.remove(SPEC_FILE)
            print(f"  Removed: {SPEC_FILE}")
        except Exception as e:
            print(f"  Warning: Could not remove {SPEC_FILE}: {e}")
        
    # Delete specific build folders inside build/ for this target to not disrupt setup wizard build if run sequentially
    target_build = os.path.join(BUILD_DIR, EXE_NAME)
    if os.path.exists(target_build):
        try:
            shutil.rmtree(target_build)
            print(f"  Removed: {target_build}")
        except Exception as e:
            print(f"  Warning: Could not remove {target_build}: {e}")

    target_dist_exe = os.path.join(DIST_DIR, f"{EXE_NAME}.exe")
    if os.path.exists(target_dist_exe):
        try:
            os.remove(target_dist_exe)
            print(f"  Removed: {target_dist_exe}")
            import time
            time.sleep(1)  # Give Windows a moment to release the file handle
        except Exception as e:
            print(f"  Warning: Could not remove {target_dist_exe}: {e}")

    # Step 3: Run PyInstaller
    print("[3/3] Running PyInstaller...")

    hidden_imports = [
        "pckconfig",
        "packages",
        "GUIconfig",
        "installdepen",
        "pipinstaller",
        "controler",
        "urls",
        "url",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                          # Single .exe output
        "--windowed",                         # No console window (GUI app)
        "--name", EXE_NAME,                   # Output name
        "--distpath", DIST_DIR,               # Output directory
        "--workpath", BUILD_DIR,              # Build temp directory
        "--specpath", SCRIPT_DIR,             # Spec file location
    ]

    # Add hidden imports
    for mod in hidden_imports:
        cmd.extend(["--hidden-import", mod])

    # Add the entry point
    cmd.append(ENTRY_POINT)

    print(f"  Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode != 0:
        print(f"\n  BUILD FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)

    # Verify output
    exe_path = os.path.join(DIST_DIR, f"{EXE_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n{'='*50}")
        print(f"  BUILD SUCCESSFUL!")
        print(f"  Output: {exe_path}")
        print(f"  Size:   {size_mb:.1f} MB")
        print(f"{'='*50}")
        print(f"\n  This executable will use all the paths provided in")
        print(f"  packageconfig.json to run python, waitress, and ngrok.")
    else:
        print(f"\n  ERROR: Expected output not found at {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    build()
