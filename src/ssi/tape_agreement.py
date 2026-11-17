import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

from ssi.targets import chart_rule

def get_boot_ci(y_true, y_pred, metric_fn, n_boot=1000, seed=20260929):
    np.random.seed(seed)
    n = len(y_true)
    boot_vals = []
    
    y_t = np.array(y_true)
    y_p = np.array(y_pred)
    
    for _ in range(n_boot):
        idx = np.random.choice(n, size=n, replace=True)
        boot_vals.append(metric_fn(y_t[idx], y_p[idx]))
        
    return np.percentile(boot_vals, 2.5), np.percentile(boot_vals, 97.5)

def qwk(y1, y2):
    return cohen_kappa_score(y1, y2, weights='quadratic')

def process_tape_agreement():
    df_resp = pd.read_csv("data/interim/responses_valid.csv")
    
    # Filter rows with both chest1_cm and chest2_cm
    df_tape = df_resp.dropna(subset=['chest1_cm', 'chest2_cm']).copy()
    
    # Table columns:
    # code, category, batch, clothing, chest1, chest2, mean chest in cm and inches, 
    # |chest1 - chest2|, chart size (round up on ties) and (round down on ties), 
    # reported size, difference in steps (reported minus chart, in steps of 2), 
    # exact match, within-one-step match, fit_rating
    
    df_tape['mean_chest_cm'] = df_tape[['chest1_cm', 'chest2_cm']].mean(axis=1)
    df_tape['mean_chest_in'] = df_tape['mean_chest_cm'] / 2.54
    df_tape['chest_diff_abs'] = (df_tape['chest1_cm'] - df_tape['chest2_cm']).abs()
    
    df_tape['chart_up'] = df_tape['mean_chest_cm'].apply(lambda x: chart_rule(x, 'up'))
    df_tape['chart_down'] = df_tape['mean_chest_cm'].apply(lambda x: chart_rule(x, 'down'))
    
    df_tape['reported_size'] = df_tape['size_reported'].astype(float)
    df_tape['diff_steps'] = (df_tape['reported_size'] - df_tape['chart_up']) / 2
    
    df_tape['exact_match'] = df_tape['reported_size'] == df_tape['chart_up']
    df_tape['within_one_step'] = df_tape['diff_steps'].abs() <= 1
    
    out_cols = [
        'code', 'category', 'batch', 'clothing', 'chest1_cm', 'chest2_cm',
        'mean_chest_cm', 'mean_chest_in', 'chest_diff_abs',
        'chart_up', 'chart_down', 'reported_size', 'diff_steps',
        'exact_match', 'within_one_step', 'fit_rating'
    ]
    
    table = df_tape[out_cols].copy()
    
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    table.to_csv("outputs/tables/tape_agreement.csv", index=False)
    
    # Stats
    n = len(df_tape)
    exact_k = df_tape['exact_match'].sum()
    within_k = df_tape['within_one_step'].sum()
    
    exact_ci = proportion_confint(exact_k, n, method='wilson')
    within_ci = proportion_confint(within_k, n, method='wilson')
    
    kappa = qwk(df_tape['reported_size'], df_tape['chart_up'])
    kappa_ci = get_boot_ci(df_tape['reported_size'], df_tape['chart_up'], qwk)
    
    mean_signed_diff = df_tape['diff_steps'].mean()
    mean_abs_diff = df_tape['diff_steps'].abs().mean()
    
    spearman, _ = stats.spearmanr(df_tape['reported_size'], df_tape['chart_up'])
    
    diff_gt_15 = (df_tape['chest_diff_abs'] > 1.5).sum()
    
    # Technical error of measurement = sqrt( sum(diff^2) / 2n )
    tem = np.sqrt( (df_tape['chest_diff_abs']**2).sum() / (2 * n) )
    
    # Sensitivity excluding P013, P044, P070
    df_sens = df_tape[~df_tape['code'].isin(['P013', 'P044', 'P070'])]
    n_sens = len(df_sens)
    sens_exact_k = df_sens['exact_match'].sum()
    sens_within_k = df_sens['within_one_step'].sum()
    sens_exact_ci = proportion_confint(sens_exact_k, n_sens, method='wilson')
    sens_within_ci = proportion_confint(sens_within_k, n_sens, method='wilson')
    
    # Boys only
    df_boys = df_tape[df_tape['category'] == 'BOYS']
    n_boys = len(df_boys)
    df_boys[out_cols].to_csv("outputs/tables/tape_agreement_boys.csv", index=False)
    
    boys_exact_k = df_boys['exact_match'].sum()
    boys_within_k = df_boys['within_one_step'].sum()
    boys_exact_ci = proportion_confint(boys_exact_k, n_boys, method='wilson')
    boys_within_ci = proportion_confint(boys_within_k, n_boys, method='wilson')
    
    with open("outputs/tables/tape_agreement_stats.txt", "w") as f:
        f.write("n = 19 is below the target of 40; the subset was not drawn by SRS; some readings were taken over clothing; results are exploratory\n\n")
        f.write(f"Total rows: {n}\n")
        f.write(f"Exact match: {exact_k} of {n} ({exact_k/n*100:.1f}%), 95% CI: [{exact_ci[0]*100:.1f}%, {exact_ci[1]*100:.1f}%]\n")
        f.write(f"Within one step: {within_k} of {n} ({within_k/n*100:.1f}%), 95% CI: [{within_ci[0]*100:.1f}%, {within_ci[1]*100:.1f}%]\n")
        f.write(f"Quadratic weighted kappa: {kappa:.3f}, 95% CI: [{kappa_ci[0]:.3f}, {kappa_ci[1]:.3f}]\n")
        f.write(f"Mean signed diff in steps: {mean_signed_diff:.2f}\n")
        f.write(f"Mean absolute diff in steps: {mean_abs_diff:.2f}\n")
        f.write(f"Spearman correlation: {spearman:.3f}\n")
        f.write(f"Pairs differing by > 1.5 cm: {diff_gt_15}\n")
        f.write(f"Technical error of measurement (cm): {tem:.2f}\n\n")
        
        f.write(f"Sensitivity (excluding P013, P044, P070, n={n_sens}):\n")
        f.write(f"Exact: {sens_exact_k} of {n_sens} ({sens_exact_k/n_sens*100:.1f}%), 95% CI: [{sens_exact_ci[0]*100:.1f}%, {sens_exact_ci[1]*100:.1f}%]\n")
        f.write(f"Within one: {sens_within_k} of {n_sens} ({sens_within_k/n_sens*100:.1f}%), 95% CI: [{sens_within_ci[0]*100:.1f}%, {sens_within_ci[1]*100:.1f}%]\n\n")
        
        f.write(f"Boys only (n={n_boys}):\n")
        f.write(f"Exact: {boys_exact_k} of {n_boys} ({boys_exact_k/n_boys*100:.1f}%), 95% CI: [{boys_exact_ci[0]*100:.1f}%, {boys_exact_ci[1]*100:.1f}%]\n")
        f.write(f"Within one: {boys_within_k} of {n_boys} ({boys_within_k/n_boys*100:.1f}%), 95% CI: [{boys_within_ci[0]*100:.1f}%, {boys_within_ci[1]*100:.1f}%]\n\n")
        
        f.write("Reported size and the chart size from tape agree exactly for about a third of tested students; this agreement bounds how well any model trained on reported size can recommend the right size.\n")
        
if __name__ == '__main__':
    process_tape_agreement()
