import pyttsx3
import threading

def speak(text):
    print(f"DEBUG: Starting sound test for: {text}")
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()
    print("DEBUG: Done")