import os
import numpy as np
from ultralytics import YOLO
from PIL import Image
import mediapipe as mp

# YOLOv8 general detection
model_general = YOLO('yolov8n.pt')

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(static_image_mode=True,
                                max_num_hands=1,
                                min_detection_confidence=0.5)

# Custom food detection model
food_model_path = 'models/food_model.pt'
if os.path.exists(food_model_path):
    model_food = YOLO(food_model_path)
else:
    model_food = None
    print(f"[Warning] Mad-model ikke fundet på {food_model_path}. Mad-genkendelse deaktiveret.")

def detect_objects(img: Image.Image):
    """Detekter hånd og beholdere, returnerer liste af dicts."""
    img_array = np.array(img)
    detections = []

    # Hand detection via MediaPipe
    results = hands_detector.process(img_array)
    if results.multi_hand_landmarks:
        h, w, _ = img_array.shape
        xs = [lm.x * w for lm in results.multi_hand_landmarks[0].landmark]
        ys = [lm.y * h for lm in results.multi_hand_landmarks[0].landmark]
        x_min, x_max = max(min(xs) - 10, 0), min(max(xs) + 10, w)
        y_min, y_max = max(min(ys) - 10, 0), min(max(ys) + 10, h)
        detections.append({
            'xmin': float(x_min), 'ymin': float(y_min),
            'xmax': float(x_max), 'ymax': float(y_max),
            'confidence': 1.0,
            'class': -1,
            'name': 'hand'
        })

    # Container detection via YOLO
    yolo_res = model_general.predict(source=img_array, verbose=False)[0]
    boxes = yolo_res.boxes.xyxy.cpu().numpy()
    confs = yolo_res.boxes.conf.cpu().numpy()
    classes = yolo_res.boxes.cls.cpu().numpy().astype(int)
    names = [yolo_res.names[c] for c in classes]
    for (x1, y1, x2, y2), conf, cls, name in zip(boxes, confs, classes, names):
        if name in ['bowl', 'cup', 'plate']:
            detections.append({
                'xmin': float(x1), 'ymin': float(y1),
                'xmax': float(x2), 'ymax': float(y2),
                'confidence': float(conf),
                'class': int(cls),
                'name': name
            })

    return detections

def detect_food_items(img: Image.Image, crop_boxes):
    """Genkend madvarer med det finetunede model, hvis tilgængelig."""
    if model_food is None:
        return []
    foods = []
    for box in crop_boxes:
        crop = img.crop((box['xmin'], box['ymin'], box['xmax'], box['ymax']))
        res = model_food.predict(source=np.array(crop), verbose=False)[0]
        if res.boxes and len(res.boxes.cls) > 0:
            cls = int(res.boxes.cls.cpu().numpy()[0])
            name = res.names[cls]
            foods.append(name)
    return foods
