import pandas as pd
import joblib
import json
from pathlib import Path
from sklearn.linear_model import Ridge
from ssi.modeling_boys import get_pipeline
from ssi.config import load_config
from datetime import datetime

def save_boys_model():
    Path("models").mkdir(parents=True, exist_ok=True)
    df = pd.read_csv("data/processed/analysis_boys.csv")
    
    img_cols = [
        'shoulder_w', 'shoulder_w_sil', 'chest_w_sil', 'waist_w_sil', 'hip_w_sil',
        'torso_len', 'arm_len', 'leg_len', 'area_ratio', 
        'ratio_chest_hip', 'ratio_shoulder_torso', 'ratio_waist_chest'
    ]
    valid_cols = [c for c in img_cols if df[c].isna().mean() <= 0.10]
    
    X = df[valid_cols]
    y = df['size_step']
    
    config = load_config()
    alpha = config['models']['ridge_alpha']
    seed = config['seed']
    
    # We use M1 since demo.py does not have access to height_cm
    pipe = get_pipeline(Ridge(alpha=alpha, random_state=seed))
    pipe.fit(X, y)
    
    joblib.dump(pipe, "models/boys_model.joblib")
    
    metadata = {
        "training_size": len(df),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status_banner": f"Status: FIT (n={len(df)})",
        "features": valid_cols,
        "model_type": "M1 (Ridge regression on image features)"
    }
    with open("models/boys_model_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    save_boys_model()

