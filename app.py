from flask import Flask, render_template, Response
import cv2
import time
import threading
from modes import get_message
from voice import speak

app = Flask(__name__)

# Load Cascades globally
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

last_alert = 0

def gen_frames():
    global last_alert
    camera = cv2.VideoCapture(0)
    
    # Trackers
    face_lost_start = None
    eyes_lost_start = None

    while True:
        success, frame = camera.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        now = time.time()
        status = "focus"

        if len(faces) == 0:
            if face_lost_start is None: face_lost_start = now
            if (now - face_lost_start) > 2: status = "phone"
        else:
            face_lost_start = None
            for (x, y, w, h) in faces:
                # ROI for eyes
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
                
                if len(eyes) == 0:
                    if eyes_lost_start is None: eyes_lost_start = now
                    if (now - eyes_lost_start) > 3: status = "tired"
                else:
                    eyes_lost_start = None

        # Voice Trigger
        if (now - last_alert) > 10:
            speak(get_message("asian_mom", "YOU DUMB DUMB"))
            last_alert = now
            print("DEBUG: Alert triggered for status:", status)

        # Encode for web
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/test_voice')
def say_something():
    
    speak("Hello Khin Than Thar")

if __name__ == '__main__':
    print("🚀 Server starting at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)