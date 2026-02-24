import time
import json
import os
import pyttsx3
import threading
import queue


class StudyEngine:
    def __init__(self):
        # -------------------------
        # 1. State Management
        # -------------------------
        self.xp = 0
        self.level = 1
        self.tasks = []
        self.history = []
        self.active_task = "General Studies"

        # -------------------------
        # 2. Status & Warning Logic
        # -------------------------
        self.is_muted = False
        self.last_status = "focus"
        self.last_voice_time = 0
        self.voice_cooldown = 10  # seconds

        # XP timing control
        self.last_xp_time = time.time()
        self.xp_interval = 1  # gain XP every 1 second

        # Distraction streak tracking
        self.distraction_count = 0

        # -------------------------
        # 3. Voice Queue System
        # -------------------------
        self.voice_queue = queue.Queue()
        self.voice_thread = None
        self.start_voice_worker()

        # Load saved data
        self.load_data()

    # =============================
    # VOICE SYSTEM (Thread Safe)
    # =============================
    def start_voice_worker(self):
        """Creates a background thread to handle all speech safely."""

        def worker():
            engine = pyttsx3.init()
            while True:
                message = self.voice_queue.get()

                if message is None:  # Shutdown signal
                    break

                try:
                    engine.say(message)
                    engine.runAndWait()
                except Exception as e:
                    print(f"Speech Worker Error: {e}")
                finally:
                    self.voice_queue.task_done()

        self.voice_thread = threading.Thread(target=worker, daemon=True)
        self.voice_thread.start()

    def trigger_voice(self, message):
        """Queue voice message if not muted."""
        if not self.is_muted:
            self.voice_queue.put(message)

    def shutdown(self):
        """Gracefully stop voice thread."""
        self.voice_queue.put(None)
        self.voice_thread.join()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        return self.is_muted

    # =============================
    # STATUS HANDLING
    # =============================
    def handle_status(self, status, message_func=None):
        current_time = time.time()

        # 1. Normalize (YOLO uses 'cell phone')
        if status == "cell phone":
            status = "phone"

        distracted_states = ["phone", "away", "multiple_people", "tired"]
        is_distracted = status in distracted_states
        
        # 2. Logic: Trigger if NEW distraction OR if same distraction persists past cooldown
        # This ensures she yells immediately when she sees it, and every 10 seconds after.
        new_distraction = is_distracted and (status != self.last_status)
        cooldown_passed = is_distracted and (current_time - self.last_voice_time >= self.voice_cooldown)

        if new_distraction or cooldown_passed:
            # Streak tracking
            if status == self.last_status:
                self.distraction_count += 1
            else:
                self.distraction_count = 1 

            # Pick the message
            if status == "tired":
                msg = "WAKE UP! Sleep is for the weak!"
            elif self.distraction_count >= 3:
                msg = f"I HAVE TOLD YOU THREE TIMES! PUT THAT {status.upper()} AWAY!"
            else:
                if message_func:
                    msg = message_func("asian_mom", status)
                else:
                    msg = f"Stop being distracted by {status}!"

            # 3. THE TRIGGER (Check Mute)
            # Ensure your UI switch is actually changing self.is_muted to False
            print(f"[DEBUG] Status: {status} | Muted: {self.is_muted}") 
            
            if not self.is_muted:
                self.trigger_voice(msg)

            self.last_voice_time = current_time
            self.xp = max(0, self.xp - 5)
            self.last_status = status
            self.save_data()

        elif status == "focus":
            self.distraction_count = 0
            # XP gain logic
            if current_time - self.last_xp_time >= self.xp_interval:
                self.xp += 1
                self.last_xp_time = current_time
                self.check_level_up()
            self.last_status = "focus"
    # =============================
    # LEVEL SYSTEM
    # =============================
    def check_level_up(self):
        required_xp = 100 + (self.level - 1) * 20

        if self.xp >= required_xp:
            self.level += 1
            self.xp -= required_xp
            self.trigger_voice(f"Level up! You are now level {self.level}")
            self.save_data()

    # =============================
    # DATA STORAGE
    # =============================
    def save_data(self):
        data = {
            "xp": self.xp,
            "level": self.level,
            "tasks": self.tasks,
            "history": self.history,
        }

        try:
            with open("user_data.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print("Save error:", e)

    def load_data(self):
        if os.path.exists("user_data.json"):
            try:
                with open("user_data.json", "r") as f:
                    data = json.load(f)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.tasks = data.get("tasks", [])
                    self.history = data.get("history", [])
            except Exception as e:
                print("Load error:", e)


# =====================================
# OPTIONAL TEST RUN
# =====================================
if __name__ == "__main__":

    def dummy_message(character, status):
        return f"Hey! Stop using your {status}!"

    engine = StudyEngine()

    try:
        while True:
            status_input = input("Enter status (focus/phone/tired/away): ")
            engine.handle_status(status_input, dummy_message)

    except KeyboardInterrupt:
        print("Shutting down...")
        engine.shutdown()