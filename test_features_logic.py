import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

def get_sil_width(mask, y, h):
    widths = []
    for dy in range(-2, 3):
        row_y = int(y) + dy
        if 0 <= row_y < h:
            widths.append(np.sum(mask[row_y, :] > 0.5))
    if widths:
        return np.median(widths)
    return np.nan

def extract_features(img_rgb, detector):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result = detector.detect(mp_image)
    h, w = img_rgb.shape[:2]
    out = {k: np.nan for k in [
        'shoulder_w', 'shoulder_w_sil', 'chest_w_sil', 'waist_w_sil', 'hip_w_sil',
        'torso_len', 'arm_len', 'leg_len', 'area_ratio', 
        'ratio_chest_hip', 'ratio_shoulder_torso', 'ratio_waist_chest',
        'shoulder_tilt_deg', 'torso_lean_deg'
    ]}
    if not result.pose_landmarks:
        return out
        
    lm = result.pose_landmarks[0]
    mask = np.squeeze(result.segmentation_masks[0].numpy_view())
    
    ys, xs = np.where(mask > 0.5)
    if len(ys) == 0:
        return out
        
    head_top = np.min(ys)
    lowest_ankle = max(lm[27].y, lm[28].y) * h
    bottom = max(np.max(ys), lowest_ankle)
    body_height_px = bottom - head_top
    
    if body_height_px <= 0:
        return out
        
    def pt(i): return np.array([lm[i].x * w, lm[i].y * h])
    
    s_l, s_r = pt(11), pt(12)
    e_l, e_r = pt(13), pt(14)
    w_l, w_r = pt(15), pt(16)
    h_l, h_r = pt(23), pt(24)
    a_l, a_r = pt(27), pt(28)
    
    s_mid = (s_l + s_r) / 2
    h_mid = (h_l + h_r) / 2
    a_mid = (a_l + a_r) / 2
    
    out['shoulder_w'] = np.linalg.norm(s_l - s_r) / body_height_px
    
    shoulder_y = s_mid[1]
    hip_y = h_mid[1]
    
    out['shoulder_w_sil'] = get_sil_width(mask, shoulder_y, h) / body_height_px
    out['chest_w_sil'] = get_sil_width(mask, shoulder_y + 0.25 * (hip_y - shoulder_y), h) / body_height_px
    out['waist_w_sil'] = get_sil_width(mask, shoulder_y + 0.60 * (hip_y - shoulder_y), h) / body_height_px
    out['hip_w_sil'] = get_sil_width(mask, hip_y, h) / body_height_px
    
    out['torso_len'] = np.linalg.norm(s_mid - h_mid) / body_height_px
    
    arm_l_len = np.linalg.norm(s_l - w_l)
    arm_r_len = np.linalg.norm(s_r - w_r)
    out['arm_len'] = ((arm_l_len + arm_r_len) / 2) / body_height_px
    
    out['leg_len'] = np.linalg.norm(h_mid - a_mid) / body_height_px
    
    mask_area = np.sum(mask > 0.5)
    out['area_ratio'] = mask_area / (body_height_px ** 2)
    
    if out['hip_w_sil'] > 0:
        out['ratio_chest_hip'] = out['chest_w_sil'] / out['hip_w_sil']
    if out['torso_len'] > 0:
        out['ratio_shoulder_torso'] = out['shoulder_w_sil'] / out['torso_len']
    if out['chest_w_sil'] > 0:
        out['ratio_waist_chest'] = out['waist_w_sil'] / out['chest_w_sil']
        
    dx = s_r[0] - s_l[0]
    dy = s_r[1] - s_l[1]
    out['shoulder_tilt_deg'] = np.degrees(math.atan2(abs(dy), abs(dx)))
    
    tdx = h_mid[0] - s_mid[0]
    tdy = h_mid[1] - s_mid[1]
    if tdy != 0:
        out['torso_lean_deg'] = np.degrees(math.atan2(abs(tdx), abs(tdy)))
    else:
        out['torso_lean_deg'] = 90
        
    return out

