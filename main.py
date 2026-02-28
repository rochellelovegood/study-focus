import customtkinter as ctk
import cv2
import os
from vision import StudyDetector
from ui_manager import StudyUI
from engine import StudyEngine
from modes import get_message
from voice import speak

class StudyGuardianController:
    def __init__(self):
        # 1. Initialize CustomTkinter Window
        self.root = ctk.CTk()
        self.root.title("Study Guardian Pro")
        
        # 2. Logic Engines
        self.engine = StudyEngine()
        self.detector = StudyDetector()
        
        # 3. Session State
        self.running = False
        self.timer_seconds = 0
        self.current_session_mins = 0
        self.current_session_xp = 0
        
        # 4. Study Partner Video Logic
        self.partner_video_path = "static/partner.mp4"
        self.partner_cap = None
        
        # 5. Initialize UI
        self.ui = StudyUI(self.root, self)
        
        # 6. Safety & Cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 7. Start AI & Video Update Loop
        self.update_loop()
        speak("Hello Khin Than Thar")

    def start_session(self, duration_mins, xp_reward):
        """Triggered by duration buttons (25m, 30m, etc.)"""
        if not self.running:
            # Prepare Partner Video
            if os.path.exists(self.partner_video_path):
                self.partner_cap = cv2.VideoCapture(self.partner_video_path)
            
            self.running = True
            self.current_session_mins = duration_mins
            self.current_session_xp = xp_reward
            self.timer_seconds = duration_mins * 60
            
            # Start Voice Notification
            self.engine.trigger_voice(f"Session started for {duration_mins} minutes on {self.engine.active_task}")
            
            # Start Countdown Clock
            self.run_countdown()

    def run_countdown(self):
        """Ticks every 1 second for the Pomodoro clock."""
        if self.running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            
            # Update UI Label
            mins, secs = divmod(self.timer_seconds, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            if self.ui.timer_label and self.ui.timer_label.winfo_exists():
                self.ui.timer_label.configure(text=time_str)
            
            self.root.after(1000, self.run_countdown)
            
        elif self.running and self.timer_seconds <= 0:
            self.complete_session()

    def stop_session(self):
        """User manual quit."""
        if self.running:
            self.running = False
            if self.partner_cap:
                self.partner_cap.release()
            self.engine.trigger_voice("Session cancelled.")
            self.ui.show_dashboard()

    def complete_session(self):
        """Timer hit 00:00 successfully."""
        if self.running:
            self.running = False
            if self.partner_cap:
                self.partner_cap.release()
            
            # Log to History and Add XP
            self.engine.log_session(self.current_session_mins, self.current_session_xp)
            self.engine.trigger_voice("Congratulations! Study session complete.")
            self.ui.show_dashboard()

    def update_loop(self):
        """Fast Heartbeat (30ms) for AI Camera and Partner Video."""
        # A. Get AI Detector Frame
        frame, status = self.detector.get_user_status()
        
        if self.running:
            # Handle AI Penalties/Rewards
            self.engine.handle_status(status, get_message)
            
            # B. Update Partner Video Frame
            if self.partner_cap and self.partner_cap.isOpened():
                ret, p_frame = self.partner_cap.read()
                
                # If video ends, loop it back to the start
                if not ret:
                    self.partner_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, p_frame = self.partner_cap.read()
                
                if ret and self.ui.partner_label and self.ui.partner_label.winfo_exists():
                    self.ui.update_frame(self.ui.partner_label, p_frame)

        # C. Update Your Camera Frame
        if frame is not None and self.ui.cam_label and self.ui.cam_label.winfo_exists():
            self.ui.update_frame(self.ui.cam_label, frame)
        
        # Schedule next update
        self.root.after(30, self.update_loop)

    def on_close(self):
        """Saves data and kills all camera processes."""
        self.running = False
        self.engine.save_data()
        self.detector.cleanup()
        if self.partner_cap:
            self.partner_cap.release()
        self.root.destroy()

if __name__ == "__main__":
    app = StudyGuardianController()
    app.root.mainloop()