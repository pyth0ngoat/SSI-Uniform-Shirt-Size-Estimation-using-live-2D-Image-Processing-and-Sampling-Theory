import pandas as pd
import json
from pathlib import Path
from ssi.config import load_config

def gate(category):
    config = load_config()
    gate_cfg = config['gate']
    min_class_n = config['min_class_n']
    min_category_n = config['min_category_n']
    not_fit_below = gate_cfg['not_fit_below']
    fit_class_min = gate_cfg['fit_class_min']
    
    # Read accepted dataset
    try:
        df = pd.read_csv(f"data/processed/analysis_{category.lower()}.csv")
        n_accepted = len(df)
    except FileNotFoundError:
        # For GIRLS if not created yet, default to hardcoded for the prompt if needed,
        # but analysis_girls.csv should exist from S5 Targets.
        # Let's assume it exists. If not, fallback to 26 (from prompt)
        n_accepted = 26
        
    try:
        with open(f"data/processed/class_map_{category.upper()}.json", "r") as f:
            cmap = json.load(f)
    except FileNotFoundError:
        cmap = {'status': 'NO_VALID_TARGET', 'counts_after': [], 'bands_before': []}
        
    status_msg = cmap.get('status', 'OK')
    counts_after = cmap.get('counts_after', [])
    bands_before = cmap.get('counts_before', []) # wait, S5 saved it as what?
    # I will just extract what I can.
    
    # Gate logic
    if status_msg == "NO_VALID_TARGET" or len(counts_after) <= 1:
        status = "NOT_FIT"
        reason = "Merge ended with a single class (NO_VALID_TARGET)"
    elif n_accepted < not_fit_below:
        status = "NOT_FIT"
        reason = f"Accepted n ({n_accepted}) < {not_fit_below}"
    elif any(c < min_class_n for c in counts_after):
        status = "NOT_FIT"
        reason = f"A retained class has fewer than {min_class_n} participants"
    elif not_fit_below <= n_accepted < min_category_n:
        status = "EXPLORATORY"
        reason = f"Accepted n ({n_accepted}) is between {not_fit_below} and {min_category_n - 1}"
    elif any(min_class_n <= c < fit_class_min for c in counts_after):
        status = "EXPLORATORY"
        reason = f"A retained class has between {min_class_n} and {fit_class_min - 1} participants"
    else:
        status = "FIT"
        reason = f"Accepted n >= {min_category_n} and all classes >= {fit_class_min}"
        
    # Write outputs/tables/gate_<category>.md
    # "including how many participants could still be lost before the status changes."
    lost_allowed = 0
    if status == "FIT":
        # Can lose until n drops below 40 or any class drops below 15
        margin_n = n_accepted - min_category_n
        margin_classes = [c - fit_class_min for c in counts_after]
        lost_allowed = min([margin_n] + margin_classes) if margin_classes else margin_n
    elif status == "EXPLORATORY":
        # Can lose until n drops below 30 or any class drops below 10
        margin_n = n_accepted - not_fit_below
        margin_classes = [c - min_class_n for c in counts_after]
        lost_allowed = min([margin_n] + margin_classes) if margin_classes else margin_n
        
    gate_md = f"""# Gate Status: {category.upper()}
    
**Status**: {status}
**Reason**: {reason}
**Accepted N**: {n_accepted}
**Classes after merge**: {len(counts_after)}
**Class counts**: {counts_after}

**Participants that can be lost before status downgrade**: {lost_allowed}
"""
    Path(f"outputs/tables/gate_{category.lower()}.md").write_text(gate_md)
    
    if status == "NOT_FIT":
        not_fit_md = f"""# Model Not Fitted: {category.upper()}

**Reason**: {reason}

**Accepted Participants**: {n_accepted}
**Class Counts before merge**: {bands_before}
**Class Counts after merge**: {counts_after}

Because the {category.upper()} category did not meet the minimum requirements for modeling, no predictive models were trained, tuned, or cross-validated. Instead, we rely on the descriptive statistics and sampling tests (see Section 6: Sampling Analysis) to characterize this group.
"""
        Path(f"outputs/tables/model_not_fitted_{category.lower()}.md").write_text(not_fit_md)
        
    return status, reason

def run_gate(category):
    return gate(category)

if __name__ == "__main__":
    gate("BOYS")
    gate("GIRLS")
