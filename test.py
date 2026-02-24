import cv2
import os

files = ["yolov4-tiny.weights", "yolov4-tiny.cfg", "coco.names"]
for f in files:
    if os.path.exists(f):
        print(f"✅ {f} found!")
    else:
        print(f"❌ {f} is MISSING!")

# Try to load the network
try:
    net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
    print("🚀 YOLO loaded successfully!")
except Exception as e:
    print(f"🔥 Error: {e}")