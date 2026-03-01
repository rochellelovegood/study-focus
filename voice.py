import pyttsx3
import threading
import queue
import time

class VoiceManager:
    def __init__(self, cooldown=10):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)

        self.queue = queue.Queue()
        self.cooldown = cooldown
        self.last_spoken = 0

        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            text = self.queue.get()
            if text is None:
                break

            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("Voice error:", e)

            self.queue.task_done()

    def speak(self, text):
        now = time.time()

        if now - self.last_spoken >= self.cooldown:
            self.queue.put(text)
            self.last_spoken = now