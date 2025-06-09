import numpy as np

def estimate_volume(hand_pixel_width, box, hand_real_cm):
    """Estimate volume given hand pixel width calibration and box."""
    px_to_cm = hand_real_cm / hand_pixel_width
    w_px = box['xmax'] - box['xmin']
    h_px = box['ymax'] - box['ymin']
    w_cm, h_cm = w_px * px_to_cm, h_px * px_to_cm
    # assume prisme: cm^3 = ml
    return w_cm * w_cm * h_cm
