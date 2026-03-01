import customtkinter as ctk
import cv2
import os
from vision import StudyDetector
from ui_manager import StudyUI
from engine import StudyEngine
from modes import get_message

class StudyGuardianController:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Study Guardian Pro")
        
        self.engine = StudyEngine()
        self.detector = StudyDetector()
        
        self.running = False
        self.timer_seconds = 0
        self.current_session_mins = 0
        self.current_session_xp = 0
        
        self.partner_video_path = "static/partner.mp4"
        self.partner_cap = None
        
        self.ui = StudyUI(self.root, self)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.update_loop()

    def start_session(self, duration_mins, xp_reward):
        """Immediately starts everything when a time button is clicked"""
        self.running = True
        self.timer_seconds = duration_mins * 60
        self.current_session_mins = duration_mins
        self.current_session_xp = xp_reward
        
        if os.path.exists(self.partner_video_path):
            self.partner_cap = cv2.VideoCapture(self.partner_video_path)
        
        # Voice and cooldown reset
        self.engine.trigger_voice(f"Starting {duration_mins} minute session. Let's focus!")
        self.engine.last_voice_time = 0  # CRITICAL: Reset cooldown so first warning always fires
        
        self.run_countdown()

    def run_countdown(self):
        if self.running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            mins, secs = divmod(self.timer_seconds, 60)
            if self.ui.timer_label:
                self.ui.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.root.after(1000, self.run_countdown)
        elif self.timer_seconds <= 0:
            self.complete_session()  # Changed from stop_session to complete_session

    def update_loop(self):
        # 1. Get AI status from camera
        frame, status = self.detector.get_user_status()
        
        # 2. If session is active, let the engine process warnings
        if self.running:
            self.engine.handle_status(status, get_message)
            
            # Update Partner Video
            if self.partner_cap and self.partner_cap.isOpened():
                ret, p_frame = self.partner_cap.read()
                if not ret: 
                    self.partner_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, p_frame = self.partner_cap.read()
                if ret:
                    self.ui.update_frame(self.ui.partner_label, p_frame)

        # 3. Always show your own camera feed
        if frame is not None:
            self.ui.update_frame(self.ui.cam_label, frame)
        
        self.root.after(30, self.update_loop)

    def stop_session(self):
        """Stop session early (user clicked stop)"""
        self.running = False
        if self.partner_cap: 
            self.partner_cap.release()
        self.engine.trigger_voice("Session ended early. Try again next time!")
        self.ui.show_dashboard()

    def complete_session(self):
        """Timer hit 00:00 successfully - award XP"""
        if self.running:
            self.running = False
            if self.partner_cap:
                self.partner_cap.release()
            
            # Log the completed session to get XP
            self.engine.log_session(self.current_session_mins, self.current_session_xp)
            self.engine.trigger_voice("Congratulations! Session complete. Great job!")
            self.ui.show_dashboard()

    def on_close(self):
        self.running = False
        self.engine.save_data()
        self.detector.cleanup()
        if self.partner_cap:
            self.partner_cap.release()
        self.root.destroy()


if __name__ == "__main__":
    app = StudyGuardianController()
    app.root.mainloop()