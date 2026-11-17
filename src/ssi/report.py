import os
import pandas as pd
from pathlib import Path

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().strip()

def format_df_md(df):
    if df.empty:
        return ""
    md = f"| {' | '.join(df.columns)} |\n"
    md += f"|{'|'.join(['---'] * len(df.columns))}|\n"
    for _, row in df.iterrows():
        row_str = ' | '.join(str(x) for x in row.values)
        md += f"| {row_str} |\n"
    return md

def main():
    Path("outputs/report").mkdir(parents=True, exist_ok=True)
    
    # Read tables and logs
    design_summ = read_file("outputs/tables/design_summary.txt")
    samp_summ = pd.read_csv("outputs/tables/sampling_summary.csv")
    
    # 2-3 sample questionnaires
    resp = pd.read_csv("data/interim/responses_valid.csv")
    sample_q = resp.head(3).copy()
    sample_q = sample_q.drop(columns=[c for c in sample_q.columns if 'file' in c.lower() or 'prn' in c.lower() or 'photo' in c.lower()], errors='ignore')
    
    md = f"""# 1. Title Page
**Project Title**: School Uniform Sizing and Measurement
**Organization**: Symbiosis Statistical Institute - Symbiosis International (Deemed University)
**Address**: Vishwabhavan Campus 3rd Floor, SCHC Building, Senapati Bapat Rd, Pune, Maharashtra 411004
**Submitted by**: <<FILL NAME>>, <<FILL PRN>>, <<FILL EMAIL>>
**Degree**: M.Sc. (Applied Statistics & Data Science)
**Academic Year**: 2025 - 2026
**Guide**: Dr. Madhulika Mishra, Assistant Professor, madhulika.mishra@ssi.edu.in

# 2. Acknowledgement
<<WRITE>> (150 to 200 words)

# 3. Introduction and Objective of the Survey
## Introduction
<<WRITE>> (200 to 250 words)

## Objective of the Survey
- **Main Objective**: Predict accurate school uniform sizes for students using morphological features extracted from photographs.
- **Specific Objectives**:
  - Extract morphological features (shoulder width, chest width, etc.) using MediaPipe Pose estimation.
  - Evaluate the reliability of self-measured tape dimensions against the official sizing chart.
  - Examine sample size requirements and the impact of different sampling designs (SRSWOR vs. Stratified) on coverage and error rates.

# 4. Sampling Design
{design_summ}

**Why it suits the survey**: The stratified approach ensures adequate representation of both Boys and Girls (as sizing charts differ strictly by category). SRSWOR provides unbiased estimates within these strata, and the reserve list handles non-response while maintaining randomization.

**Sample Size**: Total $n = 69$ (Target was at least 50 to 60).
**Reserve List Rule**: Replacements were drawn from the reserve list in pre-drawn randomized order.

### Sampling Summary Table
{format_df_md(samp_summ)}
<<WRITE INTERPRETATION>>

# 5. Questionnaire Design
The questionnaire comprises 15 items designed for clarity and logical flow:
1. **A1**: Timestamp
2. **A2**: Category (Boys/Girls)
3. **A3**: Age / Consent
4. **A4**: PRN (Removed for privacy)
5. **A5**: Email
6. **Q1**: Height (cm)
7. **Q2**: Reported Size
8. **Q3**: Fit Rating
9. **Q4**: Current Clothing
10. **Q5**: Batch
11. **Q6**: Chest Measurement 1 (cm)
12. **Q7**: Chest Measurement 2 (cm)
13. **Q8**: Shoulders (cm)
14. **Q9**: Photo Upload
15. **Q10**: Feedback / Notes

*Note: The questions logically progress from consent to demographics, followed by size and fit assessment, and finally physical measurements and photo upload. The full questionnaire is provided in the Appendix.*

# 6. Data Collection
- **Dates**: Offline station sessions conducted on 1, 5, and 6 October 2026.
- **Operators**: Field investigators taking photographs and assisting with tape measurements.
- **Outcomes**: Consented $n=69$.

### Practical Difficulties
<<WRITE>>

# 7. Data Analysis, Visualization and Interpretation

## 7.1 Tape Agreement (S10)
![Tape Agreement Table](../figures/report/tape_agreement_table.png)
<<WRITE INTERPRETATION>>

![Tape Agreement Scatter](../figures/report/tape_agreement_scatter.png)
<<WRITE INTERPRETATION>>

## 7.2 Modeling Boys (S7)
![Confusion Matrix](../figures/confusion_matrix_boys.png)
<<WRITE INTERPRETATION>>

## 7.3 Experiments and Simulations (S11)
![Learning Curve](../figures/experiment_partA_learning_curve.png)
<<WRITE INTERPRETATION>>

# 8. Result
<<WRITE>>

# 9. Challenges Faced and Future Scope
## Challenges Faced
<<WRITE>> (at least 100 words)

## Future Scope
<<WRITE>> (at least 100 words)

# 10. Bibliography
1. Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). John Wiley & Sons.
2. Lohr, S. L. (2019). *Sampling: Design and Analysis* (3rd ed.). CRC Press.
3. MediaPipe Developers. (2023). *MediaPipe Pose*. Google.
4. scikit-learn developers. (2023). *scikit-learn: Machine Learning in Python*.
5. Singh, D., & Chaudhary, F. S. (2003). *Theory and Analysis of Sample Survey Designs*. New Age International.

# 11. Appendix
## Questionnaire
(Full questionnaire text provided separately)

## Sample Questionnaires (Filled)
{format_df_md(sample_q)}

## Codebook & Draw Log
(Provided in accompanying data files)
"""
    with open("outputs/report/report_skeleton.md", "w") as f:
        f.write(md)
        
if __name__ == '__main__':
    main()
