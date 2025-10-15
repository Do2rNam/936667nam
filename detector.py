import cv2
import numpy as np


def detect_fruit(frame, return_bbox=False):
    """Return (label, confidence) where label is one of 'banana','apple','orange' or None.
    If return_bbox=True, also return (x,y,w,h) of the largest colored region for the chosen label or None.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask_y = cv2.inRange(hsv, lower_yellow, upper_yellow)
    yellow_pct = np.count_nonzero(mask_y) / (mask_y.size)

   
    lower_orange = np.array([5, 120, 120])
    upper_orange = np.array([20, 255, 255])
    mask_o = cv2.inRange(hsv, lower_orange, upper_orange)
    orange_pct = np.count_nonzero(mask_o) / (mask_o.size)


    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask_r1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_r2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_r = cv2.bitwise_or(mask_r1, mask_r2)
    red_pct = np.count_nonzero(mask_r) / (mask_r.size)


    scores = {'banana': yellow_pct, 'orange': orange_pct, 'apple': red_pct}
    label, score = max(scores.items(), key=lambda kv: kv[1])

    conf = float(score * 100)
    if score < 0.002:
        if return_bbox:
            return (None, 0.0, None)
        return (None, 0.0)

    if not return_bbox:
        return (label, conf)

    # choose mask corresponding to label to compute bounding box
    mask = None
    if label == 'banana':
        mask = mask_y
    elif label == 'orange':
        mask = mask_o
    elif label == 'apple':
        mask = mask_r

    # find contours on mask and return largest bounding rect
    try:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        # OpenCV versions may return (image, contours, hierarchy)
        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return (label, conf, None)

    # largest contour by area
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < 10:  # ignore tiny blobs
        return (label, conf, None)
    x, y, w, h = cv2.boundingRect(c)
    return (label, conf, (x, y, w, h))
