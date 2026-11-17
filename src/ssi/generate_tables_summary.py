import os
import re
import pandas as pd
from pathlib import Path

TABLES_DIR = Path("outputs/tables")
OUTPUT_FILE = Path("outputs/tables_summary.md")

CATEGORIES = [
    {
        "title": "1. Data Audit & Quality Control (QC)",
        "description": "Initial data hygiene, response counts, session breakdown, photo integrity, and computer vision QC filters.",
        "files": [
            ("data_audit.md", "High-level summary of total consented/refused participants, cohort splits, clothing, and operators."),
            ("data_quality_report.csv", "Detailed validation report of each field, missing values, range checks, and error flags."),
            ("photo_integrity.csv", "Integrity check of raw submitted images (resolution, readability, file size)."),
            ("qc_summary.csv", "Computer vision automated QC pass/fail rates across brightness, blur, and pose detection.")
        ]
    },
    {
        "title": "2. Sampling Design & Population Estimates",
        "description": "Stratified sampling framework details, sample size allocation, design weights, Kish Deff, and Horvitz-Thompson estimates.",
        "files": [
            ("sampling_summary.csv", "Sample sizes, frame population, sampling fractions, and design weights by category stratum."),
            ("design_summary.txt", "Plain-text specification of target population, sampling unit, stratification, and reserve lists."),
            ("coverage_commentary.md", "Evaluation of batch coverage, non-response patterns, and representation across cohorts."),
            ("estimates.csv", "Population estimates for mean height, proportion <= size 38, and proportion reporting fit rating 3.")
        ]
    },
    {
        "title": "3. Category Eligibility Gates",
        "description": "Formal gatekeeper decisions checking sample size (n >= 40) and per-class thresholds before model fitting.",
        "files": [
            ("gate_boys.md", "Eligibility gate evaluation for BOYS cohort (Passed: Status FIT)."),
            ("gate_girls.md", "Eligibility gate evaluation for GIRLS cohort (Failed: Status NOT_FIT)."),
            ("gate_synth.md", "Eligibility gate check for synthetic / augmented data validation."),
            ("model_not_fitted_girls.md", "Formal documentation explaining why the Girls model could not be fitted and requirements for future surveys.")
        ]
    },
    {
        "title": "4. Demographics, Group Comparisons & Statistical Tests",
        "description": "Exploratory data analysis comparing Boys and Girls cohorts on sizes, heights, clothing, fit ratings, and hypothesis tests.",
        "files": [
            ("class_counts.csv", "Raw counts across discrete shirt sizes (32 to 44) by category."),
            ("tests_table.csv", "Statistical hypothesis tests (Welch's t-test, Mann-Whitney, Fisher exact, Monte Carlo Chi-Square)."),
            ("girls_size_dist.txt", "Shirt size distribution for the Girls cohort."),
            ("girls_height_summary.txt", "Mean and standard deviation of height for the Girls cohort."),
            ("girls_fit_rating.txt", "Self-reported fit rating distribution (1 to 5) for Girls."),
            ("girls_clothing.txt", "Clothing types worn during data collection by Girls."),
            ("girls_batch_dist.txt", "Observed sample vs expected frame distribution across batches for Girls."),
            ("girls_comparison_boys.txt", "Statistical comparison summary between Girls and Boys cohorts.")
        ]
    },
    {
        "title": "5. Morphological Pose Features",
        "description": "Summary statistics of extracted MediaPipe 2D silhouette, landmark distances, and torso proportions.",
        "files": [
            ("feature_summary.csv", "Descriptive statistics (mean, SD, min, max, percentiles) for all engineered biometric features.")
        ]
    },
    {
        "title": "6. Ground Truth Validation: Tape vs. Chart Agreement",
        "description": "Validation of self-reported shirt sizes against official manufacturer sizing charts derived from physical tape measurements.",
        "files": [
            ("tape_agreement_stats.txt", "Summary statistics, exact/within-one accuracy, Wilson CIs, quadratic weighted kappa, and TEM."),
            ("tape_agreement.csv", "Participant-level tape measurements (chest1, chest2, chart size, reported size, step differences) for all 19 participants."),
            ("tape_agreement_boys.csv", "Tape vs. chart agreement restricted to the Boys cohort (n=17).")
        ]
    },
    {
        "title": "7. Model Benchmarks & Evaluation (Boys Cohort)",
        "description": "Performance metrics, per-size recall, confusion matrices, standardized coefficients, feature importances, and sensitivity analyses.",
        "files": [
            ("model_results_boys.csv", "Comprehensive cross-validation benchmark results across models (B0, B1, M1, M2, M3) and evaluation targets."),
            ("per_size_recall_boys.csv", "Per-size recall rates with Wilson 95% confidence intervals across discrete sizes."),
            ("confusion_matrix_m2_boys.csv", "Confusion matrix for the headline regression model (M2 Ridge Size-Step)."),
            ("standard_coefs_m1_boys.csv", "Standardized regression coefficients for the primary feature model (M1)."),
            ("feature_importances_m3_boys.csv", "Random Forest / GBDT feature importance rankings for morphological predictors."),
            ("comparisons_boys.csv", "Formal model comparison table (M1 vs Baselines, delta metrics, confidence intervals)."),
            ("sensitivity_boys.csv", "Sensitivity analysis evaluating model robustness under loose/heavy clothing exclusions."),
            ("permutation_test.txt", "Permutation test p-value validating statistical significance of model predictions over chance.")
        ]
    },
    {
        "title": "8. Empirical Experiments: Sample Size & Design Comparison",
        "description": "Simulation studies investigating learning curves (performance vs sample size) and sampling design efficiency (SRSWOR vs Stratified).",
        "files": [
            ("experiment_partA.txt", "Learning curve simulation: Balanced accuracy and MAE as a function of training sample size (n=8 to 24)."),
            ("experiment_partB.txt", "Sampling design Monte Carlo simulation comparing SRSWOR, Stratified Proportional, and Stratified Equal designs.")
        ]
    }
]

def df_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(c) for c in df.columns]
    rows = [[str(v) if pd.notna(v) else "" for v in row] for row in df.values]
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    row_lines = ["| " + " | ".join(r[i].ljust(col_widths[i]) for i in range(len(headers))) + " |" for r in rows]
    return "\n".join([header_line, sep_line] + row_lines)

def slugify(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s_-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')

def build_summary_md():
    lines = []
    
    # Title & Metadata
    lines.append("# Master Summary of Output Tables & Data Artifacts\n")
    lines.append("> **Project:** Image-Based SSI Uniform Shirt-Size Estimation  ")
    lines.append("> **Directory:** `outputs/tables/`  ")
    lines.append("> **Scope:** Complete consolidated record of all 34 data audit tables, sampling design calculations, category gates, exploratory analyses, feature summaries, model benchmarks, and experiment results.\n")
    lines.append("---\n")
    
    # Table of Contents
    lines.append("## Table of Contents\n")
    for cat in CATEGORIES:
        cat_slug = slugify(cat['title'])
        lines.append(f"- [**{cat['title']}**](#{cat_slug})")
        for filename, desc in cat['files']:
            file_slug = slugify(filename)
            lines.append(f"  - [{filename}](#{file_slug}) — *{desc}*")
    lines.append("\n---\n")
    
    # Iterate Categories
    for cat in CATEGORIES:
        cat_slug = slugify(cat['title'])
        lines.append(f'<a id="{cat_slug}"></a>\n')
        lines.append(f"## {cat['title']}\n")
        lines.append(f"*{cat['description']}*\n")
        
        for filename, desc in cat['files']:
            file_path = TABLES_DIR / filename
            file_slug = slugify(filename)
            lines.append(f'<a id="{file_slug}"></a>\n')
            lines.append(f"### `{filename}`\n")
            lines.append(f"**Description:** {desc}  ")
            lines.append(f"**Source File:** [`outputs/tables/{filename}`](file:///{file_path.resolve().as_posix()})\n")
            
            if not file_path.exists():
                lines.append(f"> *Warning: File `{filename}` was not found in `outputs/tables/`.*\n")
                continue
                
            ext = file_path.suffix.lower()
            
            if ext == ".csv":
                try:
                    df = pd.read_csv(file_path)
                    lines.append(df_to_markdown(df))
                    lines.append(f"\n*Table dimension: {df.shape[0]} rows × {df.shape[1]} columns.*\n")
                except Exception as e:
                    lines.append(f"> *Error rendering CSV as markdown table: {e}*\n")
                    
            elif ext == ".md":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    # Indent or demote headers so document hierarchy remains intact
                    # Replace top level # with ####, ## with #####
                    adjusted_content = re.sub(r'^(#{1,3})\s', r'#\1 ', content, flags=re.MULTILINE)
                    lines.append(adjusted_content)
                    lines.append("\n")
                except Exception as e:
                    lines.append(f"> *Error reading markdown file: {e}*\n")
                    
            elif ext == ".txt":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    # Present as clean text block / table
                    lines.append("```text")
                    lines.append(content)
                    lines.append("```\n")
                except Exception as e:
                    lines.append(f"> *Error reading text file: {e}*\n")
                    
            lines.append("---\n")
            
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))
        
    print(f"Summary markdown successfully written to {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size} bytes).")

if __name__ == "__main__":
    build_summary_md()
