import numpy as np

def estimate_volume(hand_px_width, box, hand_cm):
    px_to_cm = hand_cm / hand_px_width
    w_px = box['xmax'] - box['xmin']
    h_px = box['ymax'] - box['ymin']
    w_cm = w_px * px_to_cm
    h_cm = h_px * px_to_cm
    return w_cm * w_cm * h_cm
