import numpy as np
import cv2
from detector import detect_fruit


def make_color_frame_bgr(h, s=200, v=200, shape=(100, 100, 3)):
  
    hsv = np.zeros(shape, dtype=np.uint8)
    hsv[..., 0] = h
    hsv[..., 1] = s
    hsv[..., 2] = v
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr


def test_detect_banana():
    
    frame = make_color_frame_bgr(25)
    label, conf = detect_fruit(frame)
    assert label == 'banana'
    assert conf > 0


def test_detect_orange():
  
    frame = make_color_frame_bgr(10)
    label, conf = detect_fruit(frame)
    assert label == 'orange'
    assert conf > 0


def test_detect_apple():
    
    frame = make_color_frame_bgr(0)
    label, conf = detect_fruit(frame)
    assert label == 'apple'
    assert conf > 0
