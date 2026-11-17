import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import re
from datetime import date
from ssi.config import load_config
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageDraw, ImageFont

def process_photo(file_path: str, detector: vision.PoseLandmarker):
    img = cv2.imread(str(file_path))
    if img is None:
        return None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result = detector.detect(mp_image)
    
    if not result.pose_landmarks:
        return {'person_count': 0, 'all_key_landmarks_visible': False, 'body_height_fraction': 0,
                'feet_visible': False, 'sharpness': 0, 'brightness': 0, 'shoulder_tilt_deg': 0, 'arms_clear': False}
        
    lm = result.pose_landmarks[0]
    mask = result.segmentation_masks[0].numpy_view()
    h, w = mask.shape[:2]
    mask = np.squeeze(mask)
    
    mask_binary = (mask > 0.5).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_binary, connectivity=8)
    person_count = sum(1 for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] > 0.05 * h * w)
    if person_count == 0 and stats[1:, cv2.CC_STAT_AREA].max() > 0:
        person_count = 1  # At least someone detected
        
    min_vis = 0.5
    indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    # For presence/visibility, in Tasks API visibility is available
    all_key_landmarks_visible = all(lm[i].visibility >= min_vis for i in indices)
    
    ys, xs = np.where(mask_binary)
    if len(ys) > 0:
        head_top = np.min(ys)
        lowest_ankle = int(max(lm[27].y, lm[28].y) * h)
        bottom = max(np.max(ys), lowest_ankle)
        body_height_fraction = (bottom - head_top) / h
    else:
        body_height_fraction = 0
        
    feet_visible = (0.02 <= lm[27].x <= 0.98) and (0.02 <= lm[27].y <= 0.98) and \
                   (0.02 <= lm[28].x <= 0.98) and (0.02 <= lm[28].y <= 0.98)
                   
    if len(ys) > 0:
        min_x, max_x = np.min(xs), np.max(xs)
        min_y, max_y = np.min(ys), np.max(ys)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        roi = gray[min_y:max_y+1, min_x:max_x+1]
        sharpness = cv2.Laplacian(roi, cv2.CV_64F).var()
        brightness = gray[mask_binary == 1].mean()
    else:
        sharpness = 0
        brightness = 0
        
    dx = lm[12].x - lm[11].x
    dy = lm[12].y - lm[11].y
    shoulder_tilt_deg = np.degrees(np.arctan2(abs(dy), abs(dx)))
    
    hip_l_x = lm[23].x * w
    hip_r_x = lm[24].x * w
    hip_min = min(hip_l_x, hip_r_x)
    hip_max = max(hip_l_x, hip_r_x)
    
    w_l_x = lm[15].x * w
    w_r_x = lm[16].x * w
    margin = 0.03 * w
    w_min = min(w_l_x, w_r_x)
    w_max = max(w_l_x, w_r_x)
    arms_clear = (w_min < hip_min - margin) and (w_max > hip_max + margin)
        
    return {
        'person_count': person_count,
        'all_key_landmarks_visible': all_key_landmarks_visible,
        'body_height_fraction': body_height_fraction,
        'feet_visible': feet_visible,
        'sharpness': sharpness,
        'brightness': brightness,
        'shoulder_tilt_deg': shoulder_tilt_deg,
        'arms_clear': arms_clear
    }

def run_qc():
    config = load_config()
    qc_conf = config['qc']
    manifest_df = pd.read_csv("data/interim/photo_manifest.csv")
    manifest_df = manifest_df[manifest_df['found'] == True]
    
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True
    )
    detector = vision.PoseLandmarker.create_from_options(options)
    
    results = []
    
    for i, row in manifest_df.iterrows():
        code = row['code']
        path = row['file_path']
        res = process_photo(path, detector)
        if res is None:
            res = {'person_count': 0, 'all_key_landmarks_visible': False, 'body_height_fraction': 0,
                   'feet_visible': False, 'sharpness': 0, 'brightness': 0, 'shoulder_tilt_deg': 0, 'arms_clear': False}
        res['code'] = code
        results.append(res)
        
    qc_df = pd.DataFrame(results)
    
    # Base checks (everything except sharpness)
    base_passes = []
    for i, row in qc_df.iterrows():
        reasons = []
        if row['person_count'] != 1:
            reasons.append("Person count != 1")
        if not row['all_key_landmarks_visible']:
            reasons.append("Key landmarks missing")
        bh_min, bh_max = qc_conf['body_height_fraction']
        if not (bh_min <= row['body_height_fraction'] <= bh_max):
            reasons.append(f"Height fraction {row['body_height_fraction']:.2f} out of range")
        if not row['feet_visible']:
            reasons.append("Feet not visible")
        b_min, b_max = qc_conf['brightness']
        if not (b_min <= row['brightness'] <= b_max):
            reasons.append(f"Brightness {row['brightness']:.1f} out of range")
        if row['shoulder_tilt_deg'] > qc_conf['max_shoulder_tilt_deg']:
            reasons.append(f"Shoulder tilt {row['shoulder_tilt_deg']:.1f} > max")
        if not row['arms_clear']:
            reasons.append("Arms not clear")
            
        base_passes.append(len(reasons) == 0)
        
    qc_df['base_pass'] = base_passes
    
    min_sharpness = qc_conf.get('min_sharpness')
    if min_sharpness is None or pd.isna(min_sharpness):
        sharp_vals = qc_df[qc_df['base_pass']]['sharpness']
        if len(sharp_vals) > 0:
            min_sharpness = int(round(np.percentile(sharp_vals, 5)))
        else:
            min_sharpness = 100
            
        with open("config.yaml", "r") as f:
            text = f.read()
        text = re.sub(r'min_sharpness:\s*null', f'min_sharpness: {min_sharpness} # calibrated on {date.today()}', text)
        with open("config.yaml", "w") as f:
            f.write(text)
            
        with open("outputs/logs/qc_calibration.md", "w") as f:
            f.write(f"# QC Sharpness Calibration\nMin sharpness set to: {min_sharpness}\nBased on 5th percentile of {len(sharp_vals)} images passing other checks.")
            
    qc_passes = []
    qc_reasons_list = []
    
    for i, row in qc_df.iterrows():
        reasons = []
        if row['person_count'] != 1: reasons.append("Person count != 1")
        if not row['all_key_landmarks_visible']: reasons.append("Key landmarks missing")
        bh_min, bh_max = qc_conf['body_height_fraction']
        if not (bh_min <= row['body_height_fraction'] <= bh_max): reasons.append("Height fraction out of range")
        if not row['feet_visible']: reasons.append("Feet not visible")
        b_min, b_max = qc_conf['brightness']
        if not (b_min <= row['brightness'] <= b_max): reasons.append("Brightness out of range")
        if row['shoulder_tilt_deg'] > qc_conf['max_shoulder_tilt_deg']: reasons.append("Shoulder tilt > max")
        if not row['arms_clear']: reasons.append("Arms not clear")
        if row['sharpness'] < min_sharpness: reasons.append(f"Sharpness {row['sharpness']:.1f} < min {min_sharpness}")
        
        qc_passes.append(len(reasons) == 0)
        qc_reasons_list.append(" | ".join(reasons))
        
    qc_df['qc_pass'] = qc_passes
    qc_df['qc_reasons'] = qc_reasons_list
    
    # reorder
    qc_df = qc_df[['code', 'person_count', 'all_key_landmarks_visible', 'body_height_fraction', 'feet_visible', 'sharpness', 'brightness', 'shoulder_tilt_deg', 'arms_clear', 'qc_pass', 'qc_reasons']]
    qc_df.to_csv("data/interim/qc_report.csv", index=False)
    
    # Manual review
    failed = qc_df[~qc_df['qc_pass']]['code'].tolist()
    passed = qc_df[qc_df['qc_pass']]['code'].tolist()
    
    import random
    random.seed(config['seed'])
    n_sample = int(len(passed) * 0.1)
    passed_sample = random.sample(passed, n_sample)
    
    review_codes = set(failed + passed_sample)
    
    manual_rows = []
    for code in sorted(manifest_df['code'].tolist()):
        qc_pass = qc_df.loc[qc_df['code'] == code, 'qc_pass'].values[0]
        decision = "accept" if qc_pass else "reject"
        manual_rows.append({'code': code, 'manual_decision': decision, 'manual_reason': qc_df.loc[qc_df['code'] == code, 'qc_reasons'].values[0]})
    pd.DataFrame(manual_rows).to_csv("data/interim/qc_manual.csv", index=False)
    
    # Montage
    montage_codes = list(review_codes)
    if montage_codes:
        montage_w = 4
        montage_h = (len(montage_codes) + montage_w - 1) // montage_w
        tile_size = 200
        img = Image.new('RGB', (montage_w * tile_size, montage_h * (tile_size + 40)), 'white')
        draw = ImageDraw.Draw(img)
        
        for i, code in enumerate(montage_codes):
            col = i % montage_w
            row = i // montage_w
            x = col * tile_size
            y = row * (tile_size + 40)
            
            path = manifest_df[manifest_df['code'] == code]['file_path'].values[0]
            try:
                photo = Image.open(path)
                photo = photo.resize((tile_size, tile_size))
                img.paste(photo, (x, y))
            except:
                pass
            
            reasons = qc_df.loc[qc_df['code'] == code, 'qc_reasons'].values[0]
            short_reasons = reasons[:30] + "..." if len(reasons) > 30 else reasons
            draw.text((x + 5, y + tile_size + 5), f"{code}: {short_reasons}", fill='black')
            
        img.save("data/photos_raw/qc_montage.png")
    
    # Summary
    resp_df = pd.read_csv("data/interim/responses_valid.csv")
    merged = pd.merge(qc_df, resp_df[['code', 'category', 'clothing', 'size_reported']], on='code', how='inner')
    merged['qc_final'] = merged['qc_pass'] # manual decisions not edited yet
    
    summary = merged.groupby(['category', 'clothing', 'qc_final']).size().reset_index(name='count')
    summary.to_csv("outputs/tables/qc_summary.csv", index=False)
    
    import scipy.stats as stats
    # test category
    cont_cat = pd.crosstab(merged['category'], merged['qc_final'])
    if min(cont_cat.shape) == 2:
        try:
            _, p_cat = stats.fisher_exact(cont_cat)
        except ValueError:
            _, p_cat, _, _ = stats.chi2_contingency(cont_cat)
        if p_cat < 0.05:
            print("WARNING: QC failure is significantly related to category (p < 0.05).")
            
    # test clothing
    cont_cloth = pd.crosstab(merged['clothing'], merged['qc_final'])
    if cont_cloth.size > 0:
        _, p_cloth, _, _ = stats.chi2_contingency(cont_cloth)
        if p_cloth < 0.05:
            print("WARNING: QC failure is significantly related to clothing (p < 0.05).")

    # test size_reported
    cont_size = pd.crosstab(merged['size_reported'], merged['qc_final'])
    if cont_size.size > 0:
        _, p_size, _, _ = stats.chi2_contingency(cont_size)
        if p_size < 0.05:
            print("WARNING: QC failure is significantly related to reported size (p < 0.05).")
            
    # Print accepted n
    boys_accepted = len(merged[(merged['category'] == 'BOYS') & merged['qc_final']])
    girls_accepted = len(merged[(merged['category'] == 'GIRLS') & merged['qc_final']])
    
    print(f"Boys accepted: {boys_accepted} (Floor 40, Target 60)")
    print(f"Girls accepted: {girls_accepted} (Floor 40, Target 60)")

if __name__ == "__main__":
    run_qc()
