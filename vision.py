import cv2
import numpy as np
import time

class StudyDetector:
    def __init__(self):
        # 1. Initialize Camera
        self.cap = cv2.VideoCapture(0)
        
        # 2. Load YOLOv4-tiny (Objects: Phone, Person)
        try:
            self.net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
            self.model = cv2.dnn_DetectionModel(self.net)
            self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)
            
            with open("coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"❌ YOLO Error: {e}. Check weights/cfg/names files.")

        # 3. Load Haar Cascades (Physiological: Face, Eyes)
        # These are built into OpenCV; no extra files needed
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        # 4. Fatigue Tracking Variables
        self.eyes_closed_counter = 0
        self.TIRED_THRESHOLD = 25  # Approx 1 second of closed eyes
        
    def get_user_status(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, "away"

        # --- STEP A: YOLO DETECTION (Phones & People) ---
        classes, scores, boxes = self.model.detect(frame, confThreshold=0.5, nmsThreshold=0.4)
        detected_labels = []
        
        for (classid, score, box) in zip(classes, scores, boxes):
            label = self.classes[classid]
            detected_labels.append(label)
            
            # Draw YOLO Bounding Boxes
            color = (0, 255, 0) if label == "person" else (0, 0, 255)
            cv2.rectangle(frame, box, color, 2)
            cv2.putText(frame, f"{label.upper()}", (box[0], box[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # --- STEP B: HAAR CASCADE (Tiredness Detection) ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        is_tired = False
        if len(faces) > 0:
            # We only analyze the first (main) face detected
            (x, y, w, h) = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            
            # Search for eyes ONLY inside the face area
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
            
            # Draw a small box for the face being monitored
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 1)

            if len(eyes) == 0:
                self.eyes_closed_counter += 1
                if self.eyes_closed_counter >= self.TIRED_THRESHOLD:
                    is_tired = True
            else:
                self.eyes_closed_counter = 0
                # Optional: Draw boxes around eyes for visual feedback
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 255, 255), 1)

        # --- STEP C: LOGIC PRIORITY ---
        person_count = detected_labels.count("person")
        
        if person_count == 0:
            status = "away"
        elif is_tired:
            status = "tired"
        elif "cell phone" in detected_labels:
            status = "phone"
        elif person_count > 1:
            status = "multiple_people"
        else:
            status = "focus"

        # Display Final Status on Frame
        cv2.putText(frame, f"AI STATUS: {status.upper()}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

        return frame, status

    def cleanup(self):
        self.cap.release()