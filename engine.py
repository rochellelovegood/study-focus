import time
import pyttsx3
import threading
import queue

class StudyEngine:
    def __init__(self):
        # 1. Basic Stats
        self.xp = 0
        self.level = 1
        self.history = []
        self.is_muted = False
        
        # 2. Task Management (Matches your UI)
        self.tasks = [
            {'text': 'Python coding', 'done': False},
            {'text': 'General Studies', 'done': False}
        ]
        self.active_task = "General Studies"
        
        # 3. Logic Control
        self.last_status = "focus"
        self.last_voice_time = 0
        self.voice_cooldown = 10 
        
        # 4. Voice System
        self.voice_queue = queue.Queue()
        self.start_voice_worker()
        
        print("✅ StudyEngine Initialized")

    def start_voice_worker(self):
        def worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 170)
            except: return
            while True:
                msg = self.voice_queue.get()
                if msg is None: break
                try:
                    engine.stop()
                    engine.say(msg)
                    engine.runAndWait()
                except: pass
                finally: self.voice_queue.task_done()
        threading.Thread(target=worker, daemon=True).start()

    def trigger_voice(self, message):
        if not self.is_muted and message:
            self.voice_queue.put(message)

    # --- THIS WAS THE MISSING METHOD ---
    def handle_status(self, raw_status, message_func):
        current_time = time.time()
        status = str(raw_status).lower().strip()

        # 1. Map the AI status to our problem types
        if "phone" in status or "cell" in status:
            current_problem = "phone"
        elif "person" in status and status.count("person") > 1 or "multiple" in status:
            current_problem = "multiple_people"
        elif "away" in status or "no person" in status:
            current_problem = "away"
        else:
            current_problem = "focus"

        # 2. Trigger Logic
        if current_problem != "focus":
            # Check if enough time has passed (Cooldown)
            time_since_last = current_time - self.last_voice_time
            
            if current_problem != self.last_status or time_since_last > self.voice_cooldown:
                # GET THE MESSAGE
                msg = message_func("asian_mom", current_problem)
                
                # DEBUG PRINT: This tells us if the logic reached the "Yell" stage
                print(f"📢 LOGIC MATCH: {current_problem} | MSG: {msg} | Cooldown: {time_since_last:.1f}s")
                
                if msg:
                    self.trigger_voice(msg)
                    self.last_voice_time = current_time
                    self.last_status = current_problem
                    self.xp = max(0, self.xp - 5)
                else:
                    print("⚠️ ERROR: get_message returned NOTHING!")
        else:
            # Gain XP for focus
            if current_time - self.last_voice_time > 1:
                self.xp += 1
                self.last_status = "focus"

    def add_task(self, task_text):
        if task_text:
            self.tasks.append({'text': task_text, 'done': False})

    def toggle_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]['done'] = not self.tasks[index]['done']

    def log_session(self, mins, xp):
        session_data = {"date": time.strftime("%Y-%m-%d"), "task": self.active_task, "xp": xp}
        self.history.append(session_data)
        self.xp += xp

    # --- THIS WAS THE OTHER MISSING METHOD ---
    def save_data(self):
        """Saves current progress. You can add JSON saving here later."""
        print(f"💾 Data Saved. Current XP: {self.xp}")