import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import joblib
import json
import sys
import time
import pandas as pd
from pathlib import Path

# Add src to path so we can import from ssi without PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ssi.features import extract_features
from ssi.config import load_config

WINDOW_NAME = "SSI Demo"
DISPLAY_WIDTH = 1280  # frames are resized to this width for display, so text size is consistent

# BGR colours
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (60, 60, 255)
YELLOW = (0, 255, 255)


def draw_panel(img, lines, position="top", alpha=0.6):
    """
    Draw a stack of text lines inside a semi-transparent dark banner.
    Text size scales with image height, lines never overlap, and any line
    that is too wide is shrunk to fit the frame.

    lines: list of (text, bgr_colour, size_multiplier)
    position: "top" or "bottom"
    """
    h, w = img.shape[:2]
    unit = h / 720.0
    pad = int(20 * unit)
    gap = int(14 * unit)
    font = cv2.FONT_HERSHEY_SIMPLEX
    max_w = w - 2 * pad

    items = []
    for text, color, mult in lines:
        scale = 1.0 * unit * mult
        thick = max(2, int(round(2 * scale)))
        (tw, th), base = cv2.getTextSize(text, font, scale, thick)
        if tw > max_w:  # shrink to fit
            scale *= max_w / tw
            thick = max(1, int(round(2 * scale)))
            (tw, th), base = cv2.getTextSize(text, font, scale, thick)
        items.append((text, color, scale, thick, tw, th, base))

    total_h = sum(it[5] + it[6] for it in items) + gap * (len(items) - 1) + 2 * pad
    y0 = 0 if position == "top" else h - total_h

    # semi-transparent background banner
    overlay = img.copy()
    cv2.rectangle(overlay, (0, y0), (w, y0 + total_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    y = y0 + pad
    for text, color, scale, thick, tw, th, base in items:
        y += th
        x = (w - tw) // 2  # centred horizontally
        cv2.putText(img, text, (x, y), font, scale, color, thick, cv2.LINE_AA)
        y += base + gap

    return total_h


def draw_progress_bar(img, fraction, y_center_from_bottom=0.30, color=YELLOW):
    """Simple progress bar for the 'hold still' capture."""
    h, w = img.shape[:2]
    bar_w = int(w * 0.5)
    bar_h = max(12, int(h * 0.025))
    x0 = (w - bar_w) // 2
    y0 = int(h * (1 - y_center_from_bottom))
    cv2.rectangle(img, (x0, y0), (x0 + bar_w, y0 + bar_h), (80, 80, 80), -1)
    cv2.rectangle(img, (x0, y0), (x0 + int(bar_w * fraction), y0 + bar_h), color, -1)
    cv2.rectangle(img, (x0, y0), (x0 + bar_w, y0 + bar_h), WHITE, 2)


def process_frame_qc(img_rgb, detector):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result = detector.detect(mp_image)

    if not result.pose_landmarks:
        return False, "No person detected", 0

    lm = result.pose_landmarks[0]
    mask = result.segmentation_masks[0].numpy_view()
    h, w = mask.shape[:2]
    mask = np.squeeze(mask)

    mask_binary = (mask > 0.5).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_binary, connectivity=8)
    person_count = sum(1 for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] > 0.05 * h * w)
    if person_count == 0 and num_labels > 1 and stats[1:, cv2.CC_STAT_AREA].max() > 0:
        person_count = 1

    if person_count != 1:
        return False, f"Detected {person_count} people, need 1", 0

    min_vis = 0.5
    indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    if not all(lm[i].visibility >= min_vis for i in indices):
        return False, "Not all body parts visible", 0

    ys, xs = np.where(mask_binary)
    if len(ys) > 0:
        head_top = np.min(ys)
        lowest_ankle = int(max(lm[27].y, lm[28].y) * h)
        bottom = max(np.max(ys), lowest_ankle)
        body_height_fraction = (bottom - head_top) / h
    else:
        body_height_fraction = 0

    if not (0.3 <= body_height_fraction <= 0.95):
        return False, "Stand closer/further", 0

    feet_visible = (0.02 <= lm[27].x <= 0.98) and (0.02 <= lm[27].y <= 0.98) and \
                   (0.02 <= lm[28].x <= 0.98) and (0.02 <= lm[28].y <= 0.98)
    if not feet_visible:
        return False, "Feet must be in frame", 0

    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    if len(ys) > 0:
        min_x, max_x = np.min(xs), np.max(xs)
        min_y, max_y = np.min(ys), np.max(ys)
        roi = gray[min_y:max_y + 1, min_x:max_x + 1]
        sharpness = cv2.Laplacian(roi, cv2.CV_64F).var()
        brightness = gray[mask_binary == 1].mean()
    else:
        sharpness = 0
        brightness = 0

    if not (30 <= brightness <= 220):
        return False, "Lighting too dark or bright", sharpness

    dx = lm[12].x - lm[11].x
    dy = lm[12].y - lm[11].y
    shoulder_tilt_deg = np.degrees(np.arctan2(abs(dy), abs(dx)))

    if shoulder_tilt_deg > 5:
        return False, "Keep shoulders level", sharpness

    if sharpness < 50:
        return False, "Hold still (blurry)", sharpness

    return True, "Good", sharpness


def main(input_path="", headless=False):
    if input_path:
        # If it's an image, read it manually since cv2.VideoCapture loops on images might fail
        if input_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            is_image = True
        else:
            is_image = False
            cap = cv2.VideoCapture(input_path)
    else:
        is_image = False
        cap = cv2.VideoCapture(0)

    if not is_image and not cap.isOpened():
        print("Error: Could not open camera or video file.")
        return

    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True,
        running_mode=vision.RunningMode.IMAGE
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    try:
        model = joblib.load("models/boys_model.joblib")
        with open("models/boys_model_meta.json", "r") as f:
            meta = json.load(f)
            model_features = meta['features']
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    mode = None
    buffer_frames = []

    print("Controls:")
    print("  'B' - Boys' uniform")
    print("  'G' - Girls' uniform")
    print("  'Q' - Quit")

    prediction_text = None
    prediction_time = 0

    if not headless:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)  # resizable window
        cv2.resizeWindow(WINDOW_NAME, DISPLAY_WIDTH, int(DISPLAY_WIDTH * 9 / 16))

    while True:
        if is_image:
            frame = cv2.imread(input_path)
            ret = frame is not None
            if not ret:
                break
        else:
            ret, frame = cap.read()
            if not ret:
                if input_path:
                    # Loop video for testing
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize a copy for display so text sizing is consistent across cameras.
        # (QC and the model still use the original full-resolution img_rgb.)
        fh, fw = frame.shape[:2]
        disp_h = int(fh * DISPLAY_WIDTH / fw)
        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, disp_h))

        # ---- Top banner: always-visible controls ----
        mode_label = {None: "No mode selected", 'BOYS': "Mode: BOYS", 'GIRLS': "Mode: GIRLS"}[mode]
        draw_panel(display_frame, [
            ("B = Boys    G = Girls    Q = Quit", WHITE, 0.9),
            (mode_label, YELLOW, 0.8),
        ], position="top")

        # ---- Bottom banner: status / prediction ----
        if mode is None:
            draw_panel(display_frame, [
                ("Press B or G to begin", WHITE, 1.1),
            ], position="bottom")

        elif mode == 'GIRLS':
            draw_panel(display_frame, [
                ("Girls' prediction is not available", RED, 1.1),
                ("(not enough data)", RED, 0.9),
            ], position="bottom")

        elif mode == 'BOYS':
            if time.time() - prediction_time < 5 and prediction_text:
                draw_panel(display_frame, [
                    (f"Model prediction: {prediction_text}", GREEN, 1.6),
                    ("This is an estimate and may need confirmation", GREEN, 0.8),
                ], position="bottom")
            else:
                qc_pass, reason, sharpness = process_frame_qc(img_rgb, detector)
                if qc_pass:
                    buffer_frames.append((sharpness, img_rgb.copy()))
                    draw_progress_bar(display_frame, len(buffer_frames) / 10.0)
                    draw_panel(display_frame, [
                        (f"Hold still... ({len(buffer_frames)}/10)", YELLOW, 1.3),
                    ], position="bottom")

                    if len(buffer_frames) >= 10:
                        best_frame = max(buffer_frames, key=lambda x: x[0])[1]
                        feats = extract_features(best_frame, detector)
                        feat_df = pd.DataFrame([feats])
                        X = feat_df[model_features]

                        pred_step = model.predict(X)[0]
                        pred_size = round(pred_step) * 2 + 32
                        prediction_text = f"Size {pred_size}"
                        prediction_time = time.time()
                        buffer_frames = []
                else:
                    buffer_frames = []
                    draw_panel(display_frame, [
                        ("Please stand in the marked position", RED, 1.0),
                        (f"Reason: {reason}", RED, 1.2),
                    ], position="bottom")
                    if headless:
                        print(f"Headless Mode QC Failed: {reason}")
                        break

        if not headless:
            cv2.imshow(WINDOW_NAME, display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('b'):
                mode = 'BOYS'
                buffer_frames = []
                prediction_text = None
            elif key == ord('g'):
                mode = 'GIRLS'
                buffer_frames = []
                prediction_text = None
        else:
            # Auto-test in headless
            mode = 'BOYS'
            if prediction_text:
                print(f"Headless Mode: {prediction_text}")
                break

    if not is_image:
        cap.release()
    if not headless:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="", help="Input video or image file")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    args = parser.parse_args()

    main(input_path=args.input, headless=args.headless)