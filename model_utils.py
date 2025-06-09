import os
import numpy as np
from ultralytics import YOLO
from PIL import Image

# YOLOv8 container detection
model_general = YOLO('yolov8n.pt')

# YOLO hand detection model
model_hand = YOLO('ultralytics/handtrack')

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

    # Hand detection via YOLO handtrack
    hand_res = model_hand.predict(source=img_array, verbose=False)[0]
    if len(hand_res.boxes) > 0:
        x1, y1, x2, y2 = hand_res.boxes.xyxy.cpu().numpy()[0]
        detections.append({
            'xmin': float(x1), 'ymin': float(y1),
            'xmax': float(x2), 'ymax': float(y2),
            'confidence': float(hand_res.boxes.conf.cpu().numpy()[0]),
            'class': int(hand_res.boxes.cls.cpu().numpy()[0]),
            'name': 'hand'
        })

    # Container detection via YOLO general
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
    """Genkend madvarer med finetunet model, hvis tilgængelig."""
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
