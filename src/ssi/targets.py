import pandas as pd
import numpy as np
import json
from pathlib import Path
from ssi.config import load_config

def merge_classes(band_names, band_counts, min_class_n=10):
    bands = [[b] for b in band_names]
    counts = list(band_counts)
    
    while True:
        if all(c >= min_class_n for c in counts):
            break
        if len(counts) <= 1:
            break
            
        min_count = min(counts)
        if min_count >= min_class_n:
            break
            
        idx = counts.index(min_count)
        
        left_idx = idx - 1
        right_idx = idx + 1
        
        if left_idx >= 0 and right_idx < len(counts):
            if counts[left_idx] <= counts[right_idx]:
                merge_with = left_idx
            else:
                merge_with = right_idx
        elif left_idx >= 0:
            merge_with = left_idx
        else:
            merge_with = right_idx
            
        i, j = min(idx, merge_with), max(idx, merge_with)
        counts[i] += counts[j]
        del counts[j]
        bands[i].extend(bands[j])
        del bands[j]
        
    status = "NO_VALID_TARGET" if len(counts) == 1 else "SUCCESS"
    
    mapping = {}
    if status == "SUCCESS":
        for b_group in bands:
            group_name = "_".join(b_group)
            for b in b_group:
                mapping[b] = group_name
    else:
        for b_group in bands:
            for b in b_group:
                mapping[b] = "NO_VALID_TARGET"
                
    return {
        "status": status,
        "mapping": mapping,
        "counts_before": list(band_counts),
        "counts_after": counts
    }

def chart_rule(chest_cm, tie_mode='up'):
    if pd.isna(chest_cm):
        return np.nan
    chest_in = chest_cm / 2.54
    sizes = np.array([32, 34, 36, 38, 40, 42, 44, 46])
    dists = np.abs(sizes - chest_in)
    min_dist = np.min(dists)
    nearest = sizes[dists == min_dist]
    if len(nearest) == 1:
        return nearest[0]
    else:
        if tie_mode == 'up':
            return np.max(nearest)
        else:
            return np.min(nearest)

def build_datasets():
    config = load_config()
    
    # Paths
    Path("outputs/logs").mkdir(parents=True, exist_ok=True)
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    df_resp = pd.read_csv("data/interim/responses_valid.csv")
    df_feat = pd.read_csv("data/interim/features.csv")
    df_qc = pd.read_csv("data/interim/qc_manual.csv")
    
    # Filter
    dropped = []
    
    # 1. Consented
    for idx, row in df_resp.iterrows():
        if not row['consented']:
            dropped.append({"code": row['code'], "reason": "not consented or refused"})
    
    df_resp = df_resp[df_resp['consented'] == True]
    
    # 2. Accepted photos
    accepted_codes = set(df_qc[df_qc['manual_decision'] == 'accept']['code'])
    for idx, row in df_resp.iterrows():
        if row['code'] not in accepted_codes:
            dropped.append({"code": row['code'], "reason": "failed qc or no photo"})
            
    df_accepted = df_resp[df_resp['code'].isin(accepted_codes)]
    
    # 3. Inner join with features
    df = df_accepted.merge(df_feat, on='code', how='inner')
    
    pd.DataFrame(dropped).to_csv("outputs/logs/dropped_rows.csv", index=False)
    
    # Targets
    df['size_num'] = df['size_reported'].astype(float)
    df['size_step'] = (df['size_num'] - 32) / 2
    df['size_class'] = df['size_num']
    
    # Band mapping
    bands_cfg = config['bands']
    size_to_band = {}
    for b_name, b_sizes in bands_cfg.items():
        for s in b_sizes:
            size_to_band[s] = b_name
            
    df['band'] = df['size_num'].map(size_to_band)
    
    # Covariates
    df['loose_or_heavy'] = ((df['fit_rating'] >= 4.0) | (df['clothing'].str.contains('Jacket|Sweater', na=False, case=False))).astype(int)
    df['uniform_photo'] = df['clothing'].str.contains('Uniform', na=False, case=False).astype(int)
    
    # Chest rules
    if 'chest1_cm' in df.columns and 'chest2_cm' in df.columns:
        df['chest_mean_cm'] = df[['chest1_cm', 'chest2_cm']].mean(axis=1)
        df['chart_primary'] = df['chest_mean_cm'].apply(lambda x: chart_rule(x, tie_mode='up'))
        df['chart_sensitivity'] = df['chest_mean_cm'].apply(lambda x: chart_rule(x, tie_mode='down'))
    
    df['merged_class'] = None
    class_counts_out = []
    
    min_class_n = config.get('min_class_n', 10)
    
    for cat in config['categories']:
        cat_df = df[df['category'] == cat]
        if len(cat_df) == 0:
            continue
            
        band_names = list(bands_cfg.keys())
        band_counts = [cat_df[cat_df['band'] == b].shape[0] for b in band_names]
        
        merge_res = merge_classes(band_names, band_counts, min_class_n)
        
        map_path = f"data/processed/class_map_{cat}.json"
        with open(map_path, 'w') as f:
            json.dump(merge_res, f, indent=2)
            
        mapping = merge_res['mapping']
        
        df.loc[df['category'] == cat, 'merged_class'] = df.loc[df['category'] == cat, 'band'].map(mapping)
        
        if merge_res['status'] == "SUCCESS":
            merged_names = []
            for b in band_names:
                m = mapping[b]
                if m not in merged_names:
                    merged_names.append(m)
            for i, m in enumerate(merged_names):
                class_counts_out.append({
                    "category": cat,
                    "merged_class": m,
                    "count": merge_res['counts_after'][i]
                })
        else:
            class_counts_out.append({
                "category": cat,
                "merged_class": "NO_VALID_TARGET",
                "count": len(cat_df)
            })
            
        df[df['category'] == cat].to_csv(f"data/processed/analysis_{cat.lower()}.csv", index=False)
        
    df_counts = pd.DataFrame(class_counts_out)
    df_counts.to_csv("outputs/tables/class_counts.csv", index=False)
    
    print("\nClass Counts:")
    print(df_counts.to_string(index=False))

if __name__ == "__main__":
    build_datasets()
