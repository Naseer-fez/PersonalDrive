import os
import sys
import json
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from pckconfig import (
        config, CONFIG_TITLE, HELP_WEBSITE_URL,
        LBL_DIRECTORIES, LBL_LIMITS, LBL_SECURITY, LBL_RATE_LIMITER, LBL_NETWORK,
        DEFAULT_BANDWIDTH, DEFAULT_USER_SPACE, DEFAULT_JWT_MINUTES,
        DEFAULT_FREQUENCY, DEFAULT_RESET_SEC, DEFAULT_COOLDOWN_SEC,
        DEFAULT_FRONTEND_URL, DEFAULT_CORS_ORIGIN, DEFAULT_ALLOW_USERS, DEFAULT_RATE_LIMITER,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS,
        SERVER_CONFIG_FILE, CODE_CONFIG_SCRIPT, apply_google_light_theme
    )
except ImportError:
    from package.pckconfig import (
        config, CONFIG_TITLE, HELP_WEBSITE_URL,
        LBL_DIRECTORIES, LBL_LIMITS, LBL_SECURITY, LBL_RATE_LIMITER, LBL_NETWORK,
        DEFAULT_BANDWIDTH, DEFAULT_USER_SPACE, DEFAULT_JWT_MINUTES,
        DEFAULT_FREQUENCY, DEFAULT_RESET_SEC, DEFAULT_COOLDOWN_SEC,
        DEFAULT_FRONTEND_URL, DEFAULT_CORS_ORIGIN, DEFAULT_ALLOW_USERS, DEFAULT_RATE_LIMITER,
        DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS,
        SERVER_CONFIG_FILE, CODE_CONFIG_SCRIPT, apply_google_light_theme
    )

class ServerConfigApp:
    def __init__(self, root, on_complete=None, on_cancel=None):
        self.root = root
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.root.title(CONFIG_TITLE)
        self.root.geometry("620x720")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.style = ttk.Style()
        apply_google_light_theme(self.style, self.root)
        
        self.workspace_dir = os.path.normpath(config.get("dir") or os.getcwd())
        
        self.create_widgets()
        self.load_saved_data()
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        setup_x = config.get("setup_win_x")
        setup_y = config.get("setup_win_y")
        if setup_x is not None and setup_y is not None:
            x = setup_x
            y = setup_y
        else:
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_help_link(self, parent, title, text):
        lbl = ttk.Label(
            parent, 
            text="[?]", 
            foreground="#1a73e8", 
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        lbl.bind("<Button-1>", lambda e: messagebox.showinfo(title, text, parent=self.root))
        return lbl

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Directories Config
        dir_frame = ttk.LabelFrame(main_frame, text=LBL_DIRECTORIES, padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(dir_frame, text="Destination Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.dest_var = tk.StringVar()
        self.dest_entry = ttk.Entry(dir_frame, textvariable=self.dest_var, width=45)
        self.dest_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_dest).grid(row=0, column=2, pady=2)

        ttk.Label(dir_frame, text="User Details Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(dir_frame, textvariable=self.user_var, width=45)
        self.user_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_user).grid(row=1, column=2, pady=2)

        self.create_help_link(
            dir_frame,
            "Storage Directories Help",
            "Destination Folder:\nWhere uploaded files are stored.\n\nUser Details Folder:\nStores local user databases and profiles."
        ).grid(row=0, column=3, rowspan=2, padx=10, sticky=tk.N)

        # 1.5 System Paths Setup (Workspace, Python, Cloudflared, Ngrok Token) - DYNAMIC
        self.sys_setup_frame = ttk.LabelFrame(main_frame, text=" Workspace & System Setup ", padding="10")
        self.sys_setup_frame.pack(fill=tk.X, pady=(0, 10))
        
        sys_header_row = ttk.Frame(self.sys_setup_frame)
        sys_header_row.pack(fill=tk.X)
        
        self.show_sys_setup_var = tk.BooleanVar(value=False)
        self.sys_setup_check = ttk.Checkbutton(
            sys_header_row,
            text="Show Workspace & System Settings",
            variable=self.show_sys_setup_var,
            command=self.toggle_sys_setup
        )
        self.sys_setup_check.pack(side=tk.LEFT)
        
        self.create_help_link(
            sys_header_row,
            "Workspace & System Setup Help",
            "Workspace Folder:\nThe root folder where the server code and main configuration are stored.\n\nPython Executable:\nThe python interpreter path used to execute waitress/flask.\n\nCloudflared Tunnel Executable:\nThe path to cloudflared.exe for public url creation.\n\nNgrok Token:\nNgrok auth token for ngrok-tunnel fallback."
        ).pack(side=tk.LEFT, padx=10)
        
        self.sys_fields_frame = ttk.Frame(self.sys_setup_frame)
        
        # Grid layout for self.sys_fields_frame
        ttk.Label(self.sys_fields_frame, text="Workspace Path:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.workspace_var = tk.StringVar()
        self.workspace_entry = ttk.Entry(self.sys_fields_frame, textvariable=self.workspace_var, width=45)
        self.workspace_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(self.sys_fields_frame, text="Browse", command=self.on_workspace_browse).grid(row=0, column=2, pady=2)
        
        ttk.Label(self.sys_fields_frame, text="Python Executable:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.python_var = tk.StringVar()
        self.python_entry = ttk.Entry(self.sys_fields_frame, textvariable=self.python_var, width=45)
        self.python_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(self.sys_fields_frame, text="Browse", command=self.on_python_browse).grid(row=1, column=2, pady=2)
        
        ttk.Label(self.sys_fields_frame, text="Cloudflared Path:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cf_var = tk.StringVar()
        self.cf_entry = ttk.Entry(self.sys_fields_frame, textvariable=self.cf_var, width=45)
        self.cf_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(self.sys_fields_frame, text="Browse", command=self.on_cf_browse).grid(row=2, column=2, pady=2)
        
        ttk.Label(self.sys_fields_frame, text="Ngrok Auth Token:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ngrok_token_var = tk.StringVar()
        self.ngrok_token_entry = ttk.Entry(self.sys_fields_frame, textvariable=self.ngrok_token_var, width=45)
        self.ngrok_token_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky=tk.EW)

        # 2. Limits Config
        limits_frame = ttk.LabelFrame(main_frame, text=LBL_LIMITS, padding="10")
        limits_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(limits_frame, text="Bandwidth Limit (size):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.size_var = tk.IntVar()
        self.size_spin = ttk.Spinbox(limits_frame, from_=1, to=10000, textvariable=self.size_var, width=8)
        self.size_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(limits_frame, text="Space per User (basic):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.basic_var = tk.IntVar()
        self.basic_spin = ttk.Spinbox(limits_frame, from_=1, to=1000, textvariable=self.basic_var, width=8)
        self.basic_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        import webbrowser
        self.more_settings_btn = ttk.Button(limits_frame, text="More Settings...", command=self.show_more_settings)
        self.more_settings_btn.grid(row=0, column=4, padx=5, pady=2, sticky=tk.W)

        self.create_help_link(
            limits_frame,
            "Limits Help",
            "Bandwidth Limit (size):\nSets standard network transfer quota limits.\n\nSpace per User (basic):\nMax disk storage space (in GB) allocated per basic user account."
        ).grid(row=0, column=5, padx=10, sticky=tk.W)

        # 3. Security (Users)
        self.sec_frame = ttk.LabelFrame(main_frame, text=LBL_SECURITY, padding="10")
        self.sec_frame.pack(fill=tk.X, pady=(0, 10))

        sec_header_row = ttk.Frame(self.sec_frame)
        sec_header_row.pack(fill=tk.X)

        self.allow_users_var = tk.BooleanVar(value=DEFAULT_ALLOW_USERS)
        self.allow_users_check = ttk.Checkbutton(
            sec_header_row, 
            text="Allow Users", 
            variable=self.allow_users_var,
            command=self.toggle_allow_users_state
        )
        self.allow_users_check.pack(side=tk.LEFT)

        self.create_help_link(
            sec_header_row,
            "Security & Users Help",
            "Allow Users:\nEnables user authentication. If unchecked, the server restricts login access and registration.\n\nJWT Duration:\nThe period (in minutes) a logged-in user session remains valid before expiring, requiring them to sign in again."
        ).pack(side=tk.LEFT, padx=10)

        # Help website link button
        help_btn = ttk.Label(
            sec_header_row,
            text="Visit Website for Help",
            foreground="#1a73e8",
            cursor="hand2",
            font=("Segoe UI", 9, "underline")
        )
        help_btn.pack(side=tk.LEFT, padx=10)
        help_btn.bind("<Button-1>", lambda e: webbrowser.open_new(HELP_WEBSITE_URL))

        self.jwt_frame = ttk.Frame(self.sec_frame)
        ttk.Label(self.jwt_frame, text="JWT Expiration (minutes):").pack(side=tk.LEFT, pady=2)
        self.jwt_var = tk.IntVar()
        self.jwt_spin = ttk.Spinbox(self.jwt_frame, from_=1, to=1440, textvariable=self.jwt_var, width=10)
        self.jwt_spin.pack(side=tk.LEFT, padx=5, pady=2)

        # Brevo email configuration frame (shown when Allow Users is enabled)
        self.brevo_frame = ttk.Frame(self.sec_frame)
        ttk.Label(self.brevo_frame, text="Brevo API Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.brevo_api_entry = ttk.Entry(self.brevo_frame, width=45)
        self.brevo_api_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.brevo_frame, text="Sender Email:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sender_email_entry = ttk.Entry(self.brevo_frame, width=45)
        self.sender_email_entry.grid(row=1, column=1, padx=5, pady=2)
        self.create_help_link(
            self.brevo_frame,
            "Brevo Email Help",
            "Brevo API Key:\nAPI key from Brevo (formerly Sendinblue) for sending transactional emails.\nRequired for password recovery emails.\n\nSender Email:\nThe verified sender email address configured in your Brevo account."
        ).grid(row=0, column=2, rowspan=2, padx=10, sticky=tk.N)

        # 4. Rate Limiter Config
        self.rl_frame = ttk.LabelFrame(main_frame, text=LBL_RATE_LIMITER, padding="10")
        self.rl_frame.pack(fill=tk.X, pady=(0, 10))

        rl_header_row = ttk.Frame(self.rl_frame)
        rl_header_row.pack(fill=tk.X)

        self.rl_enable_var = tk.BooleanVar(value=DEFAULT_RATE_LIMITER)
        self.rl_check = ttk.Checkbutton(
            rl_header_row, 
            text="Enable Rate Limiter", 
            variable=self.rl_enable_var,
            command=self.toggle_rl_states
        )
        self.rl_check.pack(side=tk.LEFT)

        self.create_help_link(
            rl_header_row,
            "Rate Limiting Help",
            "Enable Rate Limiter:\nToggles request limit tracking to prevent server overload.\n\nDatabase Path:\nStores the limiter tracking logs database.\n\nRequest Frequency:\nMax request threshold permitted within the Reset Duration.\n\nReset / Cooldown Time:\nTiming thresholds (in seconds) defining the reset window and the temporary block duration."
        ).pack(side=tk.LEFT, padx=10)

        # Advanced toggle checkbox (shown beside enable checkbox when enabled)
        self.rl_adv_var = tk.BooleanVar(value=False)
        self.rl_adv_check = ttk.Checkbutton(
            rl_header_row,
            text="Show Advanced Settings",
            variable=self.rl_adv_var,
            command=self.toggle_rl_adv
        )

        self.rl_options_frame = ttk.Frame(self.rl_frame)
        
        path_row = ttk.Frame(self.rl_options_frame)
        path_row.pack(fill=tk.X, pady=2)
        ttk.Label(path_row, text="Limiter Database Path:").pack(side=tk.LEFT)
        self.rl_path_var = tk.StringVar()
        self.rl_path_entry = ttk.Entry(path_row, textvariable=self.rl_path_var, width=40)
        self.rl_path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.rl_path_btn = ttk.Button(path_row, text="Browse", command=self.browse_rl_path)
        self.rl_path_btn.pack(side=tk.RIGHT)

        grid_row = ttk.Frame(self.rl_options_frame)
        grid_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(grid_row, text="Frequency:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.freq_var = tk.IntVar()
        self.freq_spin = ttk.Spinbox(grid_row, from_=1, to=1000, textvariable=self.freq_var, width=8)
        self.freq_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(grid_row, text="Reset (sec):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.reset_var = tk.IntVar()
        self.reset_spin = ttk.Spinbox(grid_row, from_=1, to=86400, textvariable=self.reset_var, width=8)
        self.reset_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(grid_row, text="Cooldown (sec):").grid(row=0, column=4, sticky=tk.W, pady=2)
        self.cooldown_var = tk.IntVar()
        self.cooldown_spin = ttk.Spinbox(grid_row, from_=1, to=86400, textvariable=self.cooldown_var, width=8)
        self.cooldown_spin.grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)

        # 5. Network Links & Server Settings
        net_frame = ttk.LabelFrame(main_frame, text=LBL_NETWORK, padding="10")
        net_frame.pack(fill=tk.X, pady=(0, 15))

        # Grid container inside net_frame
        net_grid = ttk.Frame(net_frame)
        net_grid.pack(fill=tk.X)

        # Row 0: Central API Key
        ttk.Label(net_grid, text="Central API Key (api_key):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(net_grid, textvariable=self.api_key_var, width=45)
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=2)
        
        import webbrowser
        self.api_key_help = ttk.Label(
            net_grid,
            text="Get API Key",
            foreground="#1a73e8",
            cursor="hand2",
            font=("Segoe UI", 9, "underline")
        )
        self.api_key_help.grid(row=0, column=2, padx=10, sticky=tk.W)
        self.api_key_help.bind("<Button-1>", lambda e: webbrowser.open_new((self.url_var.get() or DEFAULT_FRONTEND_URL) + "/login"))

        self.create_help_link(
            net_grid,
            "Connections & URLs Help",
            "Central API Key (api_key):\nThe API key received from registering on the main server.\n\nFrontend Access Code (code):\nThe access code for users to login via the frontend.\n\nOptional Password (password):\nPassword required along with the access code.\n\nFrontend website URL (URL):\nThe link to your client web interface application (e.g. http://localhost:5173).\n\nCORS Header (FrontendURL):\nControls client request access permissions.\n\nServer Host:\nThe network interface the server binds to.\n\nServer Port:\nThe port number the server listens on.\n\nWorker Threads:\nNumber of concurrent request handler threads."
        ).grid(row=0, column=3, padx=10, sticky=tk.N)

        self.access_code_var = tk.StringVar()
        self.opt_password_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.cors_var = tk.StringVar()
        self.host_var = tk.StringVar()
        self.port_var = tk.IntVar()
        self.threads_var = tk.IntVar()

        # Advanced Settings Toggle
        self.show_adv_net_var = tk.BooleanVar(value=False)
        self.adv_net_check = ttk.Checkbutton(
            net_frame, 
            text="Show Advanced Connections Settings", 
            variable=self.show_adv_net_var,
            command=self.toggle_adv_net
        )
        self.adv_net_check.pack(anchor=tk.W, pady=(5, 0))

        # Advanced Settings Frame (grid layout for fields)
        self.adv_net_frame = ttk.Frame(net_frame, padding=(0, 5, 0, 0))
        
        ttk.Label(self.adv_net_frame, text="Frontend Access Code (code):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.access_code_entry = ttk.Entry(self.adv_net_frame, textvariable=self.access_code_var, width=45)
        self.access_code_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.adv_net_frame, text="Optional Password (password):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.opt_password_entry = ttk.Entry(self.adv_net_frame, textvariable=self.opt_password_var, width=45, show="●")
        self.opt_password_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self.adv_net_frame, text="Frontend website URL (URL):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.url_entry = ttk.Entry(self.adv_net_frame, textvariable=self.url_var, width=45)
        self.url_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(self.adv_net_frame, text="CORS Origin Header (FrontendURL):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.cors_entry = ttk.Entry(self.adv_net_frame, textvariable=self.cors_var, width=45)
        self.cors_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self.adv_net_frame, text="Server Host:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.host_entry = ttk.Entry(self.adv_net_frame, textvariable=self.host_var, width=45)
        self.host_entry.grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(self.adv_net_frame, text="Server Port:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.port_spin = ttk.Spinbox(self.adv_net_frame, from_=1, to=65535, textvariable=self.port_var, width=8)
        self.port_spin.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.adv_net_frame, text="Worker Threads:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.threads_spin = ttk.Spinbox(self.adv_net_frame, from_=1, to=64, textvariable=self.threads_var, width=8)
        self.threads_spin.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)

        # Actions Panel
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.cancel_btn = ttk.Button(action_frame, text="Cancel", command=self.on_close)
        self.cancel_btn.pack(side=tk.LEFT)

        self.finish_btn = ttk.Button(action_frame, text="Finish Configuration", command=self.handle_finish, style="Accent.TButton")
        self.finish_btn.pack(side=tk.RIGHT)

    def toggle_allow_users_state(self):
        if self.allow_users_var.get():
            self.jwt_frame.pack(fill=tk.X, pady=(5, 0), anchor=tk.W)
            self.brevo_frame.pack(fill=tk.X, pady=(5, 0), anchor=tk.W)
        else:
            self.jwt_frame.pack_forget()
            self.brevo_frame.pack_forget()
        self.auto_adjust_height()

    def toggle_rl_states(self):
        if self.rl_enable_var.get():
            self.rl_adv_check.pack(side=tk.LEFT, padx=10)
            self.toggle_rl_adv()
        else:
            self.rl_adv_check.pack_forget()
            self.rl_options_frame.pack_forget()
        self.auto_adjust_height()

    def toggle_rl_adv(self):
        if self.rl_enable_var.get() and self.rl_adv_var.get():
            self.rl_options_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.rl_options_frame.pack_forget()
        self.auto_adjust_height()

    def toggle_adv_net(self):
        if self.show_adv_net_var.get():
            self.adv_net_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.adv_net_frame.pack_forget()
        self.auto_adjust_height()

    def toggle_sys_setup(self):
        if self.show_sys_setup_var.get():
            self.sys_fields_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.sys_fields_frame.pack_forget()
        self.auto_adjust_height()

    def on_workspace_browse(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_var.get() or self.workspace_dir, title="Select Workspace Folder")
        if folder:
            normalized = os.path.normpath(folder)
            self.workspace_var.set(normalized)
            ans = messagebox.askyesno(
                "Update Storage Folders?",
                "Would you like to reset the Storage and Rate Limiter database directories to be inside this new workspace?",
                parent=self.root
            )
            if ans:
                self.dest_var.set(os.path.normpath(os.path.join(normalized, "test")))
                self.user_var.set(os.path.normpath(os.path.join(normalized, "userdetails")))
                self.rl_path_var.set(os.path.normpath(os.path.join(normalized, "data")))

    def on_python_browse(self):
        file = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.python_var.get()) if self.python_var.get() else None,
            title="Select Python Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file:
            self.python_var.set(os.path.normpath(file))

    def on_cf_browse(self):
        file = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.cf_var.get()) if self.cf_var.get() else None,
            title="Select Cloudflared/Ngrok Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file:
            self.cf_var.set(os.path.normpath(file))

    def auto_adjust_height(self):
        self.root.update_idletasks()
        self.root.geometry("")
        self.center_window()

    def load_saved_data(self):
        config_path = config.get("config_path", "")
        
        server_data = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    server_data = json.load(f)
            except Exception:
                pass
                
        self.dest_var.set(os.path.normpath(
            server_data.get("DestinationFolder") or 
            config.get("DestinationFolder") or 
            os.path.join(self.workspace_dir, "test")
        ))
        self.user_var.set(os.path.normpath(
            server_data.get("Userfolder") or 
            config.get("Userfolder") or 
            os.path.join(self.workspace_dir, "userdetails")
        ))
        
        self.size_var.set(server_data.get("size") or config.get("size", DEFAULT_BANDWIDTH))
        self.basic_var.set(server_data.get("basic") or config.get("basic", DEFAULT_USER_SPACE))
        
        allowusers_val = server_data.get("allowusers") if "allowusers" in server_data else server_data.get("Allowlogin")
        if allowusers_val is None:
            allowusers_val = config.get("allowusers") if config.get("allowusers") is not None else config.get("Allowlogin", DEFAULT_ALLOW_USERS)
        self.allow_users_var.set(allowusers_val)
        self.jwt_var.set(server_data.get("jwtduration") or config.get("jwtduration", DEFAULT_JWT_MINUTES))

        # Load Brevo email config from .env file if available
        brevo_api_val = config.get('EmailAPi', '')
        sender_email_val = config.get('sendemail', '')
        env_path = os.path.join(self.workspace_dir, '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line:
                            k, v = line.split('=', 1)
                            if k.strip() == 'EmailAPi':
                                brevo_api_val = v.strip()
                            elif k.strip() == 'sendemail':
                                sender_email_val = v.strip()
            except Exception:
                pass
        self.brevo_api_entry.delete(0, tk.END)
        self.brevo_api_entry.insert(0, brevo_api_val)
        self.sender_email_entry.delete(0, tk.END)
        self.sender_email_entry.insert(0, sender_email_val)

        # Load Workspace & Dependency Settings
        self.workspace_var.set(os.path.normpath(
            server_data.get("dir") or 
            config.get("dir") or 
            self.workspace_dir
        ))
        self.python_var.set(os.path.normpath(
            server_data.get("python") or 
            config.get("python") or 
            ""
        ))
        self.cf_var.set(os.path.normpath(
            server_data.get("cloudflared") or 
            config.get("cloudflared") or 
            server_data.get("ngrok") or 
            config.get("ngrok") or 
            ""
        ))
        self.ngrok_token_var.set(
            server_data.get("ngrok_token") or 
            config.get("ngrok_token") or 
            ""
        )
        self.toggle_sys_setup()

        self.toggle_allow_users_state()
        
        self.rl_enable_var.set(server_data.get("Ratelimiter") if "Ratelimiter" in server_data else config.get("Ratelimiter", DEFAULT_RATE_LIMITER))
        self.rl_path_var.set(os.path.normpath(
            server_data.get("ratelimiter") or 
            config.get("ratelimiter") or 
            os.path.join(self.workspace_dir, "data")
        ))
        self.freq_var.set(server_data.get("Allowfreq") or config.get("Allowfreq", DEFAULT_FREQUENCY))
        self.reset_var.set(server_data.get("resettime") or config.get("resettime", DEFAULT_RESET_SEC))
        self.cooldown_var.set(server_data.get("cooldowntime") or config.get("cooldowntime", DEFAULT_COOLDOWN_SEC))
        self.toggle_rl_states()
        
        self.api_key_var.set(server_data.get("api_key") or config.get("api_key", ""))
        self.access_code_var.set(server_data.get("access_code") or config.get("access_code", ""))
        self.opt_password_var.set(server_data.get("opt_password") or config.get("opt_password", ""))
        self.url_var.set(server_data.get("URL") or config.get("URL", DEFAULT_FRONTEND_URL))
        self.cors_var.set(server_data.get("FrontendURL") or config.get("FrontendURL", DEFAULT_CORS_ORIGIN))
        self.host_var.set(server_data.get("host") or config.get("host", DEFAULT_HOST))
        self.port_var.set(server_data.get("port") or config.get("port", DEFAULT_PORT))
        self.threads_var.set(server_data.get("threads") or config.get("threads", DEFAULT_THREADS))
        self.toggle_adv_net()
        self.auto_adjust_height()

    def browse_dest(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select Destination Folder")
        if folder:
            self.dest_var.set(os.path.normpath(folder))
            parent_dir = os.path.dirname(folder)
            self.user_var.set(os.path.normpath(os.path.join(parent_dir, "userdetails")))

    def browse_user(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select User Details Folder")
        if folder:
            self.user_var.set(os.path.normpath(folder))

    def browse_rl_path(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select Rate Limiter Database Folder")
        if folder:
            self.rl_path_var.set(os.path.normpath(folder))

    def update_config_py_path(self, config_py_path, target_config_json_path):
        if not os.path.exists(config_py_path):
            return False
            
        try:
            with open(config_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            pattern = r'((?:^\s*PATH|self\.path)\s*=\s*[\'"]).*?([\'"])'
            normalized_path = target_config_json_path.replace("\\", "/")
            replacement = rf'\g<1>{normalized_path}\g<2>'
            
            new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
            
            if count > 0:
                with open(config_py_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        except Exception as e:
            print(f"Error updating config.py path: {e}", file=sys.stderr)
            
        return False

    # ── Credential & Security Dialogs ──────────────────────
    def show_credential_dialog(self):
        """Show a dialog asking the user to create an initial account.
        Returns (username, email, password) or None if skipped."""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Account")
        dialog.geometry("480x340")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        dialog.configure(bg="#ffffff")
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (240)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (170)
        dialog.geometry(f"480x340+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="Create Your Account",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(
            main,
            text="Set up credentials for accessing your Personal Drive.\n"
                 "This account will be created when the server starts.",
            font=("Segoe UI", 9),
            foreground="gray",
            wraplength=420,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 15))
        
        fields = ttk.Frame(main)
        fields.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(fields, text="Username:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(fields, textvariable=username_var, width=35)
        username_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        ttk.Label(fields, text="Email:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(fields, textvariable=email_var, width=35)
        email_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        ttk.Label(fields, text="Password:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(fields, textvariable=password_var, width=35, show="●")
        password_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        # Show/hide password toggle
        show_pw_var = tk.BooleanVar(value=False)
        def toggle_pw():
            password_entry.config(show="" if show_pw_var.get() else "●")
        ttk.Checkbutton(fields, text="Show", variable=show_pw_var, command=toggle_pw).grid(
            row=2, column=2, padx=(5, 0), pady=5
        )
        
        fields.columnconfigure(1, weight=1)
        
        result = [None]
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def on_skip():
            result[0] = "SKIP"
            dialog.destroy()
        
        def on_create():
            u = username_var.get().strip()
            e = email_var.get().strip()
            p = password_var.get().strip()
            if not u or not p:
                messagebox.showwarning(
                    "Missing Fields", 
                    "Username and Password are required.",
                    parent=dialog
                )
                return
            result[0] = (u, e, p)
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Skip", command=on_skip).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Create Account", command=on_create, style="Accent.TButton").pack(side=tk.RIGHT)
        
        username_entry.focus_set()
        self.root.wait_window(dialog)
        return result[0]

    def show_security_warning(self):
        """Show a security warning when the user skips account creation.
        Returns True if user wants to continue anyway, False to go back."""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠ Security Warning")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        dialog.configure(bg="#ffffff")
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (250)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (175)
        dialog.geometry(f"500x350+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="⚠  Your Server Security Is at Risk",
            font=("Segoe UI", 13, "bold"),
            foreground="#cc6600"
        ).pack(anchor=tk.W, pady=(0, 12))
        
        warning_frame = ttk.Frame(main)
        warning_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        warning_text = tk.Text(
            warning_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            background=dialog.cget("background"),
            foreground="#202124",
            insertbackground="#202124",
            borderwidth=0,
            highlightthickness=0,
            height=10,
            cursor="arrow",
            padx=5, pady=5
        )
        warning_text.pack(fill=tk.BOTH, expand=True)
        
        reasons = (
            "Without user authentication, your server is vulnerable:\n\n"
            "🔓  Open Access — Anyone who discovers your server URL can "
            "upload, download, and delete files without restriction.\n\n"
            "👤  No Identity Tracking — There is no way to know who "
            "accessed, modified, or deleted your files.\n\n"
            "📂  Full Data Exposure — All files stored on the server "
            "are accessible to anyone on the network, including "
            "sensitive personal documents.\n\n"
            "🚫  No Revocation — Without accounts, you cannot block "
            "or revoke access for any specific user.\n\n"
            "It is strongly recommended to create at least one "
            "account to protect your data."
        )
        
        warning_text.insert("1.0", reasons)
        warning_text.config(state="disabled")
        
        result = [False]
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def go_back():
            result[0] = False
            dialog.destroy()
            
        def continue_anyway():
            result[0] = True
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Go Back (Recommended)", command=go_back, style="Accent.TButton").pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Continue Anyway", command=continue_anyway).pack(side=tk.RIGHT)
        
        self.root.wait_window(dialog)
        return result[0]

    # ── Finish Handler ─────────────────────────────────────
    def handle_finish(self):
        dest = self.dest_var.get().strip()
        user_dir = self.user_var.get().strip()
        rl_path = self.rl_path_var.get().strip()
        
        if not dest or not user_dir:
            messagebox.showerror("Error", "Please fill in all storage folder paths.")
            return
            
        if self.rl_enable_var.get() and not rl_path:
            messagebox.showerror("Error", "Please enter a rate-limiter database folder path.")
            return

        expanded_dest = os.path.expandvars(os.path.expanduser(dest))
        expanded_user = os.path.expandvars(os.path.expanduser(user_dir))
        
        for folder in (expanded_dest, expanded_user):
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory:\n{folder}\nError: {e}")
                    return

        if self.rl_enable_var.get():
            expanded_rl = os.path.expandvars(os.path.expanduser(rl_path))
            if not os.path.exists(expanded_rl):
                try:
                    os.makedirs(expanded_rl, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create rate limiter directory:\n{expanded_rl}\nError: {e}")
                    return
        else:
            expanded_rl = rl_path

        # Read Central API Key from Connections UI variable
        api_key = self.api_key_var.get().strip()

        if not api_key:
            api_key = self.show_api_key_dialog()
            if api_key is None:
                # User closed or cancelled dialog — stay on config page
                return
            self.api_key_var.set(api_key)

        if api_key:
            try:
                import winreg
                key_handle = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    "Environment",
                    0,
                    winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key_handle, "accesstooken", 0, winreg.REG_SZ, api_key)
                
                ngrok_tok = config.get("ngrok_token", "")
                if ngrok_tok:
                    winreg.SetValueEx(key_handle, "ngrokauth", 0, winreg.REG_SZ, ngrok_tok)
                    winreg.SetValueEx(key_handle, "NGROK_AUTHTOKEN", 0, winreg.REG_SZ, ngrok_tok)
                    winreg.SetValueEx(key_handle, "NGROK_API_KEY", 0, winreg.REG_SZ, ngrok_tok)
                    
                winreg.CloseKey(key_handle)
            except Exception as e:
                print(f"Warning: Failed to set winreg env variables: {e}", file=sys.stderr)

        # 1. Prepare server/project configuration properties
        server_data = {
            "DestinationFolder": expanded_dest,
            "Userfolder": expanded_user,
            "size": self.size_var.get(),
            "basic": self.basic_var.get(),
            "backend": "",
            "allowusers": self.allow_users_var.get(),
            "Allowlogin": self.allow_users_var.get(), # Legacy alias
            "api_key": api_key,
            "jwtduration": self.jwt_var.get(),
            "ratelimiter": expanded_rl,
            "FrontendURL": self.cors_var.get().strip() if hasattr(self, "cors_var") and self.cors_var.get() else "*",
            "URL": self.url_var.get().strip(),
            "Ratelimiter": self.rl_enable_var.get(),
            "Allowfreq": self.freq_var.get(),
            "resettime": self.reset_var.get(),
            "cooldowntime": self.cooldown_var.get(),
            "host": self.host_var.get().strip() if hasattr(self, "host_var") and self.host_var.get() else "0.0.0.0",
            "port": self.port_var.get() if hasattr(self, "port_var") and self.port_var.get() else 5000,
            "threads": self.threads_var.get() if hasattr(self, "threads_var") and self.threads_var.get() else 4,
            "initial_username": "",
            "initial_email": "",
            "initial_password": "",
            "access_code": self.access_code_var.get().strip() if hasattr(self, "access_code_var") else "",
            "opt_password": self.opt_password_var.get().strip() if hasattr(self, "opt_password_var") else ""
        }

        # 2. Retrieve setup/installer config properties from input fields
        package_data = {
            "dir": os.path.normpath(self.workspace_var.get().strip()),
            "workspace_path": os.path.normpath(self.workspace_var.get().strip()),
            "python": os.path.normpath(self.python_var.get().strip()),
            "cloudflared": os.path.normpath(self.cf_var.get().strip()),
            "ngrok": os.path.normpath(self.cf_var.get().strip()),
            "ngrok_token": self.ngrok_token_var.get().strip()
        }

        # 3. Create combined dictionary holding ALL settings together
        new_workspace = os.path.normpath(self.workspace_var.get().strip())
        config_json_path = os.path.normpath(os.path.join(new_workspace, SERVER_CONFIG_FILE))
        combined_config = {}
        combined_config.update(server_data)
        combined_config.update(package_data)
        combined_config["config_path"] = config_json_path

        # 4. Save combined settings directly to workspace config.json
        try:
            with open(config_json_path, 'w', encoding='utf-8') as f:
                json.dump(combined_config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save combined config file:\n{config_json_path}\nError: {e}")
            return

        # 5. Save combined settings directly to packageconfig.json
        try:
            config.set("config_path", config_json_path)
            # Remove window coordinates so they don't persist in files
            combined_config.pop("setup_win_x", None)
            combined_config.pop("setup_win_y", None)
            config.set("setup_win_x", None)
            config.set("setup_win_y", None)
            for k, v in combined_config.items():
                if v is not None:
                    config.set(k, v)
        except Exception as e:
            messagebox.showerror("Warning", f"Failed to save package config: {e}")

        # 6. Update PATH variable in pointed repository's config.py file
        config_py_path = os.path.join(new_workspace, CODE_CONFIG_SCRIPT)
        if os.path.exists(config_py_path):
            updated = self.update_config_py_path(config_py_path, config_json_path)
            if not updated:
                print(f"Warning: Could not update config.py variable in {config_py_path}", file=sys.stderr)
        else:
            print(f"Warning: {CODE_CONFIG_SCRIPT} not found in {new_workspace}", file=sys.stderr)

        # 7. Auto-fill the frontend URL via url.py
        try:
            try:
                from url import update_frontend_url
            except ImportError:
                from package.url import update_frontend_url
            update_frontend_url(new_workspace)
        except Exception as e:
            print(f"Warning: Failed to execute url.py to auto-fill frontend URL: {e}", file=sys.stderr)

        # Write Brevo credentials to .env file
        allow_users_value = self.allow_users_var.get()
        brevo_api = self.brevo_api_entry.get().strip()
        sender_email = self.sender_email_entry.get().strip()
        workspace_dir = new_workspace

        if allow_users_value:
            if not brevo_api or not sender_email:
                # Show warning but don't block
                import tkinter.messagebox as mb
                mb.showwarning(
                    "Email Configuration",
                    "Brevo API Key and Sender Email are not configured.\n"
                    "Password recovery via email will not work for users.\n\n"
                    "You can configure these later in the settings."
                )

            # Write to .env file in workspace
            env_path = os.path.join(workspace_dir, '.env')
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()

            # Update or append EmailAPi and sendemail
            updated_keys = set()
            new_lines = []
            for line in env_lines:
                key = line.split('=')[0].strip() if '=' in line else ''
                if key == 'EmailAPi':
                    new_lines.append(f'EmailAPi={brevo_api}\n')
                    updated_keys.add('EmailAPi')
                elif key == 'sendemail':
                    new_lines.append(f'sendemail={sender_email}\n')
                    updated_keys.add('sendemail')
                else:
                    new_lines.append(line)

            if 'EmailAPi' not in updated_keys:
                new_lines.append(f'EmailAPi={brevo_api}\n')
            if 'sendemail' not in updated_keys:
                new_lines.append(f'sendemail={sender_email}\n')

            with open(env_path, 'w') as f:
                f.writelines(new_lines)

        print(json.dumps(combined_config))
        sys.stdout.flush()
        
        if self.on_complete:
            self.on_complete(combined_config)
        else:
            self.root.destroy()
            sys.exit(0)

    def on_close(self):
        if self.on_cancel:
            self.on_cancel()
        else:
            self.root.destroy()
            sys.exit(0)

    def show_more_settings(self):
        """Show a dialog containing disk storage info and a bandwidth speed test."""
        dialog = tk.Toplevel(self.root)
        dialog.title("More Settings — System Diagnostics")
        dialog.geometry("520x460")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        dialog.configure(bg="#ffffff")
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (260)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (230)
        dialog.geometry(f"520x460+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="System Diagnostics & Limits",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # 1. Disk Storage Frame
        storage_frame = ttk.LabelFrame(main, text=" Storage & Available Disk Space ", padding="10")
        storage_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Get storage usage of the destination folder
        dest_path = self.dest_var.get().strip() or self.workspace_dir
        import shutil
        try:
            abs_path = os.path.abspath(dest_path)
            drive = os.path.splitdrive(abs_path)[0] or "/"
            total, used, free = shutil.disk_usage(drive)
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            free_gb = free / (1024 ** 3)
            pct_used = (used / total) * 100
            
            storage_lbl_text = f"Drive: {drive} | Total: {total_gb:.1f} GB | Used: {used_gb:.1f} GB | Free: {free_gb:.1f} GB"
        except Exception as e:
            pct_used = 0
            free_gb = 0
            storage_lbl_text = f"Could not retrieve drive info: {e}"
            
        ttk.Label(storage_frame, text=storage_lbl_text, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=2)
        
        # Storage progress bar
        progress = ttk.Progressbar(storage_frame, orient="horizontal", mode="determinate")
        progress.pack(fill=tk.X, pady=(5, 5))
        progress["value"] = pct_used
        
        # Auto-apply storage toggle
        self.apply_storage_var = tk.BooleanVar(value=True)
        
        def update_storage_limit():
            if self.apply_storage_var.get() and free_gb > 2:
                val = max(1, int(free_gb - 2))
                self.basic_var.set(val)
                
        self.apply_storage_check = ttk.Checkbutton(
            storage_frame, 
            text="Auto-apply available space to Space per User (Full minus 2 GB margin)", 
            variable=self.apply_storage_var,
            command=update_storage_limit
        )
        self.apply_storage_check.pack(anchor=tk.W, pady=(5, 0))
        
        # Initial apply if checked
        if self.apply_storage_var.get() and free_gb > 2:
            self.basic_var.set(max(1, int(free_gb - 2)))
        
        # 2. Bandwidth Speed Test Frame
        net_test_frame = ttk.LabelFrame(main, text=" Network Bandwidth Speed Test ", padding="10")
        net_test_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            net_test_frame, 
            text="Test your download speed by downloading a temporary 1MB file from Cloudflare:",
            wraplength=460, justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 10))
        
        status_lbl = ttk.Label(net_test_frame, text="Ready to test.", font=("Segoe UI", 9, "italic"))
        status_lbl.pack(anchor=tk.W, pady=5)
        
        # Auto-apply toggle
        self.apply_speed_var = tk.BooleanVar(value=True)
        self.apply_speed_check = ttk.Checkbutton(
            net_test_frame, 
            text="Auto-apply speed test result to Bandwidth Limit", 
            variable=self.apply_speed_var
        )
        self.apply_speed_check.pack(anchor=tk.W, pady=(5, 5))
        
        def run_test():
            status_lbl.config(text="Testing download speed... please wait.", foreground="#1a73e8")
            test_btn.config(state="disabled")
            
            def thread_func():
                import urllib.request
                import time
                url = "https://speed.cloudflare.com/__down?bytes=1048576"  # 1MB
                start = time.time()
                try:
                    req = urllib.request.Request(
                        url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req, timeout=12) as r:
                        content = r.read()
                    elapsed = time.time() - start
                    if elapsed <= 0:
                        elapsed = 0.001
                    size_mbits = (len(content) * 8) / 1000000.0
                    speed_mbps = size_mbits / elapsed
                    
                    if speed_mbps >= 100:
                        desc = "Very Fast"
                    elif speed_mbps >= 20:
                        desc = "Fast"
                    elif speed_mbps >= 5:
                        desc = "Moderate"
                    else:
                        desc = "Slow"
                    
                    speed_val = max(1, int(speed_mbps))
                    result_text = f"Download Speed: {speed_mbps:.2f} Mbps ({desc})"
                    dialog.after(0, lambda: status_lbl.config(text=result_text, foreground="#1e8e3e"))
                    
                    if self.apply_speed_var.get():
                        dialog.after(0, lambda: self.size_var.set(speed_val))
                except Exception as ex:
                    dialog.after(0, lambda: status_lbl.config(text=f"Speed test failed: {ex}", foreground="#d93025"))
                finally:
                    dialog.after(0, lambda: test_btn.config(state="normal"))
            
            import threading
            threading.Thread(target=thread_func, daemon=True).start()
            
        test_btn = ttk.Button(net_test_frame, text="Test Download Speed", command=run_test)
        test_btn.pack(anchor=tk.W, pady=2)
        
        # Close Button
        close_btn = ttk.Button(main, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

    def show_api_key_dialog(self):
        """Show a dialog prompting the user to enter the Central Server API Key."""
        import webbrowser
        dialog = tk.Toplevel(self.root)
        dialog.title("Central Server API Key")
        dialog.geometry("450x260")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        dialog.configure(bg="#ffffff")
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (225)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (130)
        dialog.geometry(f"450x260+{x}+{y}")
        
        main = ttk.Frame(dialog, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main,
            text="Enter Central Server API Key",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(
            main,
            text="Please enter your API key provided by the central server.\n"
                 "If you do not have an API key, visit our website to get one.",
            font=("Segoe UI", 9),
            foreground="gray",
            wraplength=410,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 15))
        
        fields = ttk.Frame(main)
        fields.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(fields, text="API Key:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        api_var = tk.StringVar(value=config.get("api_key", ""))
        api_entry = ttk.Entry(fields, textvariable=api_var, width=32)
        api_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        
        # Help link inside API key dialog
        help_link = ttk.Label(
            fields,
            text="Get API Key",
            foreground="#1a73e8",
            cursor="hand2",
            font=("Segoe UI", 9, "underline")
        )
        help_link.grid(row=0, column=2, padx=(10, 0), pady=5)
        frontend_login_url = (config.get("URL") or DEFAULT_FRONTEND_URL) + "/login"
        help_link.bind("<Button-1>", lambda e: webbrowser.open_new(frontend_login_url))
        
        fields.columnconfigure(1, weight=1)
        
        result = [None]
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        def on_skip():
            result[0] = ""
            dialog.destroy()
            
        def on_save():
            result[0] = api_var.get().strip()
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Skip", command=on_skip).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Save & Finish", command=on_save, style="Accent.TButton").pack(side=tk.RIGHT)
        
        api_entry.focus_set()
        self.root.wait_window(dialog)
        return result[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerConfigApp(root)
    root.mainloop()
