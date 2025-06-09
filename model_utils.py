import os
import numpy as np
from ultralytics import YOLO
from PIL import Image

# YOLOv8 general container detection
model_general = YOLO('yolov8n.pt')

# Custom food detection model
food_model_path = 'models/food_model.pt'
if os.path.exists(food_model_path):
    model_food = YOLO(food_model_path)
else:
    model_food = None
    print(f"[Warning] food_model.pt ikke fundet, mad-genkendelse deaktiveret.")

def detect_containers(img: Image.Image):
    """Return liste af container-detektioner (bowl, plate, cup)."""
    arr = np.array(img)
    res = model_general.predict(source=arr, verbose=False)[0]
    boxes = res.boxes.xyxy.cpu().numpy()
    confs = res.boxes.conf.cpu().numpy()
    classes = res.boxes.cls.cpu().numpy().astype(int)
    names = [res.names[c] for c in classes]
    dets = []
    for (x1, y1, x2, y2), conf, name in zip(boxes, confs, names):
        if name in ('bowl','plate','cup'):
            dets.append({
                'xmin': float(x1), 'ymin': float(y1),
                'xmax': float(x2), 'ymax': float(y2),
                'confidence': float(conf),
                'name': name
            })
    return dets

def detect_food_items(img: Image.Image, crop_boxes):
    """Recognize foods with custom model if available."""
    if model_food is None:
        return []
    foods = []
    for box in crop_boxes:
        crop = img.crop((box['xmin'], box['ymin'], box['xmax'], box['ymax']))
        res = model_food.predict(source=np.array(crop), verbose=False)[0]
        if res.boxes and len(res.boxes.cls) > 0:
            cls = int(res.boxes.cls.cpu().numpy()[0])
            foods.append(res.names[cls])
    return foods
