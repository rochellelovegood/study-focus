import customtkinter as ctk
import cv2
from PIL import Image
from tkinter import messagebox

# Set styling
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green") 

class StudyUI:
    def __init__(self, root, controller):
        self.root = root
        self.ctrl = controller
        
        # Configure Window
        self.root.geometry("1200x850")
        self.root.title("Guardian AI - Study Focus")
        self.root.configure(fg_color=("#F2F2F7", "#1C1C1E")) 
        
        self.setup_layout()

    def setup_layout(self):
        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.logo = ctk.CTkLabel(self.sidebar, text="GUARDIAN AI", 
                                 font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.pack(pady=(40, 30))

        # --- Nav Buttons ---
        self.nav_btn("Dashboard", "🏠", self.show_dashboard)
        self.nav_btn("Task List", "📝", self.show_tasks)
        self.nav_btn("History", "📊", self.show_history)
        self.nav_btn("Sound Garden", "🎧", self.show_sounds)

        # Spacer to push switch and start button to bottom
        spacer = ctk.CTkLabel(self.sidebar, text="")
        spacer.pack(expand=True)

        # --- Mute Switch ---
        # Fixed: Using BooleanVar to prevent string mismatch issues
        self.mute_var = ctk.BooleanVar(value=True) # Start as True (Unmuted)
        self.mute_switch = ctk.CTkSwitch(self.sidebar, text="Mom Warnings", 
                                         variable=self.mute_var,
                                         command=self.update_mute_status)
        self.mute_switch.pack(pady=10, padx=20)
        
        # Initialize engine state to match switch
        self.update_mute_status()

        self.start_nav_btn = ctk.CTkButton(self.sidebar, text="🚀 START FOCUS", 
                                           font=ctk.CTkFont(weight="bold"),
                                           height=45, corner_radius=10,
                                           command=self.show_study_session)
        self.start_nav_btn.pack(pady=20, padx=20, fill="x")

        # 2. Main Content Area
        self.content_area = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_area.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        
        # UI State References
        self.cam_label = None 
        self.partner_label = None
        self.timer_label = None
        
        self.show_dashboard()

    def update_mute_status(self):
        """Connects the UI Switch to the Engine is_muted variable."""
        # Switch 'On' (True) means engine.is_muted = False
        # Switch 'Off' (False) means engine.is_muted = True
        is_active = self.mute_var.get()
        self.ctrl.engine.is_muted = not is_active
        state = "ACTIVE" if is_active else "MUTED"
        print(f"[UI] Asian Mom Warnings: {state}")

    def nav_btn(self, text, icon, command):
        btn = ctk.CTkButton(self.sidebar, text=f"{icon}  {text}", 
                            command=command, height=45,
                            fg_color="transparent", text_color=("gray10", "gray90"),
                            hover_color=("gray80", "gray25"), anchor="w")
        btn.pack(fill="x", padx=15, pady=2)

    def clear_content(self):
        self.cam_label = None
        self.partner_label = None
        self.timer_label = None
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- DASHBOARD ---
    def show_dashboard(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Morning, Scholar", 
                     font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(20, 5), padx=20, anchor="w")

        xp_card = ctk.CTkFrame(self.content_area, corner_radius=15)
        xp_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(xp_card, text=f"Level {self.ctrl.engine.level}", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 0), padx=20, anchor="w")
        
        # XP Calculation for the bar
        required_xp = 100 + (self.ctrl.engine.level - 1) * 20
        progress = self.ctrl.engine.xp / required_xp
        
        self.xp_bar = ctk.CTkProgressBar(xp_card, height=12, corner_radius=10)
        self.xp_bar.set(progress)
        self.xp_bar.pack(fill="x", padx=20, pady=15)

        stats_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10)
        self.create_stat_card(stats_frame, "Sessions Done", len(self.ctrl.engine.history))
        self.create_stat_card(stats_frame, "Focus Topic", self.ctrl.engine.active_task)

    def create_stat_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))

    # --- TASK LIST ---
    def show_tasks(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Study Tasks", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20, padx=20, anchor="w")

        input_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        self.task_entry = ctk.CTkEntry(input_frame, placeholder_text="What are we studying?", height=40)
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(input_frame, text="Add", width=80, command=self.add_task_ui).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self.content_area, corner_radius=15)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        for i, t in enumerate(self.ctrl.engine.tasks):
            row = ctk.CTkFrame(scroll, fg_color=("gray95", "gray20"), corner_radius=10)
            row.pack(fill="x", pady=5, padx=5)
            cb = ctk.CTkCheckBox(row, text=t['text'], command=lambda idx=i: self.ctrl.engine.toggle_task(idx))
            if t['done']: cb.select()
            cb.pack(side="left", padx=15, pady=12)
            ctk.CTkButton(row, text="Set Active", width=80, height=26, command=lambda n=t['text']: self.set_active_task(n)).pack(side="right", padx=10)

    def set_active_task(self, name):
        self.ctrl.engine.active_task = name
        messagebox.showinfo("Focus Set", f"Ready to study: {name}")

    def add_task_ui(self):
        if self.task_entry.get():
            self.ctrl.engine.add_task(self.task_entry.get())
            self.show_tasks()

    # --- STUDY SESSION ---
    def show_study_session(self):
        self.clear_content()
        self.timer_label = ctk.CTkLabel(self.content_area, text="00:00", 
                                        font=ctk.CTkFont(family="Consolas", size=80, weight="bold"))
        self.timer_label.pack(pady=10)

        video_box = ctk.CTkFrame(self.content_area, fg_color="transparent")
        video_box.pack(pady=10, fill="both", expand=True)

        # Left Cam
        left_box = ctk.CTkFrame(video_box, corner_radius=15, border_width=2, border_color="#27AE60")
        left_box.pack(side="left", expand=True, padx=10, fill="both")
        ctk.CTkLabel(left_box, text="AI GUARDIAN (YOU)", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.cam_label = ctk.CTkLabel(left_box, text="", width=400, height=300)
        self.cam_label.pack(padx=10, pady=10)

        # Right Partner
        right_box = ctk.CTkFrame(video_box, corner_radius=15, border_width=2, border_color="#3498DB")
        right_box.pack(side="left", expand=True, padx=10, fill="both")
        ctk.CTkLabel(right_box, text="STUDY PARTNER", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.partner_label = ctk.CTkLabel(right_box, text="", width=400, height=300)
        self.partner_label.pack(padx=10, pady=10)

        p_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        p_frame.pack(pady=20)
        for t, m, x in [("25m", 25, 50), ("30m", 30, 65), ("45m", 45, 100), ("1h", 60, 150)]:
            ctk.CTkButton(p_frame, text=t, width=70, corner_radius=15,
                          command=lambda mins=m, xp=x: self.ctrl.start_session(mins, xp)).pack(side="left", padx=5)

        ctk.CTkButton(self.content_area, text="QUIT", fg_color="#E74C3C", command=self.ctrl.stop_session).pack(pady=10)

    def show_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="History Logs", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20, padx=20, anchor="w")
        hist_scroll = ctk.CTkScrollableFrame(self.content_area, corner_radius=15)
        hist_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for entry in reversed(self.ctrl.engine.history):
            row = ctk.CTkFrame(hist_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=entry['date'], width=150).pack(side="left")
            ctk.CTkLabel(row, text=entry['task'], width=250, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"+{entry['xp']} XP", text_color="#27AE60").pack(side="left")

    def show_sounds(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Sound Garden", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20, padx=20, anchor="w")
        if self.ctrl.engine.level < 2:
            ctk.CTkLabel(self.content_area, text="🔒 Unlock at Level 2").pack(pady=50)
        else:
            ctk.CTkButton(self.content_area, text="Rain Lofi", command=lambda: self.ctrl.engine.play_lofi("rain")).pack(pady=10)

    def update_frame(self, label_widget, frame):
        if label_widget and label_widget.winfo_exists():
            try:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(400, 300))
                label_widget.configure(image=ctk_img)
                label_widget.image = ctk_img 
            except Exception as e:
                print(f"Frame update error: {e}")