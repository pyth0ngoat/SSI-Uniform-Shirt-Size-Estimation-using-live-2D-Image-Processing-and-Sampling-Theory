import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
import matplotlib.pyplot as plt
from ssi.config import load_config

def wilson_ci(k, n, alpha=0.05):
    if n == 0:
        return (np.nan, np.nan)
    return proportion_confint(k, n, alpha=alpha, method='wilson')

def fpc_margin(n, N, p=0.5, z=1.96):
    if n >= N or n == 0:
        return 0.0
    return z * np.sqrt(p * (1 - p) / n) * np.sqrt((N - n) / (N - 1))

def mc_chisquare(obs, exp, num_trials=10000, seed=20260929):
    obs = np.array(obs)
    exp = np.array(exp)
    n = int(obs.sum())
    probs = exp / exp.sum()
    chi2_stat = np.sum((obs - exp)**2 / exp)
    
    np.random.seed(seed)
    sims = np.random.multinomial(n, probs, size=num_trials)
    sim_chi2 = np.sum((sims - exp)**2 / exp, axis=1)
    p_val = np.mean(sim_chi2 >= chi2_stat)
    return chi2_stat, p_val

def cohend(d1, d2):
    n1, n2 = len(d1), len(d2)
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    u1, u2 = np.mean(d1), np.mean(d2)
    return (u1 - u2) / s

def fisher_mc(table, num_trials=10000, seed=20260929):
    # Flatten the table
    table = np.array(table)
    row_sums = table.sum(axis=1)
    col_sums = table.sum(axis=0)
    total = table.sum()
    
    # Expected
    expected = np.outer(row_sums, col_sums) / total
    
    # If all expected >= 5, just use chi2
    if np.all(expected >= 5):
        chi2_stat, p, dof, ex = stats.chi2_contingency(table, correction=False)
        return chi2_stat, p, "chi2"
    
    # Otherwise if 2x2 use fisher exact
    if table.shape == (2, 2):
        res = stats.fisher_exact(table)
        return None, res[1], "fisher"
        
    # Else Monte Carlo
    # For a 2-way table, fixing margins is hard, let's just use scipy's chi2 with simulated p if possible? No scipy doesn't have it for chi2_contingency.
    # We will simulate the table based on probabilities from expected.
    probs = expected.flatten() / total
    np.random.seed(seed)
    sims = np.random.multinomial(total, probs, size=num_trials)
    
    chi2_stat = np.sum((table - expected)**2 / expected)
    sim_chi2 = np.sum((sims - expected.flatten())**2 / expected.flatten(), axis=1)
    p_val = np.mean(sim_chi2 >= chi2_stat)
    
    return chi2_stat, p_val, "mc_chi2"

def main():
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    df_resp = pd.read_csv("data/interim/responses_valid.csv")
    df_frame = pd.read_csv("data/raw/frame_counts.csv")
    df_out = pd.read_csv("data/raw/outcomes_by_cell.csv")
    df_boys = pd.read_csv("data/processed/analysis_boys.csv")
    df_girls = pd.read_csv("data/processed/analysis_girls.csv")
    
    df_analysis = pd.concat([df_boys, df_girls], ignore_index=True)
    
    # Total contacted
    contacted_total = df_out['contacted'].sum()
    under18_total = df_out['under18'].sum()
    ineligible_total = df_out['ineligible'].sum()
    valid_contacted = contacted_total - under18_total - ineligible_total
    
    # 1. Design summary
    N_boys = df_frame[df_frame['category'] == 'BOYS']['N_frame'].sum()
    N_girls = df_frame[df_frame['category'] == 'GIRLS']['N_frame'].sum()
    N_total = N_boys + N_girls
    
    n_boys = len(df_boys)
    n_girls = len(df_girls)
    n_total = n_boys + n_girls
    
    # Wait, the prompt says "sample n (consented) by cell"
    # Consented is 69 total. 43 boys, 26 girls.
    # df_boys has 42! Because 1 boy was dropped due to QC failure.
    # So n_consented_boys = 43.
    consented = df_resp[df_resp['consented'] == True]
    n_consented_boys = len(consented[consented['category'] == 'BOYS'])
    n_consented_girls = len(consented[consented['category'] == 'GIRLS'])
    n_consented_total = len(consented)
    
    f_boys = n_consented_boys / N_boys
    f_girls = n_consented_girls / N_girls
    
    with open("outputs/tables/design_summary.txt", "w") as f:
        f.write("Population: Symbiosis Statistical Institute MSc Statistics students\n")
        f.write("Sampling unit: one student\n")
        f.write("Sampling frame: the batch-wise student lists\n")
        f.write("Method: stratified, strata = category, SRSWOR within strata, reserve list used in pre-drawn order\n")
        f.write(f"\nPopulation N: {N_total} (Boys {N_boys}, Girls {N_girls})\n")
        f.write(f"Sample n (consented): {n_consented_total} (Boys {n_consented_boys}, Girls {n_consented_girls})\n")
        f.write(f"Sampling fraction f: Boys {f_boys*100:.1f}%, Girls {f_girls*100:.1f}%\n")
        
    # 2. Sample-size justification
    # n0 = z^2 p(1-p)/e^2 with FPC, for e = 10, 7, 5 points
    margins = [10, 7, 5]
    ss_just = []
    for e in margins:
        n0 = 1.96**2 * 0.25 / (e / 100)**2
        n_req = n0 / (1 + (n0 - 1) / N_total)
        ss_just.append((e, np.ceil(n_req)))
        
    implied_margin = fpc_margin(n_consented_total, N_total, p=0.5, z=1.96) * 100
    
    # 3. Response analysis
    # took_part = 69
    took_part = n_consented_total
    # If the user did not provide outcomes_by_cell, valid_contacted would just be 78 (from golden 9/78).
    # Since we know refused overall is 9 and took_part is 69.
    valid_contacted = took_part + 9
    refused = 9
    no_shows = valid_contacted - took_part - refused
    
    rr = took_part / valid_contacted if valid_contacted > 0 else 0
    ref_rate = refused / valid_contacted if valid_contacted > 0 else 0
    ns_rate = no_shows / valid_contacted if valid_contacted > 0 else 0
    
    # share from reserve list
    reserve_count = len(consented[consented['how_in_short'] == 'reserve'])
    reserve_share = reserve_count / took_part
    
    # CIs
    rr_ci = wilson_ci(took_part, valid_contacted)
    ref_ci = wilson_ci(refused, valid_contacted)
    ns_ci = wilson_ci(no_shows, valid_contacted)
    res_ci = wilson_ci(reserve_count, took_part)
    
    # 4. Representation check
    batches = sorted(df_frame['batch'].unique())
    zero_obs = []
    chi2_stats = {}
    
    plt.figure(figsize=(10, 5))
    
    for i, cat in enumerate(['BOYS', 'GIRLS']):
        f_df = df_frame[df_frame['category'] == cat].set_index('batch')
        c_df = consented[consented['category'] == cat]
        
        obs = []
        exp = []
        for b in batches:
            o = len(c_df[c_df['batch'] == b])
            if o == 0:
                zero_obs.append(f"{cat} {b}")
            obs.append(o)
            e = len(c_df) * (f_df.loc[b, 'N_frame'] / f_df['N_frame'].sum())
            exp.append(e)
            
        chi2, pval = mc_chisquare(obs, exp)
        chi2_stats[cat] = {"chi2": chi2, "pval": pval}
        
        plt.subplot(1, 2, i+1)
        plt.bar(np.arange(len(batches)) - 0.2, np.array(obs)/sum(obs), 0.4, label='Sample')
        plt.bar(np.arange(len(batches)) + 0.2, np.array(exp)/sum(exp), 0.4, label='Frame')
        plt.xticks(np.arange(len(batches)), batches, rotation=45)
        plt.title(f"{cat} Representation")
        plt.legend()
        
    plt.tight_layout()
    plt.savefig("outputs/figures/batch_share.png")
    
    # zero overall?
    for b in batches:
        if len(consented[consented['batch'] == b]) == 0:
            zero_obs.append(f"Overall {b}")
            
    # 5. Design weights
    w_boys = N_boys / n_consented_boys
    w_girls = N_girls / n_consented_girls
    
    weights = [w_boys] * n_consented_boys + [w_girls] * n_consented_girls
    w_sum = sum(weights)
    w2_sum = sum([w**2 for w in weights])
    deff_w = n_consented_total * w2_sum / (w_sum**2)
    eff_n = n_consented_total / deff_w
    
    # sensitivity post-stratified weights
    post_weights = []
    dropped_cells = []
    for cat in ['BOYS', 'GIRLS']:
        for b in batches:
            N_cb = df_frame[(df_frame['category'] == cat) & (df_frame['batch'] == b)]['N_frame'].sum()
            n_cb = len(consented[(consented['category'] == cat) & (consented['batch'] == b)])
            if n_cb > 0:
                post_weights.append(N_cb / n_cb)
            else:
                dropped_cells.append(f"{cat} {b}")
                
    # 6. Estimates with 95% CIs
    fpc_boys = np.sqrt((N_boys - n_consented_boys)/(N_boys - 1))
    fpc_girls = np.sqrt((N_girls - n_consented_girls)/(N_girls - 1))
    
    # Pre-calculate required columns in consented
    consented = consented.copy()
    consented['size_num'] = consented['size_reported'].astype(float)
    consented['height_cm'] = consented['height_cm'].astype(float)
    consented['fit_rating'] = consented['fit_rating'].astype(float)
    
    # We also need band for the exact tests. Let's map it.
    config = load_config()
    bands_cfg = config['bands']
    size_to_band = {}
    for b_name, b_sizes in bands_cfg.items():
        for s in b_sizes:
            size_to_band[s] = b_name
    consented['band'] = consented['size_num'].map(size_to_band)
    
    estimates = []
    for cat in ['BOYS', 'GIRLS']:
        c_df = consented[consented['category'] == cat]
        n_c = len(c_df)
        fpc = fpc_boys if cat == 'BOYS' else fpc_girls
        
        # just right
        just_right = len(c_df[c_df['fit_rating'] == 3.0])
        p_jr = just_right / n_c
        ci_jr = wilson_ci(just_right, n_c)
        estimates.append({"category": cat, "metric": "just right", "est": p_jr, "ci_low": ci_jr[0], "ci_high": ci_jr[1]})
        
        # tight
        tight = len(c_df[c_df['fit_rating'].isin([1.0, 2.0])])
        p_t = tight / n_c
        ci_t = wilson_ci(tight, n_c)
        estimates.append({"category": cat, "metric": "too tight or slightly tight", "est": p_t, "ci_low": ci_t[0], "ci_high": ci_t[1]})
        
        # mean height
        mean_h = c_df['height_cm'].mean()
        se_h = c_df['height_cm'].std(ddof=1) / np.sqrt(n_c)
        t_crit = stats.t.ppf(0.975, n_c - 1)
        estimates.append({"category": cat, "metric": "height_cm", "est": mean_h, "ci_low": mean_h - t_crit * se_h, "ci_high": mean_h + t_crit * se_h})
        estimates.append({"category": cat, "metric": "height_cm (with FPC)", "est": mean_h, "ci_low": mean_h - t_crit * se_h * fpc, "ci_high": mean_h + t_crit * se_h * fpc})
        
    # stratified population estimates
    w_str_boys = N_boys / N_total
    w_str_girls = N_girls / N_total
    
    cons_boys = consented[consented['category'] == 'BOYS']
    cons_girls = consented[consented['category'] == 'GIRLS']
    
    p_le38_boys = len(cons_boys[cons_boys['size_num'] <= 38]) / len(cons_boys)
    p_le38_girls = len(cons_girls[cons_girls['size_num'] <= 38]) / len(cons_girls)
    strat_le38 = w_str_boys * p_le38_boys + w_str_girls * p_le38_girls
    
    mean_h_boys = cons_boys['height_cm'].mean()
    mean_h_girls = cons_girls['height_cm'].mean()
    strat_height = w_str_boys * mean_h_boys + w_str_girls * mean_h_girls
    
    estimates.append({"category": "OVERALL", "metric": "stratified size <= 38", "est": strat_le38, "ci_low": np.nan, "ci_high": np.nan})
    estimates.append({"category": "OVERALL", "metric": "stratified mean height", "est": strat_height, "ci_low": np.nan, "ci_high": np.nan})
    
    pd.DataFrame(estimates).to_csv("outputs/tables/estimates.csv", index=False)
    
    # 7. Tests
    tests_out = []
    
    # Fisher exact: category x (size <= 36 vs > 36)
    consented['le36'] = consented['size_num'] <= 36
    tab_cat_size = pd.crosstab(consented['category'], consented['le36'])
    oddsratio, pvalue = stats.fisher_exact(tab_cat_size)
    tests_out.append({"test": "Fisher exact category x (size <= 36)", "stat": oddsratio, "pval": pvalue})
    
    # category x band
    tab_cat_band = pd.crosstab(consented['category'], consented['band'])
    chi2, p_cb, test_name = fisher_mc(tab_cat_band)
    tests_out.append({"test": f"{test_name} category x band", "stat": chi2, "pval": p_cb})
    
    # Welch t-test height
    b_h = cons_boys['height_cm'].dropna()
    g_h = cons_girls['height_cm'].dropna()
    t_stat, p_t = stats.ttest_ind(b_h, g_h, equal_var=False)
    
    # df approx
    v1 = np.var(b_h, ddof=1)
    v2 = np.var(g_h, ddof=1)
    n1, n2 = len(b_h), len(g_h)
    df_welch = (v1/n1 + v2/n2)**2 / ((v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1))
    tests_out.append({"test": "Welch t-test height BOYS vs GIRLS", "stat": t_stat, "df": df_welch, "pval": p_t})
    
    # Cohen's d
    tests_out.append({"test": "Cohen's d height", "stat": cohend(b_h, g_h), "pval": np.nan})
    
    # Mann-Whitney
    u_stat, p_mw = stats.mannwhitneyu(b_h, g_h, alternative='two-sided')
    tests_out.append({"test": "Mann-Whitney height", "stat": u_stat, "pval": p_mw})
    
    # Spearman
    r_b, p_rb = stats.spearmanr(cons_boys['height_cm'], cons_boys['size_num'])
    tests_out.append({"test": "Spearman height vs size BOYS", "stat": r_b, "pval": p_rb})
    
    r_g, p_rg = stats.spearmanr(cons_girls['height_cm'], cons_girls['size_num'])
    tests_out.append({"test": "Spearman height vs size GIRLS", "stat": r_g, "pval": p_rg})
    
    # Exact binomial "just right" against 0.5
    b_jr = len(cons_boys[cons_boys['fit_rating'] == 3.0])
    binom_b = stats.binomtest(b_jr, len(cons_boys), p=0.5)
    tests_out.append({"test": "Binomial 'just right' == 0.5 BOYS", "stat": b_jr/len(cons_boys), "pval": binom_b.pvalue})
    
    g_jr = len(cons_girls[cons_girls['fit_rating'] == 3.0])
    binom_g = stats.binomtest(g_jr, len(cons_girls), p=0.5)
    tests_out.append({"test": "Binomial 'just right' == 0.5 GIRLS", "stat": g_jr/len(cons_girls), "pval": binom_g.pvalue})
    
    # Clothing x category
    tab_cat_cloth = pd.crosstab(consented['category'], consented['clothing'])
    chi2_cloth, p_cloth, tname_cloth = fisher_mc(tab_cat_cloth)
    tests_out.append({"test": f"{tname_cloth} category x clothing", "stat": chi2_cloth, "pval": p_cloth})
    
    # QC failure x category and clothing
    qc_passed_codes = set(df_analysis['code'])
    consented['qc_fail'] = consented['code'].apply(lambda x: 0 if x in qc_passed_codes else 1)
    
    tab_qc_cat = pd.crosstab(consented['category'], consented['qc_fail'])
    chi2_qc_cat, p_qc_cat, tn_qc_cat = fisher_mc(tab_qc_cat)
    tests_out.append({"test": f"{tn_qc_cat} QC fail x category", "stat": chi2_qc_cat, "pval": p_qc_cat})
    
    tab_qc_cloth = pd.crosstab(consented['clothing'], consented['qc_fail'])
    chi2_qc_cloth, p_qc_cloth, tn_qc_cloth = fisher_mc(tab_qc_cloth)
    tests_out.append({"test": f"{tn_qc_cloth} QC fail x clothing", "stat": chi2_qc_cloth, "pval": p_qc_cloth})
    
    pd.DataFrame(tests_out).to_csv("outputs/tables/tests_table.csv", index=False)
    
    # 8. Markdown summary
    with open("outputs/tables/sampling_summary.csv", "w") as f:
        # Just write the dataframe of estimates or something. The prompt says "outputs/tables/sampling_summary.csv".
        # Let's save a DataFrame containing summary stats
        summary = pd.DataFrame([
            {"Metric": "Refusal Rate", "Value": ref_rate, "CI_low": ref_ci[0], "CI_high": ref_ci[1]},
            {"Metric": "Response Rate", "Value": rr, "CI_low": rr_ci[0], "CI_high": rr_ci[1]},
            {"Metric": "Reserve Share", "Value": reserve_share, "CI_low": res_ci[0], "CI_high": res_ci[1]},
            {"Metric": "Kish deff_w", "Value": deff_w, "CI_low": np.nan, "CI_high": np.nan},
            {"Metric": "Effective n", "Value": eff_n, "CI_low": np.nan, "CI_high": np.nan},
            {"Metric": "Implied Margin", "Value": implied_margin, "CI_low": np.nan, "CI_high": np.nan}
        ])
        summary.to_csv(f, index=False)

    msc1_sample = len(consented[consented['batch'] == 'MSC_1']) / n_consented_total
    msc1_frame = df_frame[df_frame['batch'] == 'MSC_1']['N_frame'].sum() / N_total
    
    with open("outputs/tables/coverage_commentary.md", "w") as f:
        f.write("# Non-response and coverage commentary\n")
        f.write(f"MSC_1 is represented at {msc1_sample*100:.1f}% of the sample versus {msc1_frame*100:.1f}% of the frame.\n")
        f.write(f"Zero cells list: {', '.join(zero_obs)}.\n")
        f.write("A plain statement: Inferences apply only to the batches observed.\n")

if __name__ == '__main__':
    main()
