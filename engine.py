import time
import pyttsx3
import threading
import queue


class StudyEngine:

    def __init__(self):

        # -------------------------
        # Basic Progress Stats
        # -------------------------
        self.xp = 0
        self.level = 1
        self.history = []
        self.is_muted = False

        # -------------------------
        # Task Management
        # -------------------------
        self.tasks = [
            {"text": "Python coding", "done": False},
            {"text": "General Studies", "done": False},
        ]

        self.active_task = "General Studies"

        # -------------------------
        # AI Status Tracking
        # -------------------------
        self.last_status = "focus"
        self.last_warning_time = 0  # Track when last warning was sent
        self.MIN_WARNING_INTERVAL = 30  # Minimum seconds between warnings

        # -------------------------
        # Voice System
        # -------------------------
        self.voice_queue = queue.Queue()
        self.voice_cooldown = 10
        self.last_voice_time = 0

        self.start_voice_worker()

        print("✅ StudyEngine Initialized")
        print("[UI] Asian Mom Warnings: ACTIVE")

    # --------------------------------
    # Voice Worker Thread (RESOLVED)
    # --------------------------------
    def start_voice_worker(self):

        def worker():
            print("🔊 Voice Worker Started")
            while True:
                msg = self.voice_queue.get()
                if msg is None: 
                    break
                
                try:
                    # Initialize engine for each message to avoid driver issues
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 170)
                    print(f"🎙️ Engine Speaking: {msg}")
                    engine.say(msg)
                    engine.runAndWait()
                    engine.stop()  # CRITICAL: Release the audio driver
                except Exception as e:
                    print(f"❌ Voice Output Error: {e}")
                finally:
                    self.voice_queue.task_done()

        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------
    # Trigger Voice Safely (RESOLVED)
    # --------------------------------
    def trigger_voice(self, message):

        if self.is_muted or not message:
            return

        current_time = time.time()

        if current_time - self.last_voice_time > self.voice_cooldown:
            print(f"🔊 Speaking: {message}")
            print(f"⬇️ Adding to Voice Queue: {message}")
            self.voice_queue.put(message)
            self.last_voice_time = current_time

    # --------------------------------
    # AI Status Logic (FIXED VERSION)
    # --------------------------------
    def handle_status(self, raw_status, message_func):

        status = str(raw_status).lower().strip()

        # -------------------------
        # Map detector output
        # -------------------------
        if "phone" in status or "cell" in status:
            problem = "phone"

        elif "multiple" in status or status.count("person") > 1:
            problem = "multiple_people"

        elif "away" in status or "no person" in status:
            problem = "away"

        elif "distract" in status or "looking away" in status:
            problem = "away"

        else:
            problem = "focus"

        current_time = time.time()

        # -------------------------
        # Check if status changed OR if we need to warn again (with cooldown)
        # -------------------------
        if problem != self.last_status:
            
            # Status changed
            if problem != "focus":
                # User just went away - warn them
                msg = message_func("asian_mom", problem)
                print(f"📢 WARNING: {problem} -> {msg}")
                self.trigger_voice(msg)
                self.xp = max(0, self.xp - 5)
                self.last_warning_time = current_time
            else:
                # User came back
                print("✅ User focused again")

            self.last_status = problem

        elif problem != "focus":
            # Status hasn't changed (still away), but check if we should warn again
            if current_time - self.last_warning_time > self.MIN_WARNING_INTERVAL:
                msg = message_func("asian_mom", problem)
                print(f"📢 WARNING (reminder): {problem} -> {msg}")
                self.trigger_voice(msg)
                self.xp = max(0, self.xp - 5)
                self.last_warning_time = current_time

        # -------------------------
        # Reward focus (always, even if status hasn't changed)
        # -------------------------
        if problem == "focus":
            self.xp += 1

    # --------------------------------
    # Task Functions
    # --------------------------------
    def add_task(self, task_text):

        if task_text:
            self.tasks.append({"text": task_text, "done": False})

    def toggle_task(self, index):

        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = not self.tasks[index]["done"]

    # --------------------------------
    # Log Completed Session
    # --------------------------------
    def log_session(self, mins, xp):

        session_data = {
            "date": time.strftime("%Y-%m-%d"),
            "task": self.active_task,
            "xp": xp,
        }

        self.history.append(session_data)

        self.xp += xp

    # --------------------------------
    # Save Data
    # --------------------------------
    def save_data(self):

        print(f"💾 Data Saved. Current XP: {self.xp}")