import numpy as np

def estimate_volume(hand_box, food_box, hand_real_width_cm):
    """
    Estimer volumen baseret på håndens bredde i cm.
    """
    # pixels to cm
    hand_px = hand_box['xmax'] - hand_box['xmin']
    px_to_cm = hand_real_width_cm / hand_px

    w_px = food_box['xmax'] - food_box['xmin']
    h_px = food_box['ymax'] - food_box['ymin']
    w_cm, h_cm = w_px * px_to_cm, h_px * px_to_cm

    # Forenklet prisme-model (cm3 = ml)
    volume_ml = w_cm * w_cm * h_cm
    return volume_ml
