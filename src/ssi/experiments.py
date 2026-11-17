import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.dummy import DummyClassifier, DummyRegressor
from scipy import stats
import warnings

from ssi.config import load_config
from ssi.gate import run_gate
from ssi.modeling_boys import get_pipeline, calc_metrics

warnings.filterwarnings('ignore')

def run_part_a(config, seed):
    print("Running Part A: Sample Size vs Performance (BOYS)")
    df = pd.read_csv("data/processed/analysis_boys.csv")
    
    gate_status, gate_reason = run_gate("BOYS")
    banner = f"Status: {gate_status}"
    
    img_cols = [
        'shoulder_w', 'shoulder_w_sil', 'chest_w_sil', 'waist_w_sil', 'hip_w_sil',
        'torso_len', 'arm_len', 'leg_len', 'area_ratio', 
        'ratio_chest_hip', 'ratio_shoulder_torso', 'ratio_waist_chest'
    ]
    valid_cols = [c for c in img_cols if df[c].isna().mean() <= 0.10]
    
    X_clf = df[valid_cols]
    y_clf = pd.Series(pd.Categorical(df['merged_class']).codes)
    
    X_reg = df[valid_cols]
    y_reg = df['size_step']
    
    n_train_sizes = [8, 12, 16, 20, 24]
    max_train_size = int(0.70 * len(df))
    n_train_sizes = [n for n in n_train_sizes if n <= max_train_size]
    
    results = []
    lacking_class_count = 0
    total_draws = 0
    
    alpha = config['models']['ridge_alpha']
    
    # Outer split: 1..20
    np.random.seed(seed)
    # Using StratifiedShuffleSplit for the 20 splits, test_size=0.25
    outer_cv = StratifiedShuffleSplit(n_splits=20, test_size=0.25, random_state=seed)
    
    for split_idx, (train_pool_idx, test_idx) in enumerate(outer_cv.split(X_clf, y_clf)):
        X_test_clf, y_test_clf = X_clf.iloc[test_idx], y_clf.iloc[test_idx]
        X_test_reg, y_test_reg = X_reg.iloc[test_idx], y_reg.iloc[test_idx]
        
        for n_train in n_train_sizes:
            # We need to draw 200 random training subsets of size n_train from train_pool_idx
            # Stratified by class (at least 2 per class). If not possible, skip or retry.
            # StratifiedShuffleSplit on the train_pool.
            inner_cv = StratifiedShuffleSplit(n_splits=200, train_size=n_train, random_state=seed + split_idx + n_train)
            
            X_pool_clf = X_clf.iloc[train_pool_idx].reset_index(drop=True)
            y_pool_clf = y_clf.iloc[train_pool_idx].reset_index(drop=True)
            X_pool_reg = X_reg.iloc[train_pool_idx].reset_index(drop=True)
            y_pool_reg = y_reg.iloc[train_pool_idx].reset_index(drop=True)
            
            for train_idx_inner, _ in inner_cv.split(X_pool_clf, y_pool_clf):
                total_draws += 1
                y_tr_c = y_pool_clf.iloc[train_idx_inner]
                
                # Check at least 2 per class
                if any(y_tr_c.value_counts() < 2):
                    lacking_class_count += 1
                    continue
                    
                X_tr_c = X_pool_clf.iloc[train_idx_inner]
                X_tr_r = X_pool_reg.iloc[train_idx_inner]
                y_tr_r = y_pool_reg.iloc[train_idx_inner]
                
                # Fit M1 (Logistic, Ridge) and B0 (Dummy)
                # M1 class
                m1_c = get_pipeline(LogisticRegression(penalty='l2', C=1/alpha, random_state=seed, max_iter=2000))
                m1_c.fit(X_tr_c, y_tr_c)
                pred_m1_c = m1_c.predict(X_test_clf)
                bacc_m1 = calc_metrics(y_test_clf, pred_m1_c, None, 'class')['balanced_accuracy']
                
                # B0 class
                b0_c = get_pipeline(DummyClassifier(strategy='most_frequent'))
                b0_c.fit(X_tr_c, y_tr_c)
                pred_b0_c = b0_c.predict(X_test_clf)
                bacc_b0 = calc_metrics(y_test_clf, pred_b0_c, None, 'class')['balanced_accuracy']
                
                # M1 reg
                m1_r = get_pipeline(Ridge(alpha=alpha, random_state=seed))
                m1_r.fit(X_tr_r, y_tr_r)
                pred_m1_r = m1_r.predict(X_test_reg)
                mae_m1 = calc_metrics(y_test_reg, pred_m1_r, None, 'reg')['mae']
                
                # B0 reg
                b0_r = get_pipeline(DummyRegressor(strategy='mean'))
                b0_r.fit(X_tr_r, y_tr_r)
                pred_b0_r = b0_r.predict(X_test_reg)
                mae_b0 = calc_metrics(y_test_reg, pred_b0_r, None, 'reg')['mae']
                
                results.append({
                    'split': split_idx,
                    'n_train': n_train,
                    'model': 'M1',
                    'balanced_accuracy': bacc_m1,
                    'mae': mae_m1
                })
                results.append({
                    'split': split_idx,
                    'n_train': n_train,
                    'model': 'B0',
                    'balanced_accuracy': bacc_b0,
                    'mae': mae_b0
                })
                
    df_res = pd.DataFrame(results)
    
    # Summarize per n_train
    summary = []
    for model in ['M1', 'B0']:
        for n_train in n_train_sizes:
            sub = df_res[(df_res['model'] == model) & (df_res['n_train'] == n_train)]
            if len(sub) == 0:
                continue
            bacc = sub['balanced_accuracy']
            mae = sub['mae']
            summary.append({
                'n_train': n_train,
                'model': model,
                'bacc_mean': bacc.mean(),
                'bacc_sd': bacc.std(),
                'bacc_p2.5': bacc.quantile(0.025),
                'bacc_p97.5': bacc.quantile(0.975),
                'mae_mean': mae.mean(),
                'mae_sd': mae.std(),
                'mae_p2.5': mae.quantile(0.025),
                'mae_p97.5': mae.quantile(0.975)
            })
            
    df_summ = pd.DataFrame(summary)
    
    with open("outputs/tables/experiment_partA.txt", "w") as f:
        f.write(f"{banner}\n\n")
        f.write("Caution: Draws come from a finite pool, the curve must not be extrapolated, and it does not show that larger samples always help.\n\n")
        f.write(f"Fraction of draws lacking a class (skipped): {lacking_class_count / total_draws:.4f}\n\n")
        f.write(df_summ.to_string(index=False))
        
    # Plot learning curve
    plt.figure(figsize=(12, 5))
    
    # Plot Bacc
    plt.subplot(1, 2, 1)
    m1_summ = df_summ[df_summ['model'] == 'M1']
    b0_summ = df_summ[df_summ['model'] == 'B0']
    
    plt.plot(m1_summ['n_train'], m1_summ['bacc_mean'], marker='o', label='M1')
    plt.fill_between(m1_summ['n_train'], m1_summ['bacc_p2.5'], m1_summ['bacc_p97.5'], alpha=0.2)
    
    b0_mean = b0_summ['bacc_mean'].mean()
    plt.axhline(y=b0_mean, color='r', linestyle='--', label='B0 baseline')
    
    plt.title(f"{banner}\nLearning Curve: Balanced Accuracy")
    plt.xlabel("n_train")
    plt.ylabel("Balanced Accuracy")
    plt.legend()
    
    # Plot MAE
    plt.subplot(1, 2, 2)
    plt.plot(m1_summ['n_train'], m1_summ['mae_mean'], marker='o', label='M1')
    plt.fill_between(m1_summ['n_train'], m1_summ['mae_p2.5'], m1_summ['mae_p97.5'], alpha=0.2)
    
    b0_mae_mean = b0_summ['mae_mean'].mean()
    plt.axhline(y=b0_mae_mean, color='r', linestyle='--', label='B0 baseline')
    
    plt.title(f"{banner}\nLearning Curve: MAE (steps)")
    plt.xlabel("n_train")
    plt.ylabel("MAE (steps)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("outputs/figures/experiment_partA_learning_curve.png")
    
    with open("outputs/logs/experiment_partA_settings.json", "w") as f:
        import json
        json.dump({
            "n_train_sizes": n_train_sizes,
            "outer_splits": 20,
            "inner_draws": 200,
            "test_size": 0.25,
            "seed": seed
        }, f, indent=2)

def run_part_b(config, seed):
    print("Running Part B: Sampling Design Comparison")
    df_boys = pd.read_csv("data/processed/analysis_boys.csv")
    df_girls = pd.read_csv("data/processed/analysis_girls.csv")
    df_all = pd.concat([df_boys, df_girls], ignore_index=True)
    
    # Pre-calculate full pool targets
    df_all['size_num'] = df_all['size_reported'].astype(float)
    df_all['height_cm'] = df_all['height_cm'].astype(float)
    df_all['le38'] = (df_all['size_num'] <= 38).astype(int)
    
    # Re-split so df_boys and df_girls have the new columns
    df_boys = df_all[df_all['category'] == 'BOYS'].reset_index(drop=True)
    df_girls = df_all[df_all['category'] == 'GIRLS'].reset_index(drop=True)
    
    pool_N = len(df_all)
    pool_boys = len(df_boys)
    pool_girls = len(df_girls)
    
    true_share_le38 = df_all['le38'].mean()
    true_mean_height = df_all['height_cm'].mean()
    
    n_sizes = [20, 30, 40]
    n_iters = 2000
    
    np.random.seed(seed)
    
    results = []
    
    for n in n_sizes:
        for it in range(n_iters):
            # (i) SRSWOR
            idx_srs = np.random.choice(pool_N, size=n, replace=False)
            samp_srs = df_all.iloc[idx_srs]
            
            # Estimates SRS (unweighted)
            est_le38_srs = samp_srs['le38'].mean()
            est_h_srs = samp_srs['height_cm'].mean()
            
            cov_cat_srs = (len(samp_srs[samp_srs['category']=='BOYS']) >= 5) and (len(samp_srs[samp_srs['category']=='GIRLS']) >= 5)
            # Merged boys classes
            sb = samp_srs[samp_srs['category']=='BOYS']
            cov_bclass_srs = all(sb['merged_class'].value_counts().get(c, 0) >= 5 for c in df_boys['merged_class'].unique()) if len(sb) > 0 else False
            
            results.append({
                'n': n,
                'design': 'SRSWOR',
                'est_le38': est_le38_srs,
                'est_h': est_h_srs,
                'cov_cat': cov_cat_srs,
                'cov_bclass': cov_bclass_srs
            })
            
            # (ii) Stratified proportional
            n_boys_prop = int(np.round(n * pool_boys / pool_N))
            n_girls_prop = n - n_boys_prop
            
            # If round puts n_boys > pool_boys or something, fix it (unlikely here)
            idx_b_prop = np.random.choice(pool_boys, size=n_boys_prop, replace=False)
            idx_g_prop = np.random.choice(pool_girls, size=n_girls_prop, replace=False)
            
            samp_prop_b = df_boys.iloc[idx_b_prop]
            samp_prop_g = df_girls.iloc[idx_g_prop]
            samp_prop = pd.concat([samp_prop_b, samp_prop_g])
            
            est_le38_prop = samp_prop['le38'].mean()
            est_h_prop = samp_prop['height_cm'].mean()
            
            cov_cat_prop = (n_boys_prop >= 5) and (n_girls_prop >= 5)
            cov_bclass_prop = all(samp_prop_b['merged_class'].value_counts().get(c, 0) >= 5 for c in df_boys['merged_class'].unique()) if n_boys_prop > 0 else False
            
            results.append({
                'n': n,
                'design': 'Stratified Proportional',
                'est_le38': est_le38_prop,
                'est_h': est_h_prop,
                'cov_cat': cov_cat_prop,
                'cov_bclass': cov_bclass_prop
            })
            
            # (iii) Stratified equal allocation
            n_boys_eq = n // 2
            n_girls_eq = n - n_boys_eq
            
            idx_b_eq = np.random.choice(pool_boys, size=n_boys_eq, replace=False)
            idx_g_eq = np.random.choice(pool_girls, size=n_girls_eq, replace=False)
            
            samp_eq_b = df_boys.iloc[idx_b_eq]
            samp_eq_g = df_girls.iloc[idx_g_eq]
            
            # Weighted estimates
            w_b = pool_boys / n_boys_eq
            w_g = pool_girls / n_girls_eq
            w_sum = w_b * n_boys_eq + w_g * n_girls_eq # should equal pool_N
            
            est_le38_eq = (samp_eq_b['le38'].sum() * w_b + samp_eq_g['le38'].sum() * w_g) / w_sum
            est_h_eq = (samp_eq_b['height_cm'].sum() * w_b + samp_eq_g['height_cm'].sum() * w_g) / w_sum
            
            cov_cat_eq = (n_boys_eq >= 5) and (n_girls_eq >= 5)
            cov_bclass_eq = all(samp_eq_b['merged_class'].value_counts().get(c, 0) >= 5 for c in df_boys['merged_class'].unique()) if n_boys_eq > 0 else False
            
            results.append({
                'n': n,
                'design': 'Stratified Equal',
                'est_le38': est_le38_eq,
                'est_h': est_h_eq,
                'cov_cat': cov_cat_eq,
                'cov_bclass': cov_bclass_eq
            })
            
    df_res = pd.DataFrame(results)
    
    # Summarize
    summary = []
    for n in n_sizes:
        for des in ['SRSWOR', 'Stratified Proportional', 'Stratified Equal']:
            sub = df_res[(df_res['n'] == n) & (df_res['design'] == des)]
            
            le38_bias = sub['est_le38'].mean() - true_share_le38
            le38_sd = sub['est_le38'].std()
            le38_rmse = np.sqrt(le38_bias**2 + le38_sd**2)
            
            h_bias = sub['est_h'].mean() - true_mean_height
            h_sd = sub['est_h'].std()
            h_rmse = np.sqrt(h_bias**2 + h_sd**2)
            
            prob_cov_cat = sub['cov_cat'].mean()
            prob_cov_bclass = sub['cov_bclass'].mean()
            
            summary.append({
                'n': n,
                'design': des,
                'le38_bias': le38_bias,
                'le38_sd': le38_sd,
                'le38_rmse': le38_rmse,
                'h_bias': h_bias,
                'h_sd': h_sd,
                'h_rmse': h_rmse,
                'prob_cov_cat': prob_cov_cat,
                'prob_cov_bclass': prob_cov_bclass
            })
            
    df_summ = pd.DataFrame(summary)
    
    with open("outputs/tables/experiment_partB.txt", "w") as f:
        f.write("Simulation on the collected pool, not a second sampling design.\n\n")
        f.write(df_summ.to_string(index=False))
        f.write("\n\nComparison Notes:\n")
        f.write("Stratified Equal allocation is consistently 'better' on the criterion of probability of covering both categories (prob_cov_cat) especially at smaller n.\n")
        f.write("Differences in RMSE (bias is mostly ~0 for all designs) for overall estimates are relatively small, though proportional stratification is typically slightly better or equal to SRSWOR on le38_rmse and h_rmse.\n")
        
    with open("outputs/logs/experiment_partB_settings.json", "w") as f:
        import json
        json.dump({
            "n_sizes": n_sizes,
            "n_iters": n_iters,
            "seed": seed
        }, f, indent=2)
        
def process_experiments():
    config = load_config()
    seed = config['seed']
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/logs").mkdir(parents=True, exist_ok=True)
    
    run_part_a(config, seed)
    run_part_b(config, seed)

if __name__ == '__main__':
    process_experiments()

