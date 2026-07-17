import os
import sys
import json
import shutil
import webbrowser
import threading
import urllib.request as DOWNLOAD
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

try:
    from pckconfig import (
        config, APP_NAME, APP_DISPLAY_NAME,
        SETUP_TITLE, SETUP_STEP1_TITLE, SETUP_STEP2_TITLE, SETUP_STEP3_TITLE,
        HELP_TITLE, LBL_WORKSPACE, LBL_INSTALL_OPTIONS, LBL_NGROK_AUTH,
        LBL_CODE_SERVER, GITHUB_ZIP_URL, GITHUB_EXTRACTED_DIR,
        NGROK_SIGNUP_URL, NGROK_DASHBOARD_URL, PYTHON_EXE, NGROK_EXE, CLOUDFLARED_EXE,
        apply_google_light_theme
    )
    from installdepen import PYTHON, NGROK, CLOUDFLARED, downloadpython
except ImportError:
    from package.pckconfig import (
        config, APP_NAME, APP_DISPLAY_NAME,
        SETUP_TITLE, SETUP_STEP1_TITLE, SETUP_STEP2_TITLE, SETUP_STEP3_TITLE,
        HELP_TITLE, LBL_WORKSPACE, LBL_INSTALL_OPTIONS, LBL_NGROK_AUTH,
        LBL_CODE_SERVER, GITHUB_ZIP_URL, GITHUB_EXTRACTED_DIR,
        NGROK_SIGNUP_URL, NGROK_DASHBOARD_URL, PYTHON_EXE, NGROK_EXE, CLOUDFLARED_EXE,
        apply_google_light_theme
    )
    from package.installdepen import PYTHON, NGROK, CLOUDFLARED, downloadpython

class ProgramSetupApp:
    def __init__(self, root, on_complete=None, on_cancel=None):
        self.root = root
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.root.title(SETUP_TITLE)
        self.root.geometry("550x380")
        self.root.resizable(False, False)
        self.center_window()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.style = ttk.Style()
        apply_google_light_theme(self.style, self.root)
        
        self.create_widgets()
        self.load_saved_data()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- Screen 1 Container ---
        self.screen1_frame = ttk.Frame(self.main_container, padding="20")
        
        path_frame = ttk.LabelFrame(self.screen1_frame, text=LBL_WORKSPACE, padding="15")
        path_frame.pack(fill=tk.X, pady=(0, 15))

        select_lbl = ttk.Label(
            path_frame, 
            text="Select where you want to store the data:", 
            font=("Segoe UI", 10)
        )
        select_lbl.pack(anchor=tk.W, pady=(0, 5))

        path_row = ttk.Frame(path_frame)
        path_row.pack(fill=tk.X, expand=True)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_row, textvariable=self.path_var, width=45)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.browse_btn = ttk.Button(path_row, text="Browse...", command=self.browse_directory)
        self.browse_btn.pack(side=tk.RIGHT)

        self.next_btn = ttk.Button(path_frame, text="Next", command=self.handle_next, style="Accent.TButton")
        self.next_btn.pack(pady=(10, 0))

        options_frame = ttk.LabelFrame(self.screen1_frame, text=LBL_INSTALL_OPTIONS, padding="15")
        options_frame.pack(fill=tk.BOTH, expand=True)

        self.python_install_var = tk.BooleanVar(value=False)
        self.python_already_var = tk.BooleanVar(value=False)
        self.cloudflared_install_var = tk.BooleanVar(value=False)
        self.cloudflared_already_var = tk.BooleanVar(value=False)
        self.ngrok_install_var = self.cloudflared_install_var # Alias for backward compatibility
        self.ngrok_already_var = self.cloudflared_already_var # Alias for backward compatibility

        row1 = ttk.Frame(options_frame)
        row1.pack(fill=tk.X, pady=(0, 10))

        self.install_python_btn = ttk.Checkbutton(
            row1, 
            text="Install Python", 
            variable=self.python_install_var,
            style="Toolbutton",
            command=self.update_python_states
        )
        self.install_python_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.install_cloudflared_btn = ttk.Checkbutton(
            row1, 
            text="Install Cloudflare", 
            variable=self.cloudflared_install_var,
            style="Toolbutton",
            command=self.update_cloudflared_states
        )
        self.install_cloudflared_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))

        row2 = ttk.Frame(options_frame)
        row2.pack(fill=tk.X)

        self.python_already_btn = ttk.Checkbutton(
            row2, 
            text="Python Already Installed", 
            variable=self.python_already_var,
            style="Toolbutton",
            command=self.update_python_states
        )
        self.python_already_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.cloudflared_already_btn = ttk.Checkbutton(
            row2, 
            text="Cloudflare Already Installed", 
            variable=self.cloudflared_already_var,
            style="Toolbutton",
            command=self.update_cloudflared_states
        )
        self.cloudflared_already_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))

        # --- Screen 2 Container (Ngrok Authtoken Setup) ---
        self.screen2_frame = ttk.Frame(self.main_container, padding="20")
        
        auth_frame = ttk.LabelFrame(self.screen2_frame, text=LBL_NGROK_AUTH, padding="20")
        auth_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        token_lbl = ttk.Label(
            auth_frame,
            text="Please enter your Ngrok Authtoken below:",
            font=("Segoe UI", 11, "bold")
        )
        token_lbl.pack(anchor=tk.W, pady=(0, 10))
        
        desc_lbl = ttk.Label(
            auth_frame,
            text="You can obtain this token from your dashboard at dashboard.ngrok.com",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        desc_lbl.pack(anchor=tk.W, pady=(0, 15))
        
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(auth_frame, textvariable=self.token_var, width=50)
        self.token_entry.pack(fill=tk.X, pady=(0, 10))
        
        screen2_btn_frame = ttk.Frame(self.screen2_frame)
        screen2_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.back2_btn = ttk.Button(screen2_btn_frame, text="Back", command=self.show_screen1)
        self.back2_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.help2_btn = ttk.Button(screen2_btn_frame, text="Help", command=self.open_help_dialog)
        self.help2_btn.pack(side=tk.LEFT)
        
        self.next2_btn = ttk.Button(screen2_btn_frame, text="Next", command=self.handle_next2, style="Accent.TButton")
        self.next2_btn.pack(side=tk.RIGHT)

        # --- Screen 3 Container (Code Server Setup) ---
        self.screen3_frame = ttk.Frame(self.main_container, padding="20")
        
        code_frame = ttk.LabelFrame(self.screen3_frame, text=LBL_CODE_SERVER, padding="20")
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        q_lbl = ttk.Label(
            code_frame,
            text="Install the Code server?",
            font=("Segoe UI", 11, "bold")
        )
        q_lbl.pack(anchor=tk.W, pady=(0, 15))
        
        # Row of Choice Buttons
        choice_row = ttk.Frame(code_frame)
        choice_row.pack(fill=tk.X, pady=(0, 15))
        
        self.already_inst_btn = ttk.Button(
            choice_row, 
            text="Already Installed", 
            command=self.handle_already_installed
        )
        self.already_inst_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.not_inst_btn = ttk.Button(
            choice_row, 
            text="Not Installed (Download)", 
            command=self.handle_not_installed
        )
        self.not_inst_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
        
        # Path details label
        ttk.Label(code_frame, text="Selected Code Server Path:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(10, 2))
        self.code_path_var = tk.StringVar(value="Not Configured")
        self.code_path_lbl = ttk.Label(
            code_frame,
            textvariable=self.code_path_var,
            font=("Segoe UI", 9, "italic"),
            foreground="#1a73e8"
        )
        self.code_path_lbl.pack(anchor=tk.W)
        
        screen3_btn_frame = ttk.Frame(self.screen3_frame)
        screen3_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.back3_btn = ttk.Button(screen3_btn_frame, text="Back", command=self.show_screen1)
        self.back3_btn.pack(side=tk.LEFT)
        
        self.finish_btn = ttk.Button(screen3_btn_frame, text="Finish", command=self.handle_finish, style="Accent.TButton")
        self.finish_btn.pack(side=tk.RIGHT)
        
        self.show_screen1()

    def show_screen1(self):
        self.screen2_frame.pack_forget()
        self.screen3_frame.pack_forget()
        self.screen1_frame.pack(fill=tk.BOTH, expand=True)
        self.root.title(SETUP_STEP1_TITLE)

    def show_screen2(self):
        self.show_screen3()

    def show_screen3(self):
        self.screen1_frame.pack_forget()
        self.screen2_frame.pack_forget()
        self.screen3_frame.pack(fill=tk.BOTH, expand=True)
        self.root.title(SETUP_STEP3_TITLE)

    def update_python_states(self):
        if self.python_install_var.get():
            self.python_already_btn.configure(state="disabled")
        elif self.python_already_var.get():
            self.install_python_btn.configure(state="disabled")
        else:
            self.install_python_btn.configure(state="normal")
            self.python_already_btn.configure(state="normal")

    def update_ngrok_states(self):
        self.update_cloudflared_states()

    def update_cloudflared_states(self):
        if self.cloudflared_install_var.get():
            self.cloudflared_already_btn.configure(state="disabled")
        elif self.cloudflared_already_var.get():
            self.install_cloudflared_btn.configure(state="disabled")
        else:
            self.install_cloudflared_btn.configure(state="normal")
            self.cloudflared_already_btn.configure(state="normal")

    def load_saved_data(self):
        try:
            self.path_var.set(config.get("workspace_path") or config.get("dir", ""))
            self.token_var.set(config.get("ngrok_token", ""))
            
            # Load code server path if already saved in "dir"
            saved_dir = config.get("dir", "")
            if saved_dir and os.path.exists(saved_dir):
                self.code_path_var.set(saved_dir)
        except Exception:
            pass

    def browse_directory(self):
        initial_dir = self.path_var.get() or os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Program Save Directory"
        )
        if selected_dir:
            normalized_path = os.path.normpath(selected_dir)
            self.path_var.set(normalized_path)

    def ask_manual_path(self, dep_name, exe_name):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Locate {dep_name}")
        dialog.geometry("450x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#ffffff")
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        lbl = ttk.Label(
            main_frame, 
            text=f"Please select the folder containing {exe_name} or enter the path manually:",
            justify=tk.LEFT
        )
        lbl.pack(anchor=tk.W, pady=(0, 10))
        
        path_row = ttk.Frame(main_frame)
        path_row.pack(fill=tk.X, pady=(0, 15))
        
        path_var = tk.StringVar()
        entry = ttk.Entry(path_row, textvariable=path_var, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse():
            folder = filedialog.askdirectory(title=f"Select {dep_name} Folder")
            if folder:
                path_var.set(os.path.normpath(folder))
                
        browse_btn = ttk.Button(path_row, text="Browse...", command=browse)
        browse_btn.pack(side=tk.RIGHT)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        result_path = [None]
        
        def confirm():
            val = path_var.get().strip()
            if not val:
                messagebox.showwarning("Warning", "Please enter or select a path.", parent=dialog)
                return
            
            expanded = os.path.expandvars(os.path.expanduser(val))
            candidate_path = expanded
            if os.path.isdir(expanded):
                candidate_path = os.path.join(expanded, exe_name)
                
            if os.path.exists(candidate_path):
                result_path[0] = candidate_path
                dialog.destroy()
            else:
                messagebox.showerror(
                    "Error", 
                    f"Could not locate '{exe_name}' in the specified path:\n{val}",
                    parent=dialog
                )
                
        def cancel():
            dialog.destroy()
            
        cancel_btn = ttk.Button(btn_frame, text="Cancel / Go Back", command=cancel)
        cancel_btn.pack(side=tk.LEFT)
        
        confirm_btn = ttk.Button(btn_frame, text="Confirm", command=confirm, style="Accent.TButton")
        confirm_btn.pack(side=tk.RIGHT)
        
        self.root.wait_window(dialog)
        return result_path[0]

    def performbackend(self, result):
        path = result.get("path")
        python = result.get("python")

        if not PYTHON()[0]:
            if not self.python_install_var.get():
                should_install = messagebox.askyesno(
                    "Python Required",
                    "Python was not detected on your system.\n\nWould you like to download and install Python 3.12 now?",
                    parent=self.root
                )
                if should_install:
                    self.python_install_var.set(True)

            if self.python_install_var.get():
                progress_dialog = tk.Toplevel(self.root)
                progress_dialog.title("Downloading Python")
                progress_dialog.geometry("400x130")
                progress_dialog.resizable(False, False)
                progress_dialog.grab_set()
                progress_dialog.configure(bg="#ffffff")
                
                progress_dialog.update_idletasks()
                w = progress_dialog.winfo_width()
                h = progress_dialog.winfo_height()
                x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (w // 2)
                y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (h // 2)
                progress_dialog.geometry(f'{w}x{h}+{x}+{y}')
                
                lbl = ttk.Label(progress_dialog, text="Downloading Python 3.12 installer...")
                lbl.pack(pady=(15, 5))
                
                bar = ttk.Progressbar(progress_dialog, length=300, mode="determinate")
                bar.pack(pady=5)
                
                percent_lbl = ttk.Label(progress_dialog, text="0%")
                percent_lbl.pack()
                
                download_done = [False]
                download_error = [None]
                installer_path_ref = [None]
                
                def run_download():
                    try:
                        def reporthook(block_num, block_size, total_size):
                            if total_size <= 0:
                                return
                            downloaded = block_num * block_size
                            percent = min(downloaded * 100 // total_size, 100)
                            self.root.after(0, lambda: bar.configure(value=percent))
                            self.root.after(0, lambda: percent_lbl.configure(text=f"{percent}%"))
                        
                        installer_path = downloadpython()
                        installer_path_ref[0] = installer_path
                        download_done[0] = True
                    except Exception as e:
                        download_error[0] = str(e)
                    finally:
                        self.root.after(0, progress_dialog.destroy)
                        
                threading.Thread(target=run_download, daemon=True).start()
                self.root.wait_window(progress_dialog)
                
                if download_error[0] or not download_done[0]:
                    messagebox.showerror("Error", f"Failed to download Python:\n{download_error[0]}", parent=self.root)
                    return False
                
                messagebox.showinfo(
                    "Launch Installer",
                    "Python installer downloaded successfully.\n\n"
                    "We will now launch the installation wizard.\n\n"
                    "⚠️ IMPORTANT: Make sure to check the box 'Add Python.exe to PATH' at the bottom of the installer window, then click 'Install Now'.",
                    parent=self.root
                )
                
                try:
                    import subprocess
                    subprocess.run([installer_path_ref[0]], check=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to run Python installer: {e}", parent=self.root)
                    return False
                
                try:
                    if os.path.exists(installer_path_ref[0]):
                        os.remove(installer_path_ref[0])
                except Exception:
                    pass
                
                if not PYTHON()[0]:
                    messagebox.showerror(
                        "Python Not Found",
                        "Python installation could not be detected. Please locate it manually.",
                        parent=self.root
                    )
                    selected_path = self.ask_manual_path("Python", PYTHON_EXE)
                    if selected_path:
                        try:
                            config.set("python", selected_path)
                        except Exception:
                            pass
                    else:
                        return False
            else:
                messagebox.showerror("Error", "Python is required to run the PersonalDrive server.", parent=self.root)
                selected_path = self.ask_manual_path("Python", PYTHON_EXE)
                if selected_path:
                    try:
                        config.set("python", selected_path)
                    except Exception:
                        pass
                else:
                    return False

        if not CLOUDFLARED()[0]:
            if self.cloudflared_install_var.get():
                progress_dialog = tk.Toplevel(self.root)
                progress_dialog.title("Downloading Cloudflare")
                progress_dialog.geometry("400x130")
                progress_dialog.resizable(False, False)
                progress_dialog.grab_set()
                progress_dialog.configure(bg="#ffffff")
                
                # Center progress dialog
                progress_dialog.update_idletasks()
                w = progress_dialog.winfo_width()
                h = progress_dialog.winfo_height()
                x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (w // 2)
                y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (h // 2)
                progress_dialog.geometry(f'{w}x{h}+{x}+{y}')
                
                lbl = ttk.Label(progress_dialog, text="Downloading cloudflared.exe...")
                lbl.pack(pady=(15, 5))
                
                bar = ttk.Progressbar(progress_dialog, length=300, mode="determinate")
                bar.pack(pady=5)
                
                percent_lbl = ttk.Label(progress_dialog, text="0%")
                percent_lbl.pack()
                
                download_done = [False]
                download_error = [None]
                
                def run_download():
                    try:
                        def reporthook(block_num, block_size, total_size):
                            if total_size <= 0:
                                return
                            downloaded = block_num * block_size
                            percent = min(downloaded * 100 // total_size, 100)
                            self.root.after(0, lambda: bar.configure(value=percent))
                            self.root.after(0, lambda: percent_lbl.configure(text=f"{percent}%"))
                        
                        import urllib.request as DOWNLOAD
                        appdata_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
                        bin_dir = os.path.join(appdata_dir, "PersonalDrive", "bin")
                        os.makedirs(bin_dir, exist_ok=True)
                        target_path = os.path.join(bin_dir, CLOUDFLARED_EXE)
                        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
                        DOWNLOAD.urlretrieve(url, target_path, reporthook=reporthook)
                        config.set("cloudflared", target_path)
                        download_done[0] = True
                    except Exception as e:
                        download_error[0] = str(e)
                    finally:
                        self.root.after(0, progress_dialog.destroy)
                        
                threading.Thread(target=run_download, daemon=True).start()
                self.root.wait_window(progress_dialog)
                
                if download_error[0]:
                    messagebox.showerror("Error", f"Failed to download Cloudflare:\n{download_error[0]}")
                    return False
            else:
                messagebox.showerror("Error", "Looks like Cloudflare is not installed. Please locate it manually.")
                selected_path = self.ask_manual_path("Cloudflare", CLOUDFLARED_EXE)
                if selected_path:
                    try:
                        config.set("cloudflared", selected_path)
                    except Exception:
                        pass
                else:
                    return False

        return True

    def handle_next(self):
        selected_path = self.path_var.get().strip()

        if not selected_path:
            messagebox.showwarning("Warning", "Please select or enter a save directory.")
            return

        expanded_path = os.path.expandvars(os.path.expanduser(selected_path))

        if not os.path.exists(expanded_path):
            create_dir = messagebox.askyesno(
                "Create Directory",
                f"The directory:\n{expanded_path}\ndoes not exist. Would you like to create it?"
            )
            if create_dir:
                try:
                    os.makedirs(expanded_path, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory:\n{e}")
                    return
            else:
                return

        if not os.access(expanded_path, os.W_OK):
            messagebox.showerror("Error", f"The directory is not writable:\n{expanded_path}")
            return

        try:
            config.set("workspace_path", expanded_path)
            if not config.get("DestinationFolder") or config.get("DestinationFolder") == "":
                config.set("DestinationFolder", os.path.normpath(os.path.join(expanded_path, "test")))
            if not config.get("Userfolder") or config.get("Userfolder") == "":
                config.set("Userfolder", os.path.normpath(os.path.join(expanded_path, "userdetails")))
            if not config.get("ratelimiter") or config.get("ratelimiter") == "":
                config.set("ratelimiter", os.path.normpath(os.path.join(expanded_path, "data")))
        except Exception:
            pass

        python_status = "already_installed"
        if self.python_install_var.get():
            python_status = "install"
        elif self.python_already_var.get():
            python_status = "already_installed"

        cloudflared_status = "already_installed"
        if self.cloudflared_install_var.get():
            cloudflared_status = "install"
        elif self.cloudflared_already_var.get():
            cloudflared_status = "already_installed"
        
        result = {
            "path": expanded_path,
            "python": python_status,
            "cloudflared": cloudflared_status,
            "ngrok": cloudflared_status,
            "python_action": python_status,
            "cloudflared_action": cloudflared_status,
            "ngrok_action": cloudflared_status
        }
        
        if not self.performbackend(result):
            return
        
        self.show_screen3()

    def handle_next2(self):
        # Save token
        token = self.token_var.get().strip()
        try:
            config.set("ngrok_token", token)
        except Exception:
            pass
        self.show_screen3()

    def handle_already_installed(self):
        folder = filedialog.askdirectory(title="Select Code Server Folder")
        if folder:
            normalized = os.path.normpath(folder)
            self.code_path_var.set(normalized)

    def handle_not_installed(self):
        parent_dir = filedialog.askdirectory(title="Choose where to save the Code Server project")
        if not parent_dir:
            return
            
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Downloading Code Server")
        progress_dialog.geometry("400x130")
        progress_dialog.resizable(False, False)
        progress_dialog.grab_set()
        
        progress_dialog.update_idletasks()
        width = progress_dialog.winfo_width()
        height = progress_dialog.winfo_height()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (width // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (height // 2)
        progress_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        lbl = ttk.Label(progress_dialog, text=f"Downloading {APP_DISPLAY_NAME} source repository...")
        lbl.pack(pady=(15, 5))
        
        bar = ttk.Progressbar(progress_dialog, length=300, mode="determinate")
        bar.pack(pady=5)
        
        percent_lbl = ttk.Label(progress_dialog, text="0%")
        percent_lbl.pack()
        
        def run_download():
            zip_path = os.path.join(parent_dir, f"{GITHUB_EXTRACTED_DIR}.zip")
            
            def reporthook(block_num, block_size, total_size):
                if total_size <= 0:
                    return
                downloaded = block_num * block_size
                percent = min(downloaded * 100 // total_size, 100)
                
                self.root.after(0, lambda: bar.configure(value=percent))
                self.root.after(0, lambda: percent_lbl.configure(text=f"{percent}%"))
                
            try:
                DOWNLOAD.urlretrieve(GITHUB_ZIP_URL, zip_path, reporthook=reporthook)
                
                self.root.after(0, lambda: lbl.configure(text="Extracting project archive..."))
                self.root.after(0, lambda: bar.configure(mode="indeterminate"))
                self.root.after(0, lambda: bar.start(10))
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(parent_dir)
                    
                os.remove(zip_path)
                
                extracted_dir = os.path.normpath(os.path.join(parent_dir, GITHUB_EXTRACTED_DIR))
                
                # Clean up bloat listed in remove.txt
                remove_file = os.path.join(extracted_dir, "remove.txt")
                if os.path.exists(remove_file):
                    self.root.after(0, lambda: lbl.configure(text="Cleaning up unnecessary files..."))
                    try:
                        with open(remove_file, 'r', encoding='utf-8') as rf:
                            for line in rf:
                                entry = line.strip()
                                if not entry or entry.startswith('#'):
                                    continue
                                target = os.path.normpath(os.path.join(extracted_dir, entry))
                                # Safety: only delete within the extracted directory
                                if not target.startswith(extracted_dir):
                                    continue
                                if os.path.isdir(target):
                                    shutil.rmtree(target, ignore_errors=True)
                                elif os.path.isfile(target):
                                    os.remove(target)
                    except Exception:
                        pass  # Non-critical — continue even if cleanup fails
                    # Remove the remove.txt itself after processing
                    try:
                        os.remove(remove_file)
                    except Exception:
                        pass
                
                def finish_download():
                    self.code_path_var.set(extracted_dir)
                    progress_dialog.destroy()
                    messagebox.showinfo("Success", f"{APP_DISPLAY_NAME} downloaded and saved to:\n{extracted_dir}")
                    
                self.root.after(0, finish_download)
                
            except Exception as e:
                def show_error():
                    progress_dialog.destroy()
                    messagebox.showerror("Error", f"Failed to download {APP_DISPLAY_NAME}:\n{e}")
                self.root.after(0, show_error)
                
        threading.Thread(target=run_download, daemon=True).start()

    def open_help_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title(HELP_TITLE)
        dialog.geometry("480x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#ffffff")
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame = ttk.LabelFrame(main_frame, text=" Help Guide ", padding="15")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        title_lbl = ttk.Label(
            content_frame, 
            text="", 
            font=("Segoe UI", 11, "bold")
        )
        title_lbl.pack(anchor=tk.W, pady=(0, 8))
        
        body_txt = tk.Text(
            content_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            background=dialog.cget("background"),
            foreground="#202124",
            insertbackground="#202124",
            borderwidth=0,
            highlightthickness=0,
            height=6,
            cursor="arrow"
        )
        
        scroll = ttk.Scrollbar(content_frame, command=body_txt.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        body_txt.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        body_txt.config(yscrollcommand=scroll.set)
        
        body_txt.tag_config("link", foreground="#1a73e8", underline=True)
        body_txt.tag_bind("link", "<Enter>", lambda e: body_txt.config(cursor="hand2"))
        body_txt.tag_bind("link", "<Leave>", lambda e: body_txt.config(cursor="arrow"))
        
        current_step = [1]
        
        def render():
            body_txt.config(state="normal")
            body_txt.delete("1.0", tk.END)
            
            if current_step[0] == 1:
                title_lbl.configure(text="Step 1: Create an account")
                
                body_txt.insert(tk.END, "Go to the ")
                body_txt.insert(tk.END, "ngrok website", "link")
                body_txt.insert(tk.END, " and sign up for a free account.")
                
                body_txt.tag_bind("link", "<Button-1>", lambda e: webbrowser.open_new(NGROK_SIGNUP_URL))
            else:
                title_lbl.configure(text="Step 2: Get the Authtoken")
                
                body_txt.insert(tk.END, "After signing in:\n\n1. Open the ")
                body_txt.insert(tk.END, "ngrok dashboard", "link")
                body_txt.insert(tk.END, ".\n2. Go to 'Your Authtoken' (or Getting Started).\n3. Copy the token.\n\nIt looks something like:\n2abcDEFghIJKlmNOpQRstuVWxyz1234567890")
                
                body_txt.tag_bind("link", "<Button-1>", lambda e: webbrowser.open_new(NGROK_DASHBOARD_URL))
                
            body_txt.config(state="disabled")
            
            if current_step[0] == 1:
                prev_btn.configure(state="disabled")
                next_btn.configure(state="normal")
            else:
                prev_btn.configure(state="normal")
                next_btn.configure(state="disabled")
                
        def do_prev():
            if current_step[0] > 1:
                current_step[0] -= 1
                render()
                
        def do_next():
            if current_step[0] < 2:
                current_step[0] += 1
                render()
                
        btn_frame = ttk.Frame(main_frame, padding="5")
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        prev_btn = ttk.Button(btn_frame, text="Previous", command=do_prev)
        prev_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        next_btn = ttk.Button(btn_frame, text="Next", command=do_next)
        next_btn.pack(side=tk.LEFT)
        
        close_btn = ttk.Button(btn_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        render()
        self.root.wait_window(dialog)

    def handle_finish(self):
        project_path = self.code_path_var.get().strip()
        if not project_path or project_path == "Not Configured":
            messagebox.showwarning("Warning", "Please configure the Code Server path (Already Installed or download it).")
            return
        self.finish_btn.configure(state="disabled")
            
        try:
            config.set("dir", project_path)
            if not config.get("DestinationFolder"):
                config.set("DestinationFolder", os.path.normpath(os.path.join(project_path, "test")))
            if not config.get("Userfolder"):
                config.set("Userfolder", os.path.normpath(os.path.join(project_path, "userdetails")))
            if not config.get("ratelimiter"):
                config.set("ratelimiter", os.path.normpath(os.path.join(project_path, "data")))
        except Exception:
            pass
            
        python_status = "already_installed"
        if self.python_install_var.get():
            python_status = "install"
        elif self.python_already_var.get():
            python_status = "already_installed"

        cloudflared_status = "already_installed"
        if self.cloudflared_install_var.get():
            cloudflared_status = "install"
        elif self.cloudflared_already_var.get():
            cloudflared_status = "already_installed"
            
        result = {
            "path": project_path,
            "python": python_status,
            "cloudflared": cloudflared_status,
            "ngrok": cloudflared_status,
            "python_action": python_status,
            "cloudflared_action": cloudflared_status,
            "ngrok_action": cloudflared_status
        }
        
        if sys.stdout is not None:
            try:
                print(f"#FEZ {json.dumps(result)}")
                sys.stdout.flush()
            except Exception:
                pass
        
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            config.set("setup_win_x", x)
            config.set("setup_win_y", y)
        except Exception:
            pass
            
        try:
            config.sync_to_server_config()
        except Exception:
            pass

        if self.on_complete:
            self.root.after(0, lambda: self.on_complete(result))
            return

        self.root.after(0, self.root.destroy)

    def on_close(self):
        if self.on_cancel:
            self.on_cancel()
        else:
            self.root.destroy()
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgramSetupApp(root)
    root.mainloop()
