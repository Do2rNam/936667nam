import cv2
import time
import os
import csv
import argparse
import ctypes
from datetime import datetime
from db import FruitDB
from detector import detect_fruit
from nutrition_api import get_nutrition_info

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-bbox', action='store_true')
    parser.add_argument('--no-detect', action='store_true')
    parser.add_argument('--no-smooth', action='store_true')
    parser.add_argument('--smooth-alpha', type=float, default=0.6)
    parser.add_argument('--fullscreen', action='store_true')
    args = parser.parse_args()

    bbox_on = not args.no_bbox
    detect_on = not args.no_detect
    smoothing_on = not args.no_smooth
    smooth_alpha = float(args.smooth_alpha)

    # ==========================
    # Mở camera
    # ==========================
    cap = None
    for idx in range(0, 5):
        cap_try = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap_try.isOpened():
            cap = cap_try
            break
        else:
            cap_try.release()

    if not cap or not cap.isOpened():
        print("❌ Không thể mở camera (đã thử index 0-4).")
        return
    print("✅ Camera opened.")

    # ==========================
    # Tạo cửa sổ
    # ==========================
    cv2.namedWindow('Fruit Detector', cv2.WINDOW_NORMAL)
    if args.fullscreen:
        try:
            user32 = ctypes.windll.user32
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)
            cv2.resizeWindow('Fruit Detector', screen_w, screen_h)
            cv2.setWindowProperty('Fruit Detector', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        except Exception:
            pass

    current_button_rects = {}
    smoothed_bbox = None
    last_label = None
    last_nutrition_info = None
    last_error = None

    # ==========================
    # Mouse callback
    # ==========================
    def _mouse_cb(event, mx, my, flags, param):
        nonlocal bbox_on, detect_on, smoothing_on, last_label, smoothed_bbox
        if event != cv2.EVENT_LBUTTONUP:
            return
        fx, fy = mx, my
        for key, rect in current_button_rects.items():
            x1, y1, x2, y2 = rect
            if x1 <= fx <= x2 and y1 <= fy <= y2:
                if key == 'b':
                    bbox_on = not bbox_on
                    print('[TOGGLE] BBox overlay:', 'ON' if bbox_on else 'OFF')
                elif key == 'd':
                    detect_on = not detect_on
                    print('[TOGGLE] Detection:', 'ON' if detect_on else 'OFF')
                    if not detect_on:
                        last_label = None
                        smoothed_bbox = None
                elif key == 'm':
                    smoothing_on = not smoothing_on
                    print('[TOGGLE] Smoothing:', 'ON' if smoothing_on else 'OFF')
                break

    cv2.setMouseCallback('Fruit Detector', _mouse_cb)
    print('🚀 Nhấn Q để thoát.')

    # ==========================
    # Vẽ nút
    # ==========================
    def draw_button(display, x, y, w, h, text, active, key):
        color = (0, 200, 0) if active else (100, 100, 100)
        cv2.rectangle(display, (x, y), (x + w, y + h), color, -1)
        cv2.rectangle(display, (x, y), (x + w, y + h), (255, 255, 255), 1)
        cv2.putText(display, text, (x + 10, y + h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        current_button_rects[key] = (x, y, x + w, y + h)


    # ==========================
    # Vòng lặp chính
    # ==========================
    while True:
        ret, frame = cap.read()
        if not ret:
            print('⚠️ Không đọc được frame từ camera')
            break

        display = frame.copy()
        label, conf, bbox = (None, 0.0, None)
        # reset error for this frame; will be set if detector says None
        last_error = None

        # Nhận diện trái cây
        if detect_on:
            label, conf, bbox = detect_fruit(frame, return_bbox=True)

            # Nếu detector trả về None -> không phải trái cây
            if label is None:
                last_nutrition_info = None
                last_label = None
                last_error = 'Error'
            else:
                # Chỉ gọi API khi nhãn mới
                if label != last_label:
                    last_label = label
                    last_nutrition_info = get_nutrition_info(label)
        else:
            last_label = None
            last_nutrition_info = None
            last_error = None

        # ==========================
        # Vẽ bbox
        # ==========================
        draw_bbox = None
        if bbox:
            bx, by, bw, bh = bbox
            if smoothing_on:
                if smoothed_bbox is None:
                    smoothed_bbox = (float(bx), float(by), float(bw), float(bh))
                else:
                    sx, sy, sw, sh = smoothed_bbox
                    sx = smooth_alpha * sx + (1.0 - smooth_alpha) * bx
                    sy = smooth_alpha * sy + (1.0 - smooth_alpha) * by
                    sw = smooth_alpha * sw + (1.0 - smooth_alpha) * bw
                    sh = smooth_alpha * sh + (1.0 - smooth_alpha) * bh
                    smoothed_bbox = (sx, sy, sw, sh)
                draw_bbox = tuple(map(int, smoothed_bbox))
            else:
                draw_bbox = bbox

        if bbox_on and draw_bbox:
            x, y, w, h = draw_bbox
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # ==========================
        # Vẽ nút B / D / M
        btn_w, btn_h = 100, 40
        padding = 10
        draw_button(display, 10, 10, btn_w, btn_h, "BBox", bbox_on, 'b')
        draw_button(display, 10 + btn_w + padding, 10, btn_w, btn_h, "Detect", detect_on, 'd')
        draw_button(display, 10 + 2 * (btn_w + padding), 10, btn_w, btn_h, "Smooth", smoothing_on, 'm')

        # ==========================
        # Hiển thị thông tin trái cây / lỗi
        # ==========================
        if last_error:
            cv2.putText(display, f"{last_error}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        elif last_label and last_nutrition_info:
            cv2.putText(display, f"Fruit: {last_nutrition_info['name']}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(display, f"Calories: {last_nutrition_info['calories']} kcal", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display, f"Protein: {last_nutrition_info['protein']} g", (10, 135),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display, f"Carbs: {last_nutrition_info['carbs']} g", (10, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display, f"Fat: {last_nutrition_info['fat']} g", (10, 185),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        elif last_label and not last_nutrition_info:
            cv2.putText(display, f"{last_label}: No nutrition data", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Fruit Detector', display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if cv2.getWindowProperty('Fruit Detector', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
