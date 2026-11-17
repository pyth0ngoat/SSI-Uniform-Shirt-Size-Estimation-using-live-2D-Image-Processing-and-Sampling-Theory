import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True
)
detector = vision.PoseLandmarker.create_from_options(options)

img = cv2.imread(r'C:\Users\kapil\.gemini\antigravity\scratch\ssi_project\data\photos_raw\Q7. Upload the photo (File responses)\P003.jpg')
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
result = detector.detect(mp_image)

if result.pose_landmarks:
    lm = result.pose_landmarks[0]
    mask = result.segmentation_masks[0].numpy_view()
    h, w = mask.shape
    
    # 1. person_count
    mask_binary = (mask > 0.5).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_binary, connectivity=8)
    # stats: [x, y, w, h, area]
    person_count = sum(1 for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] > 0.05 * h * w)
    
    # 2. landmarks visible
    min_vis = 0.5
    indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    all_vis = all(lm[i].visibility >= min_vis for i in indices)
    
    # 3. body height fraction
    ys, xs = np.where(mask_binary)
    if len(ys) > 0:
        head_top = np.min(ys)
        lowest_ankle = int(max(lm[27].y, lm[28].y) * h)
        bottom = max(np.max(ys), lowest_ankle)
        body_height_fraction = (bottom - head_top) / h
    else:
        body_height_fraction = 0
        
    # 4. feet_visible
    feet_visible = (0.02 <= lm[27].x <= 0.98) and (0.02 <= lm[27].y <= 0.98) and \
                   (0.02 <= lm[28].x <= 0.98) and (0.02 <= lm[28].y <= 0.98)
                   
    # 5. sharpness
    if len(ys) > 0:
        min_x, max_x = np.min(xs), np.max(xs)
        min_y, max_y = np.min(ys), np.max(ys)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        roi = gray[min_y:max_y+1, min_x:max_x+1]
        sharpness = cv2.Laplacian(roi, cv2.CV_64F).var()
    else:
        sharpness = 0
        
    # 6. brightness
    if len(ys) > 0:
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        brightness = gray[mask_binary == 1].mean()
    else:
        brightness = 0
        
    # 7. shoulder tilt
    dx = lm[12].x - lm[11].x
    dy = lm[12].y - lm[11].y
    tilt = np.degrees(np.arctan2(abs(dy), abs(dx)))
    
    # 8. arms clear
    hip_y = int((lm[23].y + lm[24].y) / 2 * h)
    hip_y = np.clip(hip_y, 0, h - 1)
    row = mask_binary[hip_y, :]
    if np.any(row):
        torso_min_x = np.argmax(row)
        torso_max_x = w - 1 - np.argmax(row[::-1])
        w_l_x = lm[15].x * w
        w_r_x = lm[16].x * w
        margin = 0.03 * w
        w_min = min(w_l_x, w_r_x)
        w_max = max(w_l_x, w_r_x)
        arms_clear = (w_min < torso_min_x - margin) and (w_max > torso_max_x + margin)
    else:
        arms_clear = False
        
    print(f"person_count: {person_count}")
    print(f"all_vis: {all_vis}")
    print(f"body_height_fraction: {body_height_fraction}")
    print(f"feet_visible: {feet_visible}")
    print(f"sharpness: {sharpness}")
    print(f"brightness: {brightness}")
    print(f"tilt: {tilt}")
    print(f"arms_clear: {arms_clear}")

