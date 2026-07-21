"""
NasCloud — Unified Setup & Server Application

Intelligently routes to either the Setup Wizard (if setup is incomplete)
or directly to the Server Launcher GUI (if setup is complete).
Bundled as a single self-contained application (NasCloud.exe).
"""
import sys
import os
import tkinter as tk

try:
    from pckconfig import config, APP_DISPLAY_NAME, APP_VERSION, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH
    from GUIsetup import ProgramSetupApp
    from GUIconfig import ServerConfigApp
    from server_launcher import ServerLauncher
except ImportError:
    from package.pckconfig import config, APP_DISPLAY_NAME, APP_VERSION, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH
    from package.GUIsetup import ProgramSetupApp
    from package.GUIconfig import ServerConfigApp
    from package.server_launcher import ServerLauncher


def _safe_print(msg):
    """Print only when stdout is available (not in windowed .exe mode)."""
    try:
        if sys.stdout is not None:
            print(msg)
            sys.stdout.flush()
    except Exception:
        pass


def fetch_remote_config(root):
    """Dynamically fetch urls.json from GitHub and update config if a new version/URL is found."""
    def task():
        import urllib.request
        import json
        try:
            url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/urls.json"
            req = urllib.request.Request(url, headers={'User-Agent': 'NasCloud-App/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                remote_version = data.get("version")
                if remote_version and remote_version != APP_VERSION:
                    def show_update():
                        from tkinter import messagebox
                        messagebox.showinfo(
                            "New Version Available",
                            f"A new version of {APP_DISPLAY_NAME} ({remote_version}) is available!\n\n"
                            "Please download it from GitHub to get the latest features.",
                            parent=root
                        )
                    root.after(2000, show_update)
                    
                central = data.get("central_server_url") or data.get("CENTRAL_SERVER_URL")
                frontend = data.get("frontend_url") or data.get("DEFAULT_FRONTEND_URL")
                
                if central:
                    config.set("central_server_url", central)
                if frontend:
                    config.set("URL", frontend)
        except Exception as e:
            _safe_print(f"Warning: Failed to fetch urls.json: {e}")
            
    import threading
    threading.Thread(target=task, daemon=True).start()


def is_setup_complete():
    """Check if the user has already completed the initial setup."""
    workspace = config.get("dir", "")
    return bool(workspace and os.path.exists(workspace))


def main():
    root = tk.Tk()
    
    # Start checking for urls.json remotely
    fetch_remote_config(root)
    
    if is_setup_complete():
        # Setup already complete — jump straight to Server Launcher
        _safe_print(f"{APP_DISPLAY_NAME} setup is already complete. Launching Server.")
        app = ServerLauncher(root)
        root.mainloop()
        sys.exit(0)

    setup_completed = False
    config_completed = False

    def transition_to_server():
        if not root.winfo_exists():
            return
        for widget in root.winfo_children():
            widget.destroy()
        _safe_print(f"Transitioning to {APP_DISPLAY_NAME} Server GUI...")
        ServerLauncher(root)

    # ── Phase 1: Setup Wizard ──────────────────────────────
    def on_setup_complete(result):
        nonlocal setup_completed
        setup_completed = True
        config.reload()
        
        def transition():
            if not root.winfo_exists():
                return
            # Clear all setup widgets from the root window
            for widget in root.winfo_children():
                widget.destroy()
                
            # Start Phase 2 (Server Configuration) inside the same root window
            build_config_gui()
            
        root.after_idle(transition)

    def on_setup_cancel():
        root.destroy()
        sys.exit(1)

    # ── Phase 2: Server Configuration ──────────────────────
    def on_config_complete(combined_config):
        nonlocal config_completed
        
        allow_users = combined_config.get("allowusers", False)
        if not allow_users:
            def transition_to_file_copy():
                if not root.winfo_exists():
                    return
                # Clear all configuration widgets from the root window
                for widget in root.winfo_children():
                    widget.destroy()
                
                # Make the window non-resizable again for setup/file-copy
                root.resizable(False, False)
                # Set window geometry back to setup size
                root.geometry("550x550")
                
                # Phase 3: Start ProgramSetupApp directly on the files screen
                def on_file_copy_complete(result):
                    nonlocal config_completed
                    config_completed = True
                    # Transition to ServerLauncher instead of launching separate exe
                    if root.winfo_exists():
                        for widget in root.winfo_children():
                            widget.destroy()
                        ServerLauncher(root)
                
                def on_file_copy_cancel():
                    root.destroy()
                    sys.exit(1)
                
                ProgramSetupApp(root, start_screen="files", on_complete=on_file_copy_complete, on_cancel=on_file_copy_cancel)
            
            root.after_idle(transition_to_file_copy)
        else:
            config_completed = True
            if root.winfo_exists():
                for widget in root.winfo_children():
                    widget.destroy()
                ServerLauncher(root)

    def on_config_cancel():
        root.destroy()
        sys.exit(1)

    def build_config_gui():
        ServerConfigApp(root, on_complete=on_config_complete, on_cancel=on_config_cancel)

    # Start ProgramSetupApp in the root window
    ProgramSetupApp(root, on_complete=on_setup_complete, on_cancel=on_setup_cancel)
    root.mainloop()

    # Clean up the window after mainloop exits
    try:
        if root.winfo_exists():
            root.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    main()
