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

        # -------------------------
        # Voice System
        # -------------------------
        self.voice_queue = queue.Queue()
        self.voice_cooldown = 10
        self.last_voice_time = 0

        self.start_voice_worker()

        print("✅ StudyEngine Initialized")

    # --------------------------------
    # Voice Worker Thread
    # --------------------------------
    def start_voice_worker(self):

        def worker():

            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 170)
            except Exception as e:
                print("Voice engine failed:", e)
                return

            while True:

                message = self.voice_queue.get()

                if message is None:
                    break

                try:
                    engine.say(message)
                    engine.runAndWait()

                except Exception as e:
                    print("Voice error:", e)

                finally:
                    self.voice_queue.task_done()

        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------
    # Trigger Voice Safely
    # --------------------------------
    def trigger_voice(self, message):

        if self.is_muted:
            return

        if not message:
            return

        current_time = time.time()

        if current_time - self.last_voice_time > self.voice_cooldown:

            print("🔊 Speaking:", message)

            self.voice_queue.put(message)

            self.last_voice_time = current_time

    # --------------------------------
    # AI Status Logic
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

        # -------------------------
        # React only if status changed
        # -------------------------
        if problem != self.last_status:

            if problem != "focus":

                msg = message_func("asian_mom", problem)

                print(f"📢 WARNING: {problem} -> {msg}")

                self.trigger_voice(msg)

                self.xp = max(0, self.xp - 5)

            else:

                print("✅ User focused again")

            self.last_status = problem

        # -------------------------
        # Reward focus
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