"""
NasCloud — Unified Setup & Configuration Launcher

Seamlessly chains the Setup Wizard (Steps 1-3) into the
Server Configuration GUI in a single process. This is the
entry point for both development runs and the .exe build.
"""
import sys
import os
import subprocess
import tkinter as tk

try:
    from pckconfig import config, APP_DISPLAY_NAME
    from GUIsetup import ProgramSetupApp
    from GUIconfig import ServerConfigApp
except ImportError:
    from package.pckconfig import config, APP_DISPLAY_NAME
    from package.GUIsetup import ProgramSetupApp
    from package.GUIconfig import ServerConfigApp


SERVER_EXE_NAME = "NasCloudServer.exe"


def _safe_print(msg):
    """Print only when stdout is available (not in windowed .exe mode)."""
    try:
        if sys.stdout is not None:
            print(msg)
            sys.stdout.flush()
    except Exception:
        pass


def main():
    root = tk.Tk()
    setup_completed = False
    config_completed = False

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
                    _launch_server_exe()
                    if root.winfo_exists():
                        root.quit()
                
                def on_file_copy_cancel():
                    root.destroy()
                    sys.exit(1)
                
                ProgramSetupApp(root, start_screen="files", on_complete=on_file_copy_complete, on_cancel=on_file_copy_cancel)
            
            root.after_idle(transition_to_file_copy)
        else:
            config_completed = True
            _launch_server_exe()
            if root.winfo_exists():
                root.quit()

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
        root.destroy()
    except Exception:
        pass

    if config_completed:
        _safe_print(f"\n{APP_DISPLAY_NAME} setup and configuration complete!")
        sys.exit(0)
    else:
        _safe_print("Configuration was cancelled by the user.")
        sys.exit(1)


def _launch_server_exe():
    """Find and launch the NasCloud Server executable as a detached process."""
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller .exe — look next to the executable
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running as a Python script — look in the same directory
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    server_exe = os.path.join(exe_dir, SERVER_EXE_NAME)
    if os.path.exists(server_exe):
        try:
            # Launch as a fully detached process
            subprocess.Popen(
                [server_exe],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
            _safe_print(f"Launched {SERVER_EXE_NAME} from: {server_exe}")
        except Exception as e:
            _safe_print(f"Failed to launch {SERVER_EXE_NAME}: {e}")
    else:
        _safe_print(f"{SERVER_EXE_NAME} not found in {exe_dir} — skipping auto-launch.")


if __name__ == "__main__":
    main()
