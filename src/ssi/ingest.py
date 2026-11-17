import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
from ssi.config import load_config

def load_responses(path: str | Path, config: dict = None) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == '.xlsx':
        df = pd.read_excel(path, sheet_name="Form Responses 1")
    else:
        df = pd.read_csv(path)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed')

    cols = {
        "Timestamp": "timestamp",
        "A1. Participant code (from the slip)": "code",
        "A2. Form filled by": "filled_by",
        "A3. Session": "session",
        "A4. How did this person get in?": "how_in",
        "A5. Consent and age (script read out)": "consent",
        "Q1. Uniform category chosen by the participant": "category",
        "Q2. Batch": "batch",
        "Q3. Height in cm (as told by the participant)": "height_cm",
        "Q4. Current SSI shirt size": "size_reported",
        "Q5. How does that shirt fit?": "fit_rating",
        "Q6. What is the participant wearing on top?": "clothing",
        "Q8. Chest reading 1 (cm), ONLY if flagged for tape": "chest1_cm",
        "Q9. Chest reading 2 (cm), ONLY if flagged for tape": "chest2_cm",
        "Q10. Notes": "notes",
        "Q7. Upload the photo": "photo_link"
    }
    df = df.rename(columns=cols)

    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', np.nan)

    if 'category' in df.columns:
        df['category'] = df['category'].replace({"Boys'": "BOYS", "Girls'": "GIRLS"})
        df['category'] = df['category'].str.upper()

    if 'photo_link' in df.columns:
        df['photo_file_id'] = df['photo_link'].apply(
            lambda x: x.split("id=")[1].split("&")[0] if pd.notna(x) and "id=" in str(x) else np.nan
        )

    if 'size_reported' in df.columns:
        df['size_reported'] = df['size_reported'].replace("Does not know / no SSI shirt", np.nan)
        df['size_reported'] = pd.to_numeric(df['size_reported'], errors='coerce')

    df['consented'] = df['consent'].str.startswith("Yes", na=False)
    df['refused'] = df['consent'] == "No: refused"
    df['under18'] = df['consent'] == "No: under 18"
    df['mode'] = df['session'].apply(lambda x: "online" if pd.notna(x) and "online" in str(x).lower() else "station")
    
    pilot_codes = config.get("pilot_codes", []) if config else []
    df['is_pilot'] = (
        df['code'].isin(pilot_codes) | 
        (df['session'] == "PILOT") | 
        (df['how_in'] == "Pilot student")
    )

    df['how_in_short'] = df['how_in'].apply(
        lambda x: "primary" if pd.notna(x) and "primary" in str(x).lower() else (
                  "reserve" if pd.notna(x) and "reserve" in str(x).lower() else np.nan)
    )

    df['session_date'] = df['timestamp'].dt.date

    for c in ['height_cm', 'fit_rating', 'chest1_cm', 'chest2_cm']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    return df

def validate_responses(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    problems = []

    def add_prob(code, field, problem, severity):
        problems.append({"code": code, "field": field, "problem": problem, "severity": severity})

    code_pattern = re.compile(r"^P\d{3}$")
    seen_codes = set()
    prev_time = None
    code_nums = []

    for i, row in df.iterrows():
        code = row['code']
        if not isinstance(code, str) or not code_pattern.match(code):
            add_prob(code, "code", "Invalid code format", "ERROR")
        else:
            code_num = int(code[1:])
            code_nums.append((code, code_num))
            
        if code in seen_codes:
            add_prob(code, "code", "Duplicate code", "ERROR")
        seen_codes.add(code)

        if pd.notna(row['timestamp']) and row['timestamp'] > datetime.now():
            add_prob(code, "timestamp", "Timestamp in the future", "ERROR")

        if prev_time is not None and pd.notna(row['timestamp']):
            if row['timestamp'] < prev_time:
                add_prob(code, "timestamp", "Earlier than previous row", "WARNING")
        if pd.notna(row['timestamp']):
            prev_time = row['timestamp']

        if pd.notna(row['timestamp']) and pd.notna(row['session']):
            day = row['timestamp'].day
            month = row['timestamp'].month
            session_str = str(row['session']).lower()
            if "october" in session_str and month == 10:
                if "1st" in session_str and day != 1:
                    add_prob(code, "timestamp", f"Date does not match session {row['session']}", "WARNING")
                elif "5th" in session_str and day != 5:
                    add_prob(code, "timestamp", f"Date does not match session {row['session']}", "WARNING")
                elif "6th" in session_str and day != 6:
                    add_prob(code, "timestamp", f"Date does not match session {row['session']}", "WARNING")

        if row['consented']:
            if row['category'] not in config.get('categories', []):
                add_prob(code, "category", "Invalid category", "ERROR")
            if row['batch'] not in config.get('batches', []):
                add_prob(code, "batch", "Invalid batch", "ERROR")
            if row['session'] not in config.get('sessions', []):
                add_prob(code, "session", "Invalid session", "ERROR")
            
            hr = config.get('height_range', [130, 210])
            if pd.isna(row['height_cm']) or not (hr[0] <= row['height_cm'] <= hr[1]):
                add_prob(code, "height_cm", "Height out of range or missing", "ERROR")

            sizes = config.get('sizes', [])
            if pd.isna(row['size_reported']):
                add_prob(code, "size_reported", "Size missing", "WARNING")
            elif row['size_reported'] not in sizes:
                add_prob(code, "size_reported", f"Size not in sizes {sizes}", "ERROR")

            if pd.isna(row['fit_rating']) or not (1 <= row['fit_rating'] <= 5):
                add_prob(code, "fit_rating", "Invalid fit rating", "ERROR")

            allowed_clothing = ['Regular top or shirt', 'Loose top or hoodie', 'Plain fitted top', 'Jacket or heavy layer', 'SSI uniform shirt']
            if row['clothing'] not in allowed_clothing:
                add_prob(code, "clothing", "Invalid clothing", "ERROR")

            if pd.isna(row['photo_link']):
                add_prob(code, "photo_link", "Photo link missing", "ERROR")

        has_c1 = pd.notna(row['chest1_cm'])
        has_c2 = pd.notna(row['chest2_cm'])
        
        if has_c1 != has_c2:
            add_prob(code, "chest", "chest1 and chest2 must be both present or both missing", "ERROR")
        
        if has_c1 and has_c2:
            if not row['consented']:
                add_prob(code, "chest", "Tape readings only for consented rows", "ERROR")
            
            cr = config.get('chest_range', [60, 140])
            if not (cr[0] <= row['chest1_cm'] <= cr[1]) or not (cr[0] <= row['chest2_cm'] <= cr[1]):
                add_prob(code, "chest", "Chest out of range", "ERROR")
                
            diff = abs(row['chest1_cm'] - row['chest2_cm'])
            if diff > config.get('tape_pair_max_diff_cm', 1.5):
                add_prob(code, "chest", "Chest diff > max", "WARNING")

    if code_nums:
        code_nums.sort(key=lambda x: x[1])
        for i in range(1, len(code_nums)):
            if code_nums[i][1] > code_nums[i-1][1] + 1:
                gap_start = code_nums[i-1][1] + 1
                gap_end = code_nums[i][1] - 1
                for gap_num in range(gap_start, gap_end + 1):
                    add_prob("ALL", "code", f"Gap in code sequence: P{gap_num:03d}", "WARNING")

    return pd.DataFrame(problems, columns=["code", "field", "problem", "severity"])

def run_ingest():
    config = load_config()
    raw_dir = Path("data/raw")
    interim_dir = Path("data/interim")
    outputs_dir = Path("outputs/tables")
    
    xlsx_path = raw_dir / "responses_export.xlsx.xlsx"
    if not xlsx_path.exists():
        xlsx_path = raw_dir / "responses_export.xlsx"
    csv_paths = list(raw_dir.glob("responses_export*.csv"))
    
    if xlsx_path.exists():
        df = load_responses(xlsx_path, config)
    elif csv_paths:
        df = load_responses(csv_paths[0], config)
    else:
        raise FileNotFoundError("Could not find responses_export in data/raw")

    probs = validate_responses(df, config)
    probs.to_csv(outputs_dir / "data_quality_report.csv", index=False)

    df.to_csv(interim_dir / "responses_valid.csv", index=False)

    consented_df = df[df['consented']]
    refused_df = df[df['refused']]

    def to_md_table(series, col_name):
        lines = [f"| {col_name} | Count |", "|---|---|"]
        for idx, val in series.items():
            lines.append(f"| {idx} | {val} |")
        return "\n".join(lines)

    md = [
        "# Data Audit Report\n",
        f"- **Total Rows**: {len(df)}",
        f"- **Consented**: {len(consented_df)}",
        f"- **Refused**: {len(refused_df)}\n",
        "## By Category (Consented)",
        to_md_table(consented_df['category'].value_counts(), 'Category'),
        "\n## By Batch (Consented)",
        to_md_table(consented_df['batch'].value_counts(), 'Batch'),
        "\n## By Session (Consented)",
        to_md_table(consented_df['session'].value_counts(), 'Session'),
        "\n## By How In (Consented)",
        to_md_table(consented_df['how_in_short'].value_counts(), 'How In'),
        "\n## By Operator (All)",
        to_md_table(df['filled_by'].value_counts(), 'Operator'),
        "\n## By Clothing (Consented)",
        to_md_table(consented_df['clothing'].value_counts(), 'Clothing'),
        "\n## Fit Rating Distribution (Consented)",
        to_md_table(consented_df['fit_rating'].value_counts().sort_index(), 'Fit Rating'),
        f"\n## Tape Count: {consented_df['chest1_cm'].notna().sum()}",
    ]

    if not probs.empty:
        md.append(f"\n## Errors: {len(probs[probs['severity'] == 'ERROR'])}")
        md.append(f"## Warnings: {len(probs[probs['severity'] == 'WARNING'])}")
    else:
        md.append("\n## Errors: 0")
        md.append("## Warnings: 0")

    with open(outputs_dir / "data_audit.md", "w") as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    run_ingest()
