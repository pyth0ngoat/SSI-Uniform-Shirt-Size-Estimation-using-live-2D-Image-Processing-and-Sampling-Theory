import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

def get_sil_width(mask, y, h):
    widths = []
    for dy in range(-2, 3):
        row_y = int(y) + dy
        if 0 <= row_y < h:
            widths.append(np.sum(mask[row_y, :] > 0.5))
    if widths:
        return np.median(widths)
    return np.nan

def blur_face(img_rgb, lm, w, h):
    face_x = [lm[i].x * w for i in range(11)]
    face_y = [lm[i].y * h for i in range(11)]
    
    if not face_x:
        return img_rgb
        
    min_x, max_x = min(face_x), max(face_x)
    min_y, max_y = min(face_y), max(face_y)
    
    fw = max_x - min_x
    fh = max_y - min_y
    
    pad_x = fw * 0.4
    pad_y = fh * 0.4
    
    min_x = max(0, int(min_x - pad_x))
    max_x = min(w, int(max_x + pad_x))
    min_y = max(0, int(min_y - pad_y))
    max_y = min(h, int(max_y + pad_y))
    
    roi = img_rgb[min_y:max_y, min_x:max_x]
    if roi.size > 0:
        # Check if ROI is valid size
        if roi.shape[0] > 0 and roi.shape[1] > 0:
            roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
            roi_bgr = cv2.GaussianBlur(roi_bgr, (99, 99), 30)
            roi = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
            img_rgb[min_y:max_y, min_x:max_x] = roi
    return img_rgb

def extract_features_and_landmarks(img_rgb, detector):
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
        return out, None
        
    lm = result.pose_landmarks[0]
    mask = np.squeeze(result.segmentation_masks[0].numpy_view())
    
    ys, xs = np.where(mask > 0.5)
    if len(ys) == 0:
        return out, lm
        
    head_top = np.min(ys)
    lowest_ankle = max(lm[27].y, lm[28].y) * h
    bottom = max(np.max(ys), lowest_ankle)
    body_height_px = bottom - head_top
    
    if body_height_px <= 0:
        return out, lm
        
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
        
    return out, lm

def extract_features(img_rgb, detector):
    out, _ = extract_features_and_landmarks(img_rgb, detector)
    return out

def run_features():
    manifest = pd.read_csv("data/interim/photo_manifest.csv")
    qc_manual = pd.read_csv("data/interim/qc_manual.csv")
    responses = pd.read_csv("data/interim/responses_valid.csv")
    
    df = manifest.merge(qc_manual, on="code").merge(responses[['code', 'category']], on="code")
    accepted = df[df['manual_decision'] == 'accept']
    
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True
    )
    detector = vision.PoseLandmarker.create_from_options(options)
    
    out_dir = Path("data/photos_blurred")
    out_dir.mkdir(exist_ok=True, parents=True)
    
    features_list = []
    
    for _, row in accepted.iterrows():
        code = row['code']
        path = row['file_path']
        
        img_pil = Image.open(path)
        exif = img_pil.getexif()
        if exif and 0x0112 in exif:
            img_pil = ImageOps.exif_transpose(img_pil)
            
        img_rgb = np.array(img_pil)
        if img_rgb.shape[2] == 4:
            img_rgb = img_rgb[:,:,:3]
            
        feats, lm = extract_features_and_landmarks(img_rgb, detector)
        feats['code'] = code
        features_list.append(feats)
        
        if lm:
            img_blurred = blur_face(img_rgb.copy(), lm, img_rgb.shape[1], img_rgb.shape[0])
            out_img = Image.fromarray(img_blurred)
            out_img.save(out_dir / f"{code}.jpg")
            
    feat_df = pd.DataFrame(features_list)
    # Reorder code to front
    cols = ['code'] + [c for c in feat_df.columns if c != 'code']
    feat_df = feat_df[cols]
    
    feat_df.to_csv("data/interim/features.csv", index=False)
    
    # Feature summary
    merged = feat_df.merge(accepted[['code', 'category']], on='code')
    summary_list = []
    for cat in ['BOYS', 'GIRLS']:
        cat_df = merged[merged['category'] == cat]
        for col in cols[1:]:
            s = cat_df[col]
            summary_list.append({
                'category': cat,
                'feature': col,
                'mean': s.mean(),
                'sd': s.std(),
                'min': s.min(),
                'max': s.max(),
                'missing': s.isna().sum()
            })
            
    pd.DataFrame(summary_list).to_csv("outputs/tables/feature_summary.csv", index=False)
    
    # Sanity checks
    print("=== Sanity Checks ===")
    missing_pct = feat_df.isna().mean() * 100
    high_missing = missing_pct[missing_pct > 10]
    if len(high_missing) > 0:
        print("Features with >10% missing:")
        print(high_missing)
    else:
        print("No features with >10% missing.")
        
    out_of_range = feat_df[(feat_df['shoulder_w'] < 0.1) | (feat_df['shoulder_w'] > 0.35)]
    if len(out_of_range) > 0:
        print(f"WARNING: {len(out_of_range)} photos have implausible shoulder_w")
        
    # Scatter
    fig_dir = Path("outputs/figures")
    fig_dir.mkdir(exist_ok=True, parents=True)
    
    plt.figure()
    for cat in ['BOYS', 'GIRLS']:
        subset = merged[merged['category'] == cat]
        plt.scatter(subset['shoulder_w_sil'], subset['chest_w_sil'], label=cat)
    plt.xlabel('shoulder_w_sil')
    plt.ylabel('chest_w_sil')
    plt.legend()
    plt.title("Chest Width vs Shoulder Width")
    plt.savefig(fig_dir / "scatter_chest_shoulder.png")
    plt.close()
    
    # Heatmap
    plt.figure(figsize=(10, 8))
    corr = feat_df.drop(columns=['code']).corr()
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(fig_dir / "correlation_heatmap.png")
    plt.close()

if __name__ == "__main__":
    run_features()
