import os
import numpy as np
from ultralytics import YOLO
from PIL import Image
import torch
import torchvision.transforms as T
from torchvision.models import resnet50

# YOLO til beholdere
model_general = YOLO('yolov8n.pt')

# Food-model (YOLO fintuning)
food_model_path = 'models/food_model.pt'
if os.path.exists(food_model_path):
    model_food = YOLO(food_model_path)
else:
    model_food = None

# ResNet50 Food101 fallback
food101_weights = 'models/food101_resnet50.pth'
if os.path.exists(food101_weights):
    # Opbyg modelarkitektur
    food101 = resnet50(num_classes=101)
    state = torch.load(food101_weights, map_location='cpu')
    # Nogle checkpoints er gemt som {'model':state_dict}
    sd = state.get('model', state)
    food101.load_state_dict(sd)
    food101.eval()
    # Klasselisten for Food101 (101 klasser)
    FOOD101_CLASSES = [...]  # udfyld med listen af Food101-kategorienavne i korrekt rækkefølge
    # Transform til input
    tfm = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    ])
else:
    food101 = None

def detect_containers(img: Image.Image):
    arr = np.array(img)
    res = model_general.predict(source=arr, verbose=False)[0]
    boxes = res.boxes.xyxy.cpu().numpy()
    confs = res.boxes.conf.cpu().numpy()
    names = [res.names[int(c)] for c in res.boxes.cls.cpu().numpy()]
    dets = []
    for (x1, y1, x2, y2), conf, name in zip(boxes, confs, names):
        if name in ('bowl','plate','cup'):
            dets.append({'xmin': float(x1),'ymin': float(y1),
                         'xmax': float(x2),'ymax': float(y2),
                         'confidence': float(conf),'name': name})
    return dets

def detect_food_items(img: Image.Image, crop_boxes):
    foods = []
    # 1) Prøv YOLO mad-model
    if model_food is not None:
        arr = np.array(img)
        for box in crop_boxes:
            crop = img.crop((box['xmin'], box['ymin'], box['xmax'], box['ymax']))
            res = model_food.predict(source=np.array(crop), verbose=False)[0]
            for i, conf in enumerate(res.boxes.conf.cpu().numpy()):
                name = res.names[int(res.boxes.cls.cpu().numpy()[i])]
                foods.append({'name': name, 'confidence': float(conf)})
        if foods:
            return foods

    # 2) Fallback: ResNet50 Food101
    if food101 is not None:
        for box in crop_boxes:
            crop = img.crop((box['xmin'], box['ymin'], box['xmax'], box['ymax']))
            x = tfm(crop).unsqueeze(0)  # batch
            with torch.no_grad():
                logits = food101(x)
                probs = torch.softmax(logits, dim=1)[0]
                top1 = torch.argmax(probs).item()
                foods.append({
                    'name': FOOD101_CLASSES[top1],
                    'confidence': float(probs[top1].cpu().item())
                })
    return foods
