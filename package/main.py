"""
PersonalDrive — Unified Setup & Configuration Launcher

Seamlessly chains the Setup Wizard (Steps 1-3) into the
Server Configuration GUI in a single process. This is the
entry point for both development runs and the .exe build.
"""
import sys
import tkinter as tk

try:
    from pckconfig import config, APP_DISPLAY_NAME
    from GUIsetup import ProgramSetupApp
    from GUIconfig import ServerConfigApp
except ImportError:
    from package.pckconfig import config, APP_DISPLAY_NAME
    from package.GUIsetup import ProgramSetupApp
    from package.GUIconfig import ServerConfigApp


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
        config_completed = True
        if root.winfo_exists():
            root.destroy()

    def on_config_cancel():
        root.destroy()
        sys.exit(1)

    def build_config_gui():
        ServerConfigApp(root, on_complete=on_config_complete, on_cancel=on_config_cancel)

    # Start ProgramSetupApp in the root window
    ProgramSetupApp(root, on_complete=on_setup_complete, on_cancel=on_setup_cancel)
    root.mainloop()

    if config_completed:
        print(f"\n{APP_DISPLAY_NAME} setup and configuration complete!")
        sys.exit(0)
    else:
        print("Configuration was cancelled by the user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
