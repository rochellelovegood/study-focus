import cv2
import numpy as np

class StudyDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        
        # 1. Load the AI Model
        try:
            self.net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
            self.model = cv2.dnn_DetectionModel(self.net)
            self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)
            
            with open("coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Error loading YOLO files: {e}")
            print("Ensure yolov4-tiny.weights, yolov4-tiny.cfg, and coco.names are in the folder.")

    def get_user_status(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, "away"

        # 2. Perform Detection
        # confThreshold=0.5 (50% certainty), nmsThreshold=0.4 (reduces overlapping boxes)
        classes, scores, boxes = self.model.detect(frame, confThreshold=0.5, nmsThreshold=0.4)

        detected_labels = []
        for (classid, score, box) in zip(classes, scores, boxes):
            label = self.classes[classid]
            detected_labels.append(label)
            
            # Draw Bounding Box for the UI
            color = (0, 255, 0) if label == "person" else (0, 0, 255)
            cv2.rectangle(frame, box, color, 2)
            cv2.putText(frame, f"{label.upper()}", (box[0], box[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 3. Logic for your Project requirements
        person_count = detected_labels.count("person")
        
        if person_count > 1:
            return frame, "multiple_people"
        elif "cell phone" in detected_labels:
            return frame, "phone"
        elif person_count == 1:
            return frame, "focus"
        else:
            return frame, "away"

    def cleanup(self):
        self.cap.release()