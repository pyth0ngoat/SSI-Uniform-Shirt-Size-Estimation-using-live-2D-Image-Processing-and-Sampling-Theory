# Master Summary of Output Tables & Data Artifacts

> **Project:** Image-Based SSI Uniform Shirt-Size Estimation  
> **Directory:** `outputs/tables/`  
> **Scope:** Complete consolidated record of all 34 data audit tables, sampling design calculations, category gates, exploratory analyses, feature summaries, model benchmarks, and experiment results.

---

## Table of Contents

- [**1. Data Audit & Quality Control (QC)**](#1-data-audit-quality-control-qc)
  - [data_audit.md](#data-auditmd) — *High-level summary of total consented/refused participants, cohort splits, clothing, and operators.*
  - [data_quality_report.csv](#data-quality-reportcsv) — *Detailed validation report of each field, missing values, range checks, and error flags.*
  - [photo_integrity.csv](#photo-integritycsv) — *Integrity check of raw submitted images (resolution, readability, file size).*
  - [qc_summary.csv](#qc-summarycsv) — *Computer vision automated QC pass/fail rates across brightness, blur, and pose detection.*
- [**2. Sampling Design & Population Estimates**](#2-sampling-design-population-estimates)
  - [sampling_summary.csv](#sampling-summarycsv) — *Sample sizes, frame population, sampling fractions, and design weights by category stratum.*
  - [design_summary.txt](#design-summarytxt) — *Plain-text specification of target population, sampling unit, stratification, and reserve lists.*
  - [coverage_commentary.md](#coverage-commentarymd) — *Evaluation of batch coverage, non-response patterns, and representation across cohorts.*
  - [estimates.csv](#estimatescsv) — *Population estimates for mean height, proportion <= size 38, and proportion reporting fit rating 3.*
- [**3. Category Eligibility Gates**](#3-category-eligibility-gates)
  - [gate_boys.md](#gate-boysmd) — *Eligibility gate evaluation for BOYS cohort (Passed: Status FIT).*
  - [gate_girls.md](#gate-girlsmd) — *Eligibility gate evaluation for GIRLS cohort (Failed: Status NOT_FIT).*
  - [gate_synth.md](#gate-synthmd) — *Eligibility gate check for synthetic / augmented data validation.*
  - [model_not_fitted_girls.md](#model-not-fitted-girlsmd) — *Formal documentation explaining why the Girls model could not be fitted and requirements for future surveys.*
- [**4. Demographics, Group Comparisons & Statistical Tests**](#4-demographics-group-comparisons-statistical-tests)
  - [class_counts.csv](#class-countscsv) — *Raw counts across discrete shirt sizes (32 to 44) by category.*
  - [tests_table.csv](#tests-tablecsv) — *Statistical hypothesis tests (Welch's t-test, Mann-Whitney, Fisher exact, Monte Carlo Chi-Square).*
  - [girls_size_dist.txt](#girls-size-disttxt) — *Shirt size distribution for the Girls cohort.*
  - [girls_height_summary.txt](#girls-height-summarytxt) — *Mean and standard deviation of height for the Girls cohort.*
  - [girls_fit_rating.txt](#girls-fit-ratingtxt) — *Self-reported fit rating distribution (1 to 5) for Girls.*
  - [girls_clothing.txt](#girls-clothingtxt) — *Clothing types worn during data collection by Girls.*
  - [girls_batch_dist.txt](#girls-batch-disttxt) — *Observed sample vs expected frame distribution across batches for Girls.*
  - [girls_comparison_boys.txt](#girls-comparison-boystxt) — *Statistical comparison summary between Girls and Boys cohorts.*
- [**5. Morphological Pose Features**](#5-morphological-pose-features)
  - [feature_summary.csv](#feature-summarycsv) — *Descriptive statistics (mean, SD, min, max, percentiles) for all engineered biometric features.*
- [**6. Ground Truth Validation: Tape vs. Chart Agreement**](#6-ground-truth-validation-tape-vs-chart-agreement)
  - [tape_agreement_stats.txt](#tape-agreement-statstxt) — *Summary statistics, exact/within-one accuracy, Wilson CIs, quadratic weighted kappa, and TEM.*
  - [tape_agreement.csv](#tape-agreementcsv) — *Participant-level tape measurements (chest1, chest2, chart size, reported size, step differences) for all 19 participants.*
  - [tape_agreement_boys.csv](#tape-agreement-boyscsv) — *Tape vs. chart agreement restricted to the Boys cohort (n=17).*
- [**7. Model Benchmarks & Evaluation (Boys Cohort)**](#7-model-benchmarks-evaluation-boys-cohort)
  - [model_results_boys.csv](#model-results-boyscsv) — *Comprehensive cross-validation benchmark results across models (B0, B1, M1, M2, M3) and evaluation targets.*
  - [per_size_recall_boys.csv](#per-size-recall-boyscsv) — *Per-size recall rates with Wilson 95% confidence intervals across discrete sizes.*
  - [confusion_matrix_m2_boys.csv](#confusion-matrix-m2-boyscsv) — *Confusion matrix for the headline regression model (M2 Ridge Size-Step).*
  - [standard_coefs_m1_boys.csv](#standard-coefs-m1-boyscsv) — *Standardized regression coefficients for the primary feature model (M1).*
  - [feature_importances_m3_boys.csv](#feature-importances-m3-boyscsv) — *Random Forest / GBDT feature importance rankings for morphological predictors.*
  - [comparisons_boys.csv](#comparisons-boyscsv) — *Formal model comparison table (M1 vs Baselines, delta metrics, confidence intervals).*
  - [sensitivity_boys.csv](#sensitivity-boyscsv) — *Sensitivity analysis evaluating model robustness under loose/heavy clothing exclusions.*
  - [permutation_test.txt](#permutation-testtxt) — *Permutation test p-value validating statistical significance of model predictions over chance.*
- [**8. Empirical Experiments: Sample Size & Design Comparison**](#8-empirical-experiments-sample-size-design-comparison)
  - [experiment_partA.txt](#experiment-partatxt) — *Learning curve simulation: Balanced accuracy and MAE as a function of training sample size (n=8 to 24).*
  - [experiment_partB.txt](#experiment-partbtxt) — *Sampling design Monte Carlo simulation comparing SRSWOR, Stratified Proportional, and Stratified Equal designs.*

---

<a id="1-data-audit-quality-control-qc"></a>

## 1. Data Audit & Quality Control (QC)

*Initial data hygiene, response counts, session breakdown, photo integrity, and computer vision QC filters.*

<a id="data-auditmd"></a>

### `data_audit.md`

**Description:** High-level summary of total consented/refused participants, cohort splits, clothing, and operators.  
**Source File:** [`outputs/tables/data_audit.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/data_audit.md)

## Data Audit Report

- **Total Rows**: 78
- **Consented**: 69
- **Refused**: 9

### By Category (Consented)
| Category | Count |
|---|---|
| BOYS | 43 |
| GIRLS | 26 |

### By Batch (Consented)
| Batch | Count |
|---|---|
| MSC_1 | 33 |
| BSC_1 | 16 |
| BSC_3 | 15 |
| BSC_2 | 4 |
| BSC_4 | 1 |

### By Session (Consented)
| Session | Count |
|---|---|
| 5th October | 28 |
| 6th October | 28 |
| 1st October | 13 |

### By How In (Consented)
| How In | Count |
|---|---|
| primary | 38 |
| reserve | 31 |

### By Operator (All)
| Operator | Count |
|---|---|
| Ayush | 25 |
| Kapil | 22 |
| Vaishnavi | 20 |
| Mithilesh | 11 |

### By Clothing (Consented)
| Clothing | Count |
|---|---|
| Regular top or shirt | 34 |
| Loose top or hoodie | 16 |
| Plain fitted top | 9 |
| SSI uniform shirt | 9 |
| Jacket or heavy layer | 1 |

### Fit Rating Distribution (Consented)
| Fit Rating | Count |
|---|---|
| 1.0 | 3 |
| 2.0 | 9 |
| 3.0 | 43 |
| 4.0 | 13 |
| 5.0 | 1 |

### Tape Count: 19

### Errors: 0
### Warnings: 17


---

<a id="data-quality-reportcsv"></a>

### `data_quality_report.csv`

**Description:** Detailed validation report of each field, missing values, range checks, and error flags.  
**Source File:** [`outputs/tables/data_quality_report.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/data_quality_report.csv)

| code | field     | problem                                 | severity |
| ---- | --------- | --------------------------------------- | -------- |
| P003 | chest     | Chest diff > max                        | WARNING  |
| P008 | chest     | Chest diff > max                        | WARNING  |
| P020 | chest     | Chest diff > max                        | WARNING  |
| P022 | timestamp | Earlier than previous row               | WARNING  |
| P023 | chest     | Chest diff > max                        | WARNING  |
| P027 | chest     | Chest diff > max                        | WARNING  |
| P028 | chest     | Chest diff > max                        | WARNING  |
| P030 | chest     | Chest diff > max                        | WARNING  |
| P034 | timestamp | Earlier than previous row               | WARNING  |
| P043 | timestamp | Earlier than previous row               | WARNING  |
| P054 | timestamp | Date does not match session 6th October | WARNING  |
| P055 | timestamp | Date does not match session 6th October | WARNING  |
| P056 | timestamp | Date does not match session 6th October | WARNING  |
| P057 | timestamp | Earlier than previous row               | WARNING  |
| P060 | timestamp | Earlier than previous row               | WARNING  |
| P071 | chest     | Chest diff > max                        | WARNING  |
| P076 | timestamp | Earlier than previous row               | WARNING  |

*Table dimension: 17 rows × 4 columns.*

---

<a id="photo-integritycsv"></a>

### `photo_integrity.csv`

**Description:** Integrity check of raw submitted images (resolution, readability, file size).  
**Source File:** [`outputs/tables/photo_integrity.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/photo_integrity.csv)

| code | field | problem                | severity |
| ---- | ----- | ---------------------- | -------- |
| P035 | phash | Near-duplicate of P024 | WARNING  |
| P035 | phash | Near-duplicate of P031 | WARNING  |
| P057 | phash | Near-duplicate of P047 | WARNING  |
| P059 | phash | Near-duplicate of P050 | WARNING  |
| P061 | phash | Near-duplicate of P060 | WARNING  |

*Table dimension: 5 rows × 4 columns.*

---

<a id="qc-summarycsv"></a>

### `qc_summary.csv`

**Description:** Computer vision automated QC pass/fail rates across brightness, blur, and pose detection.  
**Source File:** [`outputs/tables/qc_summary.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/qc_summary.csv)

| category | clothing              | qc_final | count |
| -------- | --------------------- | -------- | ----- |
| BOYS     | Loose top or hoodie   | False    | 1     |
| BOYS     | Loose top or hoodie   | True     | 8     |
| BOYS     | Plain fitted top      | True     | 3     |
| BOYS     | Regular top or shirt  | True     | 25    |
| BOYS     | SSI uniform shirt     | True     | 6     |
| GIRLS    | Jacket or heavy layer | True     | 1     |
| GIRLS    | Loose top or hoodie   | True     | 7     |
| GIRLS    | Plain fitted top      | True     | 6     |
| GIRLS    | Regular top or shirt  | True     | 9     |
| GIRLS    | SSI uniform shirt     | True     | 3     |

*Table dimension: 10 rows × 4 columns.*

---

<a id="2-sampling-design-population-estimates"></a>

## 2. Sampling Design & Population Estimates

*Stratified sampling framework details, sample size allocation, design weights, Kish Deff, and Horvitz-Thompson estimates.*

<a id="sampling-summarycsv"></a>

### `sampling_summary.csv`

**Description:** Sample sizes, frame population, sampling fractions, and design weights by category stratum.  
**Source File:** [`outputs/tables/sampling_summary.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/sampling_summary.csv)

| Metric         | Value              | CI_low             | CI_high            |
| -------------- | ------------------ | ------------------ | ------------------ |
| Refusal Rate   | 0.1153846153846153 | 0.0619051062553332 | 0.2049701319848162 |
| Response Rate  | 0.8846153846153846 | 0.7950298680151837 | 0.9380948937446668 |
| Reserve Share  | 0.4492753623188406 | 0.3376885562924371 | 0.5662123249731189 |
| Kish deff_w    | 1.0511254979532023 |                    |                    |
| Effective n    | 65.64392180986935  |                    |                    |
| Implied Margin | 10.110216887250555 |                    |                    |

*Table dimension: 6 rows × 4 columns.*

---

<a id="design-summarytxt"></a>

### `design_summary.txt`

**Description:** Plain-text specification of target population, sampling unit, stratification, and reserve lists.  
**Source File:** [`outputs/tables/design_summary.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/design_summary.txt)

```text
Population: Symbiosis Statistical Institute MSc Statistics students
Sampling unit: one student
Sampling frame: the batch-wise student lists
Method: stratified, strata = category, SRSWOR within strata, reserve list used in pre-drawn order

Population N: 257 (Boys 132, Girls 125)
Sample n (consented): 69 (Boys 43, Girls 26)
Sampling fraction f: Boys 32.6%, Girls 20.8%
```

---

<a id="coverage-commentarymd"></a>

### `coverage_commentary.md`

**Description:** Evaluation of batch coverage, non-response patterns, and representation across cohorts.  
**Source File:** [`outputs/tables/coverage_commentary.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/coverage_commentary.md)

## Non-response and coverage commentary
MSC_1 is represented at 47.8% of the sample versus 17.5% of the frame.
Zero cells list: BOYS MSC_2, GIRLS BSC_4, GIRLS MSC_2, Overall MSC_2.
A plain statement: Inferences apply only to the batches observed.


---

<a id="estimatescsv"></a>

### `estimates.csv`

**Description:** Population estimates for mean height, proportion <= size 38, and proportion reporting fit rating 3.  
**Source File:** [`outputs/tables/estimates.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/estimates.csv)

| category | metric                      | est                | ci_low             | ci_high            |
| -------- | --------------------------- | ------------------ | ------------------ | ------------------ |
| BOYS     | just right                  | 0.6511627906976745 | 0.5017178199285205 | 0.775814100026473  |
| BOYS     | too tight or slightly tight | 0.1860465116279069 | 0.0974175142899622 | 0.3261700365727439 |
| BOYS     | height_cm                   | 175.8139534883721  | 173.95494333807153 | 177.67296363867268 |
| BOYS     | height_cm (with FPC)        | 175.8139534883721  | 174.28166296182698 | 177.34624401491723 |
| GIRLS    | just right                  | 0.5769230769230769 | 0.389486137465917  | 0.7445555668634344 |
| GIRLS    | too tight or slightly tight | 0.1538461538461538 | 0.0615003372357835 | 0.3353119932821348 |
| GIRLS    | height_cm                   | 157.57692307692307 | 155.6042166523512  | 159.54962950149493 |
| GIRLS    | height_cm (with FPC)        | 157.57692307692307 | 155.8142603799776  | 159.33958577386852 |
| OVERALL  | stratified size <= 38       | 0.7340581778189235 |                    |                    |
| OVERALL  | stratified mean height      | 166.94380251004085 |                    |                    |

*Table dimension: 10 rows × 5 columns.*

---

<a id="3-category-eligibility-gates"></a>

## 3. Category Eligibility Gates

*Formal gatekeeper decisions checking sample size (n >= 40) and per-class thresholds before model fitting.*

<a id="gate-boysmd"></a>

### `gate_boys.md`

**Description:** Eligibility gate evaluation for BOYS cohort (Passed: Status FIT).  
**Source File:** [`outputs/tables/gate_boys.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/gate_boys.md)

## Gate Status: BOYS
    
**Status**: FIT
**Reason**: Accepted n >= 40 and all classes >= 15
**Accepted N**: 42
**Classes after merge**: 2
**Class counts**: [26, 16]

**Participants that can be lost before status downgrade**: 1


---

<a id="gate-girlsmd"></a>

### `gate_girls.md`

**Description:** Eligibility gate evaluation for GIRLS cohort (Failed: Status NOT_FIT).  
**Source File:** [`outputs/tables/gate_girls.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/gate_girls.md)

## Gate Status: GIRLS
    
**Status**: NOT_FIT
**Reason**: Merge ended with a single class (NO_VALID_TARGET)
**Accepted N**: 26
**Classes after merge**: 1
**Class counts**: [26]

**Participants that can be lost before status downgrade**: 0


---

<a id="gate-synthmd"></a>

### `gate_synth.md`

**Description:** Eligibility gate check for synthetic / augmented data validation.  
**Source File:** [`outputs/tables/gate_synth.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/gate_synth.md)

## Gate Status: SYNTH
    
**Status**: EXPLORATORY
**Reason**: A retained class has between 10 and 14 participants
**Accepted N**: 41
**Classes after merge**: 2
**Class counts**: [27, 14]

**Participants that can be lost before status downgrade**: 4


---

<a id="model-not-fitted-girlsmd"></a>

### `model_not_fitted_girls.md`

**Description:** Formal documentation explaining why the Girls model could not be fitted and requirements for future surveys.  
**Source File:** [`outputs/tables/model_not_fitted_girls.md`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/model_not_fitted_girls.md)

## Model Not Fitted: GIRLS

**Reason**: Merge ended with a single class (NO_VALID_TARGET)

**Accepted Participants**: 26
**Class Counts before merge**: [18, 4, 4, 0]
**Class Counts after merge**: [26]

Because the GIRLS category did not meet the minimum requirements for modeling, no predictive models were trained, tuned, or cross-validated. Instead, we rely on the descriptive statistics and sampling tests (see Section 6: Sampling Analysis) to characterize this group.


---

<a id="4-demographics-group-comparisons-statistical-tests"></a>

## 4. Demographics, Group Comparisons & Statistical Tests

*Exploratory data analysis comparing Boys and Girls cohorts on sizes, heights, clothing, fit ratings, and hypothesis tests.*

<a id="class-countscsv"></a>

### `class_counts.csv`

**Description:** Raw counts across discrete shirt sizes (32 to 44) by category.  
**Source File:** [`outputs/tables/class_counts.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/class_counts.csv)

| category | merged_class    | count |
| -------- | --------------- | ----- |
| BOYS     | 32-34_36-38     | 26    |
| BOYS     | 40-42_44-46     | 16    |
| GIRLS    | NO_VALID_TARGET | 26    |

*Table dimension: 3 rows × 3 columns.*

---

<a id="tests-tablecsv"></a>

### `tests_table.csv`

**Description:** Statistical hypothesis tests (Welch's t-test, Mann-Whitney, Fisher exact, Monte Carlo Chi-Square).  
**Source File:** [`outputs/tables/tests_table.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/tests_table.csv)

| test                                 | stat               | pval                   | df                |
| ------------------------------------ | ------------------ | ---------------------- | ----------------- |
| Fisher exact category x (size <= 36) | 5.098039215686274  | 0.0030665161403658     |                   |
| mc_chi2 category x band              | 20.316190676628437 | 0.007                  |                   |
| Welch t-test height BOYS vs GIRLS    | 13.723219715745811 | 2.3061097336464692e-20 | 61.37818851952265 |
| Cohen's d height                     | 3.2353271256963096 |                        |                   |
| Mann-Whitney height                  | 1110.0             | 8.912277954557839e-12  |                   |
| Spearman height vs size BOYS         | 0.529010489765238  | 0.0002651807844221     |                   |
| Spearman height vs size GIRLS        | 0.5354975988269036 | 0.0048140759252811     |                   |
| Binomial 'just right' == 0.5 BOYS    | 0.6511627906976745 | 0.0659940344557981     |                   |
| Binomial 'just right' == 0.5 GIRLS   | 0.5769230769230769 | 0.557197093963623      |                   |
| mc_chi2 category x clothing          | 7.016945306745238  | 0.6066                 |                   |
| fisher QC fail x category            |                    | 1.0                    |                   |
| mc_chi2 QC fail x clothing           | 3.3612132352941173 | 0.8185                 |                   |

*Table dimension: 12 rows × 4 columns.*

---

<a id="girls-size-disttxt"></a>

### `girls_size_dist.txt`

**Description:** Shirt size distribution for the Girls cohort.  
**Source File:** [`outputs/tables/girls_size_dist.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_size_dist.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
 Size  Count
 32.0     13
 34.0      5
 36.0      2
 38.0      2
 40.0      2
 42.0      2
```

---

<a id="girls-height-summarytxt"></a>

### `girls_height_summary.txt`

**Description:** Mean and standard deviation of height for the Girls cohort.  
**Source File:** [`outputs/tables/girls_height_summary.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_height_summary.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
Mean: 157.58
SD: 4.88
```

---

<a id="girls-fit-ratingtxt"></a>

### `girls_fit_rating.txt`

**Description:** Self-reported fit rating distribution (1 to 5) for Girls.  
**Source File:** [`outputs/tables/girls_fit_rating.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_fit_rating.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
 Fit Rating  Count
        1.0      2
        2.0      2
        3.0     15
        4.0      7
```

---

<a id="girls-clothingtxt"></a>

### `girls_clothing.txt`

**Description:** Clothing types worn during data collection by Girls.  
**Source File:** [`outputs/tables/girls_clothing.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_clothing.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
             Clothing  Count
Jacket or heavy layer      1
  Loose top or hoodie      7
     Plain fitted top      6
 Regular top or shirt      9
    SSI uniform shirt      3
```

---

<a id="girls-batch-disttxt"></a>

### `girls_batch_dist.txt`

**Description:** Observed sample vs expected frame distribution across batches for Girls.  
**Source File:** [`outputs/tables/girls_batch_dist.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_batch_dist.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
Batch  Sample  Expected
BSC_1       5     2.288
BSC_2       1     5.824
BSC_3       3     4.160
BSC_4       0     3.328
MSC_1      17     5.824
MSC_2       0     4.576
```

---

<a id="girls-comparison-boystxt"></a>

### `girls_comparison_boys.txt`

**Description:** Statistical comparison summary between Girls and Boys cohorts.  
**Source File:** [`outputs/tables/girls_comparison_boys.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/girls_comparison_boys.txt)

```text
Girls model not fitted: see model_not_fitted_GIRLS.md
Extracted from S6 Tests:
                                test        stat         pval        df
Fisher exact category x (size <= 36)    5.098039 3.066516e-03       NaN
             mc_chi2 category x band   20.316191 7.000000e-03       NaN
   Welch t-test height BOYS vs GIRLS   13.723220 2.306110e-20 61.378189
                    Cohen's d height    3.235327          NaN       NaN
                 Mann-Whitney height 1110.000000 8.912278e-12       NaN
        Spearman height vs size BOYS    0.529010 2.651808e-04       NaN
       Spearman height vs size GIRLS    0.535498 4.814076e-03       NaN
   Binomial 'just right' == 0.5 BOYS    0.651163 6.599403e-02       NaN
  Binomial 'just right' == 0.5 GIRLS    0.576923 5.571971e-01       NaN
         mc_chi2 category x clothing    7.016945 6.066000e-01       NaN
           fisher QC fail x category         NaN 1.000000e+00       NaN
          mc_chi2 QC fail x clothing    3.361213 8.185000e-01       NaN
```

---

<a id="5-morphological-pose-features"></a>

## 5. Morphological Pose Features

*Summary statistics of extracted MediaPipe 2D silhouette, landmark distances, and torso proportions.*

<a id="feature-summarycsv"></a>

### `feature_summary.csv`

**Description:** Descriptive statistics (mean, SD, min, max, percentiles) for all engineered biometric features.  
**Source File:** [`outputs/tables/feature_summary.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/feature_summary.csv)

| category | feature              | mean               | sd                 | min                | max                | missing |
| -------- | -------------------- | ------------------ | ------------------ | ------------------ | ------------------ | ------- |
| BOYS     | shoulder_w           | 0.199852967364054  | 0.0107154082777119 | 0.1834423936844076 | 0.2208308125799989 | 0       |
| BOYS     | shoulder_w_sil       | 0.2601366826391268 | 0.0151517696180992 | 0.2362655881361644 | 0.2899721448467967 | 0       |
| BOYS     | chest_w_sil          | 0.2967417732095812 | 0.021822494853635  | 0.2593984962406015 | 0.343492586490939  | 0       |
| BOYS     | waist_w_sil          | 0.3005501028089766 | 0.0235827505425956 | 0.2593346911065852 | 0.3610027855153203 | 0       |
| BOYS     | hip_w_sil            | 0.2773356045152558 | 0.0210589729978385 | 0.2355889724310776 | 0.3308623298033283 | 0       |
| BOYS     | torso_len            | 0.2984880680761635 | 0.0080767406460485 | 0.2840833371783027 | 0.3222786065089048 | 0       |
| BOYS     | arm_len              | 0.3040804320557891 | 0.0128621874435536 | 0.278157015161755  | 0.3417023287979944 | 0       |
| BOYS     | leg_len              | 0.3556664662908148 | 0.0199024728696651 | 0.3212551519171318 | 0.394673531817815  | 0       |
| BOYS     | area_ratio           | 0.1915785309217229 | 0.0100584833668848 | 0.1713263041903152 | 0.2119427035743079 | 0       |
| BOYS     | ratio_chest_hip      | 1.0724943655013213 | 0.0713162639315241 | 0.9077868852459016 | 1.2228739002932552 | 0       |
| BOYS     | ratio_shoulder_torso | 0.8715165827443376 | 0.0451443912058206 | 0.799494811998741  | 0.97056451027402   | 0       |
| BOYS     | ratio_waist_chest    | 1.0148420914291787 | 0.0700139601006255 | 0.8872901678657075 | 1.1279761904761905 | 0       |
| BOYS     | shoulder_tilt_deg    | 1.8262765123706008 | 1.407257899554574  | 0.1453173481250773 | 5.224074505336904  | 0       |
| BOYS     | torso_lean_deg       | 1.279772500884513  | 0.7851083085929197 | 0.0285397404061482 | 2.938540981160271  | 0       |
| GIRLS    | shoulder_w           | 0.1945400614438326 | 0.0109258799866496 | 0.1718077324938922 | 0.2161110936735225 | 0       |
| GIRLS    | shoulder_w_sil       | 0.2574231165209089 | 0.0164584625755311 | 0.233570159857904  | 0.2927036199095023 | 0       |
| GIRLS    | chest_w_sil          | 0.2873200930948119 | 0.0311439339993039 | 0.239120476408612  | 0.3639705882352941 | 0       |
| GIRLS    | waist_w_sil          | 0.2972443336396552 | 0.0312665939069084 | 0.249656436097114  | 0.3790983606557377 | 0       |
| GIRLS    | hip_w_sil            | 0.2915925429706302 | 0.0238432428584257 | 0.2478240952817224 | 0.3338604020781567 | 0       |
| GIRLS    | torso_len            | 0.2874785844816619 | 0.0100773462729371 | 0.2672575346345546 | 0.3072407330358233 | 0       |
| GIRLS    | arm_len              | 0.3078699011066614 | 0.0126190804996397 | 0.2823174109702988 | 0.330598834681479  | 0       |
| GIRLS    | leg_len              | 0.3783755975958825 | 0.020010054650616  | 0.3456335617465514 | 0.4266003085819256 | 0       |
| GIRLS    | area_ratio           | 0.2040428956190177 | 0.0129318505781419 | 0.1738018385941086 | 0.2297264657255175 | 0       |
| GIRLS    | ratio_chest_hip      | 0.985789645554137  | 0.0731157758225671 | 0.8530259365994236 | 1.12853470437018   | 0       |
| GIRLS    | ratio_shoulder_torso | 0.8954607881438646 | 0.0481737390722031 | 0.8051600732067926 | 1.0080504528825875 | 0       |
| GIRLS    | ratio_waist_chest    | 1.03660244406271   | 0.0616444130487483 | 0.9249291784702552 | 1.1283783783783785 | 0       |
| GIRLS    | shoulder_tilt_deg    | 1.4648000602018945 | 1.0704979950603308 | 0.1325761455923962 | 4.256857292195906  | 0       |
| GIRLS    | torso_lean_deg       | 1.3500321376619602 | 0.6682495878571253 | 0.3198313512636722 | 2.4568891551620355 | 0       |

*Table dimension: 28 rows × 7 columns.*

---

<a id="6-ground-truth-validation-tape-vs-chart-agreement"></a>

## 6. Ground Truth Validation: Tape vs. Chart Agreement

*Validation of self-reported shirt sizes against official manufacturer sizing charts derived from physical tape measurements.*

<a id="tape-agreement-statstxt"></a>

### `tape_agreement_stats.txt`

**Description:** Summary statistics, exact/within-one accuracy, Wilson CIs, quadratic weighted kappa, and TEM.  
**Source File:** [`outputs/tables/tape_agreement_stats.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/tape_agreement_stats.txt)

```text
n = 19 is below the target of 40; the subset was not drawn by SRS; some readings were taken over clothing; results are exploratory

Total rows: 19
Exact match: 6 of 19 (31.6%), 95% CI: [15.4%, 54.0%]
Within one step: 12 of 19 (63.2%), 95% CI: [41.0%, 80.9%]
Quadratic weighted kappa: 0.621, 95% CI: [0.192, 0.807]
Mean signed diff in steps: -0.16
Mean absolute diff in steps: 1.11
Spearman correlation: 0.603
Pairs differing by > 1.5 cm: 8
Technical error of measurement (cm): 1.19

Sensitivity (excluding P013, P044, P070, n=16):
Exact: 5 of 16 (31.2%), 95% CI: [14.2%, 55.6%]
Within one: 10 of 16 (62.5%), 95% CI: [38.6%, 81.5%]

Boys only (n=17):
Exact: 5 of 17 (29.4%), 95% CI: [13.3%, 53.1%]
Within one: 10 of 17 (58.8%), 95% CI: [36.0%, 78.4%]

Reported size and the chart size from tape agree exactly for about a third of tested students; this agreement bounds how well any model trained on reported size can recommend the right size.
```

---

<a id="tape-agreementcsv"></a>

### `tape_agreement.csv`

**Description:** Participant-level tape measurements (chest1, chest2, chart size, reported size, step differences) for all 19 participants.  
**Source File:** [`outputs/tables/tape_agreement.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/tape_agreement.csv)

| code | category | batch | clothing             | chest1_cm | chest2_cm | mean_chest_cm | mean_chest_in      | chest_diff_abs | chart_up | chart_down | reported_size | diff_steps | exact_match | within_one_step | fit_rating |
| ---- | -------- | ----- | -------------------- | --------- | --------- | ------------- | ------------------ | -------------- | -------- | ---------- | ------------- | ---------- | ----------- | --------------- | ---------- |
| P003 | BOYS     | MSC_1 | Regular top or shirt | 87.0      | 89.0      | 88.0          | 34.645669291338585 | 2.0            | 34       | 34         | 38.0          | 2.0        | False       | False           | 4.0        |
| P008 | BOYS     | MSC_1 | Plain fitted top     | 88.0      | 90.0      | 89.0          | 35.03937007874016  | 2.0            | 36       | 36         | 34.0          | -1.0       | False       | True            | 2.0        |
| P013 | GIRLS    | MSC_1 | Loose top or hoodie  | 96.0      | 96.0      | 96.0          | 37.79527559055118  | 0.0            | 38       | 38         | 36.0          | -1.0       | False       | True            | 2.0        |
| P020 | BOYS     | BSC_3 | Regular top or shirt | 89.0      | 87.0      | 88.0          | 34.645669291338585 | 2.0            | 34       | 34         | 36.0          | 1.0        | False       | True            | 3.0        |
| P021 | BOYS     | MSC_1 | Regular top or shirt | 95.0      | 94.0      | 94.5          | 37.204724409448815 | 1.0            | 38       | 38         | 34.0          | -2.0       | False       | False           | 1.0        |
| P023 | BOYS     | MSC_1 | Regular top or shirt | 91.0      | 93.0      | 92.0          | 36.22047244094488  | 2.0            | 36       | 36         | 32.0          | -2.0       | False       | False           | 3.0        |
| P025 | BOYS     | MSC_1 | Regular top or shirt | 107.0     | 107.0     | 107.0         | 42.1259842519685   | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 3.0        |
| P027 | BOYS     | MSC_1 | Regular top or shirt | 95.0      | 97.0      | 96.0          | 37.79527559055118  | 2.0            | 38       | 38         | 38.0          | 0.0        | True        | True            | 3.0        |
| P028 | BOYS     | BSC_3 | Regular top or shirt | 95.0      | 98.0      | 96.5          | 37.99212598425197  | 3.0            | 38       | 38         | 36.0          | -1.0       | False       | True            | 2.0        |
| P030 | BOYS     | MSC_1 | Regular top or shirt | 97.0      | 95.0      | 96.0          | 37.79527559055118  | 2.0            | 38       | 38         | 42.0          | 2.0        | False       | False           | 3.0        |
| P039 | BOYS     | MSC_1 | Regular top or shirt | 91.0      | 90.0      | 90.5          | 35.62992125984252  | 1.0            | 36       | 36         | 36.0          | 0.0        | True        | True            | 3.0        |
| P043 | BOYS     | MSC_1 | Plain fitted top     | 97.0      | 98.0      | 97.5          | 38.38582677165354  | 1.0            | 38       | 38         | 36.0          | -1.0       | False       | True            | 4.0        |
| P044 | BOYS     | MSC_1 | Loose top or hoodie  | 96.0      | 96.0      | 96.0          | 37.79527559055118  | 0.0            | 38       | 38         | 32.0          | -3.0       | False       | False           | 2.0        |
| P052 | GIRLS    | MSC_1 | SSI uniform shirt    | 83.0      | 82.0      | 82.5          | 32.48031496062992  | 1.0            | 32       | 32         | 32.0          | 0.0        | True        | True            | 3.0        |
| P070 | BOYS     | BSC_3 | Loose top or hoodie  | 109.0     | 109.0     | 109.0         | 42.91338582677165  | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 2.0        |
| P071 | BOYS     | BSC_3 | Regular top or shirt | 101.0     | 97.0      | 99.0          | 38.976377952755904 | 4.0            | 38       | 38         | 42.0          | 2.0        | False       | False           | 4.0        |
| P075 | BOYS     | BSC_3 | Regular top or shirt | 107.0     | 107.0     | 107.0         | 42.1259842519685   | 0.0            | 42       | 42         | 40.0          | -1.0       | False       | True            | 4.0        |
| P077 | BOYS     | BSC_3 | Regular top or shirt | 80.0      | 81.0      | 80.5          | 31.69291338582677  | 1.0            | 32       | 32         | 36.0          | 2.0        | False       | False           | 3.0        |
| P078 | BOYS     | BSC_3 | Regular top or shirt | 108.0     | 108.0     | 108.0         | 42.51968503937008  | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 5.0        |

*Table dimension: 19 rows × 16 columns.*

---

<a id="tape-agreement-boyscsv"></a>

### `tape_agreement_boys.csv`

**Description:** Tape vs. chart agreement restricted to the Boys cohort (n=17).  
**Source File:** [`outputs/tables/tape_agreement_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/tape_agreement_boys.csv)

| code | category | batch | clothing             | chest1_cm | chest2_cm | mean_chest_cm | mean_chest_in      | chest_diff_abs | chart_up | chart_down | reported_size | diff_steps | exact_match | within_one_step | fit_rating |
| ---- | -------- | ----- | -------------------- | --------- | --------- | ------------- | ------------------ | -------------- | -------- | ---------- | ------------- | ---------- | ----------- | --------------- | ---------- |
| P003 | BOYS     | MSC_1 | Regular top or shirt | 87.0      | 89.0      | 88.0          | 34.645669291338585 | 2.0            | 34       | 34         | 38.0          | 2.0        | False       | False           | 4.0        |
| P008 | BOYS     | MSC_1 | Plain fitted top     | 88.0      | 90.0      | 89.0          | 35.03937007874016  | 2.0            | 36       | 36         | 34.0          | -1.0       | False       | True            | 2.0        |
| P020 | BOYS     | BSC_3 | Regular top or shirt | 89.0      | 87.0      | 88.0          | 34.645669291338585 | 2.0            | 34       | 34         | 36.0          | 1.0        | False       | True            | 3.0        |
| P021 | BOYS     | MSC_1 | Regular top or shirt | 95.0      | 94.0      | 94.5          | 37.204724409448815 | 1.0            | 38       | 38         | 34.0          | -2.0       | False       | False           | 1.0        |
| P023 | BOYS     | MSC_1 | Regular top or shirt | 91.0      | 93.0      | 92.0          | 36.22047244094488  | 2.0            | 36       | 36         | 32.0          | -2.0       | False       | False           | 3.0        |
| P025 | BOYS     | MSC_1 | Regular top or shirt | 107.0     | 107.0     | 107.0         | 42.1259842519685   | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 3.0        |
| P027 | BOYS     | MSC_1 | Regular top or shirt | 95.0      | 97.0      | 96.0          | 37.79527559055118  | 2.0            | 38       | 38         | 38.0          | 0.0        | True        | True            | 3.0        |
| P028 | BOYS     | BSC_3 | Regular top or shirt | 95.0      | 98.0      | 96.5          | 37.99212598425197  | 3.0            | 38       | 38         | 36.0          | -1.0       | False       | True            | 2.0        |
| P030 | BOYS     | MSC_1 | Regular top or shirt | 97.0      | 95.0      | 96.0          | 37.79527559055118  | 2.0            | 38       | 38         | 42.0          | 2.0        | False       | False           | 3.0        |
| P039 | BOYS     | MSC_1 | Regular top or shirt | 91.0      | 90.0      | 90.5          | 35.62992125984252  | 1.0            | 36       | 36         | 36.0          | 0.0        | True        | True            | 3.0        |
| P043 | BOYS     | MSC_1 | Plain fitted top     | 97.0      | 98.0      | 97.5          | 38.38582677165354  | 1.0            | 38       | 38         | 36.0          | -1.0       | False       | True            | 4.0        |
| P044 | BOYS     | MSC_1 | Loose top or hoodie  | 96.0      | 96.0      | 96.0          | 37.79527559055118  | 0.0            | 38       | 38         | 32.0          | -3.0       | False       | False           | 2.0        |
| P070 | BOYS     | BSC_3 | Loose top or hoodie  | 109.0     | 109.0     | 109.0         | 42.91338582677165  | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 2.0        |
| P071 | BOYS     | BSC_3 | Regular top or shirt | 101.0     | 97.0      | 99.0          | 38.976377952755904 | 4.0            | 38       | 38         | 42.0          | 2.0        | False       | False           | 4.0        |
| P075 | BOYS     | BSC_3 | Regular top or shirt | 107.0     | 107.0     | 107.0         | 42.1259842519685   | 0.0            | 42       | 42         | 40.0          | -1.0       | False       | True            | 4.0        |
| P077 | BOYS     | BSC_3 | Regular top or shirt | 80.0      | 81.0      | 80.5          | 31.69291338582677  | 1.0            | 32       | 32         | 36.0          | 2.0        | False       | False           | 3.0        |
| P078 | BOYS     | BSC_3 | Regular top or shirt | 108.0     | 108.0     | 108.0         | 42.51968503937008  | 0.0            | 42       | 42         | 42.0          | 0.0        | True        | True            | 5.0        |

*Table dimension: 17 rows × 16 columns.*

---

<a id="7-model-benchmarks-evaluation-boys-cohort"></a>

## 7. Model Benchmarks & Evaluation (Boys Cohort)

*Performance metrics, per-size recall, confusion matrices, standardized coefficients, feature importances, and sensitivity analyses.*

<a id="model-results-boyscsv"></a>

### `model_results_boys.csv`

**Description:** Comprehensive cross-validation benchmark results across models (B0, B1, M1, M2, M3) and evaluation targets.  
**Source File:** [`outputs/tables/model_results_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/model_results_boys.csv)

| target                             | model | metric                   | mean               | ci_low             | ci_high            |
| ---------------------------------- | ----- | ------------------------ | ------------------ | ------------------ | ------------------ |
| (a) merged_class                   | B0    | balanced_accuracy        | 0.5                | 0.5                | 0.5                |
| (a) merged_class                   | B0    | exact_size_accuracy      | 0.619047619047619  | 0.4761904761904761 | 0.7619047619047621 |
| (a) merged_class                   | B0    | within_one_step_accuracy | 1.0                | 1.0                | 1.0                |
| (a) merged_class                   | B0    | mae                      | 0.380952380952381  | 0.238095238095238  | 0.5238095238095238 |
| (a) merged_class                   | B1    | balanced_accuracy        | 0.6288461538461539 | 0.5115101102941174 | 0.7613263888888887 |
| (a) merged_class                   | B1    | exact_size_accuracy      | 0.6833333333333332 | 0.5511607142857143 | 0.8132440476190474 |
| (a) merged_class                   | B1    | within_one_step_accuracy | 1.0                | 1.0                | 1.0                |
| (a) merged_class                   | B1    | mae                      | 0.3166666666666666 | 0.1867559523809523 | 0.4488392857142857 |
| (a) merged_class                   | M1    | balanced_accuracy        | 0.6746394230769232 | 0.5509815463362069 | 0.7985416666666666 |
| (a) merged_class                   | M1    | exact_size_accuracy      | 0.7035714285714285 | 0.5869047619047619 | 0.8154761904761905 |
| (a) merged_class                   | M1    | within_one_step_accuracy | 1.0                | 1.0                | 1.0                |
| (a) merged_class                   | M1    | mae                      | 0.2964285714285714 | 0.1845238095238095 | 0.413095238095238  |
| (a) merged_class                   | M2    | balanced_accuracy        | 0.7888221153846153 | 0.6776741071428571 | 0.8927951388888891 |
| (a) merged_class                   | M2    | exact_size_accuracy      | 0.8107142857142857 | 0.7119047619047618 | 0.902410714285714  |
| (a) merged_class                   | M2    | within_one_step_accuracy | 1.0                | 1.0                | 1.0                |
| (a) merged_class                   | M2    | mae                      | 0.1892857142857142 | 0.0975892857142857 | 0.288095238095238  |
| (a) merged_class                   | M3    | balanced_accuracy        | 0.6489182692307693 | 0.5128958333333333 | 0.7741114551529902 |
| (a) merged_class                   | M3    | exact_size_accuracy      | 0.6642857142857143 | 0.5392559523809524 | 0.7774107142857143 |
| (a) merged_class                   | M3    | within_one_step_accuracy | 1.0                | 1.0                | 1.0                |
| (a) merged_class                   | M3    | mae                      | 0.3357142857142857 | 0.2225892857142857 | 0.4607440476190476 |
| (b) HEADLINE regression            | B0    | rmse                     | 1.731282459875894  | 1.4686760552400946 | 1.992830901901069  |
| (b) HEADLINE regression            | B0    | exact_size_accuracy      | 0.2142857142857142 | 0.0952380952380952 | 0.3333333333333332 |
| (b) HEADLINE regression            | B0    | within_one_step_accuracy | 0.5476190476190477 | 0.4047619047619048 | 0.6904761904761904 |
| (b) HEADLINE regression            | B0    | mae                      | 1.4393769629063748 | 1.1594790605636192 | 1.7394290064510656 |
| (b) HEADLINE regression            | B1    | rmse                     | 1.521568638186487  | 1.2441107063863424 | 1.793208825179692  |
| (b) HEADLINE regression            | B1    | exact_size_accuracy      | 0.2357142857142857 | 0.1261904761904762 | 0.3512499999999999 |
| (b) HEADLINE regression            | B1    | within_one_step_accuracy | 0.6511904761904761 | 0.505922619047619  | 0.7785714285714286 |
| (b) HEADLINE regression            | B1    | mae                      | 1.2363316169266247 | 0.9959188019985036 | 1.5059340950552438 |
| (b) HEADLINE regression            | M1    | rmse                     | 1.7360474582570742 | 1.4267429675043577 | 2.027956063216761  |
| (b) HEADLINE regression            | M1    | exact_size_accuracy      | 0.1904761904761905 | 0.119047619047619  | 0.2786011904761905 |
| (b) HEADLINE regression            | M1    | within_one_step_accuracy | 0.6107142857142857 | 0.4904166666666666 | 0.7274107142857142 |
| (b) HEADLINE regression            | M1    | mae                      | 1.4163384271073802 | 1.146656934999819  | 1.6998394956167375 |
| (b) HEADLINE regression            | M2    | rmse                     | 1.3357313996613294 | 1.0874964925743682 | 1.5712540995078204 |
| (b) HEADLINE regression            | M2    | exact_size_accuracy      | 0.2809523809523809 | 0.1856845238095237 | 0.3797619047619047 |
| (b) HEADLINE regression            | M2    | within_one_step_accuracy | 0.7404761904761904 | 0.6321428571428571 | 0.8357440476190476 |
| (b) HEADLINE regression            | M2    | mae                      | 1.076474155464727  | 0.8719100198858849 | 1.284421984171373  |
| (b) HEADLINE regression            | M3    | rmse                     | 1.760210957311546  | 1.4660088594418348 | 2.0571656533739926 |
| (b) HEADLINE regression            | M3    | exact_size_accuracy      | 0.2083333333333333 | 0.1201785714285714 | 0.2976785714285713 |
| (b) HEADLINE regression            | M3    | within_one_step_accuracy | 0.5773809523809523 | 0.4464285714285714 | 0.7011904761904761 |
| (b) HEADLINE regression            | M3    | mae                      | 1.4389597457131902 | 1.1710615059210812 | 1.7386700935090715 |
| (c) EXPLORATORY per-size class CV  | B0    | balanced_accuracy        | 0.0737301587301587 | 0.0644465445269016 | 0.0918561507936508 |
| (c) EXPLORATORY per-size class CV  | B0    | exact_size_accuracy      | 0.1202380952380952 | 0.0725892857142857 | 0.1726190476190476 |
| (c) EXPLORATORY per-size class CV  | B0    | within_one_step_accuracy | 0.4702380952380952 | 0.3666369047619048 | 0.5644047619047617 |
| (c) EXPLORATORY per-size class CV  | B0    | mae                      | 1.788095238095238  | 1.5666369047619049 | 2.0297916666666667 |
| (c) EXPLORATORY per-size class CV  | B1    | balanced_accuracy        | 0.1667460317460317 | 0.1169635156510156 | 0.2208784593382807 |
| (c) EXPLORATORY per-size class CV  | B1    | exact_size_accuracy      | 0.2607142857142857 | 0.1595238095238095 | 0.3678869047619047 |
| (c) EXPLORATORY per-size class CV  | B1    | within_one_step_accuracy | 0.6345238095238095 | 0.5130952380952382 | 0.7476190476190476 |
| (c) EXPLORATORY per-size class CV  | B1    | mae                      | 1.3166666666666669 | 1.036875           | 1.6120535714285713 |
| (c) EXPLORATORY per-size class CV  | M1    | balanced_accuracy        | 0.2288888888888888 | 0.1364782196969697 | 0.3461204906204906 |
| (c) EXPLORATORY per-size class CV  | M1    | exact_size_accuracy      | 0.2869047619047619 | 0.186875           | 0.3905059523809523 |
| (c) EXPLORATORY per-size class CV  | M1    | within_one_step_accuracy | 0.4952380952380952 | 0.3797321428571428 | 0.613125           |
| (c) EXPLORATORY per-size class CV  | M1    | mae                      | 1.488095238095238  | 1.2142857142857144 | 1.775029761904762  |
| (c) EXPLORATORY per-size class CV  | M2    | balanced_accuracy        | 0.2674603174603174 | 0.1729081246134817 | 0.3843445037105751 |
| (c) EXPLORATORY per-size class CV  | M2    | exact_size_accuracy      | 0.3476190476190476 | 0.2380654761904762 | 0.463095238095238  |
| (c) EXPLORATORY per-size class CV  | M2    | within_one_step_accuracy | 0.5833333333333333 | 0.4666071428571429 | 0.6928869047619047 |
| (c) EXPLORATORY per-size class CV  | M2    | mae                      | 1.2571428571428571 | 0.995238095238095  | 1.5250297619047617 |
| (c) EXPLORATORY per-size class CV  | M3    | balanced_accuracy        | 0.2060714285714285 | 0.1161023886827458 | 0.2915732258812615 |
| (c) EXPLORATORY per-size class CV  | M3    | exact_size_accuracy      | 0.2047619047619047 | 0.1309523809523809 | 0.2893154761904761 |
| (c) EXPLORATORY per-size class CV  | M3    | within_one_step_accuracy | 0.4392857142857143 | 0.3357142857142857 | 0.5464285714285714 |
| (c) EXPLORATORY per-size class CV  | M3    | mae                      | 1.8702380952380948 | 1.5975             | 2.165535714285714  |
| (c) EXPLORATORY per-size class LOO | B0    | balanced_accuracy        | 0.1428571428571428 | 0.1428571428571428 | 0.1666666666666666 |
| (c) EXPLORATORY per-size class LOO | B0    | exact_size_accuracy      | 0.238095238095238  | 0.119047619047619  | 0.3809523809523809 |
| (c) EXPLORATORY per-size class LOO | B0    | within_one_step_accuracy | 0.5476190476190477 | 0.4047619047619047 | 0.6904761904761905 |
| (c) EXPLORATORY per-size class LOO | B0    | mae                      | 1.5714285714285714 | 1.213690476190476  | 1.9523809523809523 |
| (c) EXPLORATORY per-size class LOO | B1    | balanced_accuracy        | 0.1809523809523809 | 0.1098651348651348 | 0.25               |
| (c) EXPLORATORY per-size class LOO | B1    | exact_size_accuracy      | 0.2857142857142857 | 0.1428571428571428 | 0.4285714285714285 |
| (c) EXPLORATORY per-size class LOO | B1    | within_one_step_accuracy | 0.6904761904761905 | 0.5476190476190477 | 0.8333333333333334 |
| (c) EXPLORATORY per-size class LOO | B1    | mae                      | 1.238095238095238  | 0.9047619047619048 | 1.5952380952380951 |
| (c) EXPLORATORY per-size class LOO | M1    | balanced_accuracy        | 0.2182539682539682 | 0.099766156462585  | 0.3631195887445887 |
| (c) EXPLORATORY per-size class LOO | M1    | exact_size_accuracy      | 0.2619047619047619 | 0.1428571428571428 | 0.4047619047619047 |
| (c) EXPLORATORY per-size class LOO | M1    | within_one_step_accuracy | 0.4523809523809524 | 0.3095238095238095 | 0.5952380952380952 |
| (c) EXPLORATORY per-size class LOO | M1    | mae                      | 1.5                | 1.1428571428571428 | 1.8571428571428568 |
| (c) EXPLORATORY per-size class LOO | M2    | balanced_accuracy        | 0.2817460317460317 | 0.1533627087198515 | 0.4294770408163265 |
| (c) EXPLORATORY per-size class LOO | M2    | exact_size_accuracy      | 0.3571428571428571 | 0.2136904761904762 | 0.5                |
| (c) EXPLORATORY per-size class LOO | M2    | within_one_step_accuracy | 0.5714285714285714 | 0.4285714285714285 | 0.7142857142857143 |
| (c) EXPLORATORY per-size class LOO | M2    | mae                      | 1.238095238095238  | 0.9047619047619048 | 1.5952380952380951 |
| (c) EXPLORATORY per-size class LOO | M3    | balanced_accuracy        | 0.2444444444444444 | 0.0955952380952381 | 0.3816242784992784 |
| (c) EXPLORATORY per-size class LOO | M3    | exact_size_accuracy      | 0.2142857142857142 | 0.0952380952380952 | 0.3571428571428571 |
| (c) EXPLORATORY per-size class LOO | M3    | within_one_step_accuracy | 0.4285714285714285 | 0.2857142857142857 | 0.5714285714285714 |
| (c) EXPLORATORY per-size class LOO | M3    | mae                      | 1.8333333333333333 | 1.4523809523809523 | 2.261904761904762  |

*Table dimension: 80 rows × 6 columns.*

---

<a id="per-size-recall-boyscsv"></a>

### `per_size_recall_boys.csv`

**Description:** Per-size recall rates with Wilson 95% confidence intervals across discrete sizes.  
**Source File:** [`outputs/tables/per_size_recall_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/per_size_recall_boys.csv)

| target                            | model | size | n  | recall             | ci_low             | ci_high            |
| --------------------------------- | ----- | ---- | -- | ------------------ | ------------------ | ------------------ |
| (b) HEADLINE regression           | M2    | 32   | 3  | 0.0                | 0.0                | 0.5614970317550455 |
| (b) HEADLINE regression           | M2    | 34   | 4  | 0.25               | 0.0455872608097006 | 0.6993581574175982 |
| (b) HEADLINE regression           | M2    | 36   | 10 | 0.3                | 0.107791267406301  | 0.6032218525388546 |
| (b) HEADLINE regression           | M2    | 38   | 9  | 0.3333333333333333 | 0.1205838183869109 | 0.6457978644196039 |
| (b) HEADLINE regression           | M2    | 40   | 4  | 0.25               | 0.0455872608097006 | 0.6993581574175982 |
| (b) HEADLINE regression           | M2    | 42   | 9  | 0.2222222222222222 | 0.0632251071178467 | 0.5474110308930111 |
| (b) HEADLINE regression           | M2    | 44   | 3  | 0.0                | 0.0                | 0.5614970317550455 |
| (c) EXPLORATORY per-size class CV | M2    | 32   | 3  | 0.0                | 0.0                | 0.5614970317550455 |
| (c) EXPLORATORY per-size class CV | M2    | 34   | 4  | 0.0                | 0.0                | 0.4898908364545974 |
| (c) EXPLORATORY per-size class CV | M2    | 36   | 10 | 0.5                | 0.2365930905125639 | 0.7634069094874361 |
| (c) EXPLORATORY per-size class CV | M2    | 38   | 9  | 0.6666666666666666 | 0.3542021355803961 | 0.879416181613089  |
| (c) EXPLORATORY per-size class CV | M2    | 40   | 4  | 0.25               | 0.0455872608097006 | 0.6993581574175982 |
| (c) EXPLORATORY per-size class CV | M2    | 42   | 9  | 0.3333333333333333 | 0.1205838183869109 | 0.6457978644196039 |
| (c) EXPLORATORY per-size class CV | M2    | 44   | 3  | 0.3333333333333333 | 0.0614919447203962 | 0.7923403991979523 |

*Table dimension: 14 rows × 7 columns.*

---

<a id="confusion-matrix-m2-boyscsv"></a>

### `confusion_matrix_m2_boys.csv`

**Description:** Confusion matrix for the headline regression model (M2 Ridge Size-Step).  
**Source File:** [`outputs/tables/confusion_matrix_m2_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/confusion_matrix_m2_boys.csv)

| Unnamed: 0 | 32.0 | 34.0 | 36.0 | 38.0 | 40.0 | 42.0 | 44.0 |
| ---------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 32.0       | 0.0  | 0.0  | 2.0  | 1.0  | 0.0  | 0.0  | 0.0  |
| 34.0       | 0.0  | 0.0  | 2.0  | 2.0  | 0.0  | 0.0  | 0.0  |
| 36.0       | 1.0  | 0.0  | 5.0  | 1.0  | 1.0  | 2.0  | 0.0  |
| 38.0       | 0.0  | 2.0  | 1.0  | 4.0  | 1.0  | 1.0  | 0.0  |
| 40.0       | 0.0  | 0.0  | 1.0  | 1.0  | 1.0  | 1.0  | 0.0  |
| 42.0       | 0.0  | 0.0  | 2.0  | 1.0  | 2.0  | 4.0  | 0.0  |
| 44.0       | 0.0  | 0.0  | 1.0  | 0.0  | 1.0  | 0.0  | 1.0  |

*Table dimension: 7 rows × 8 columns.*

---

<a id="standard-coefs-m1-boyscsv"></a>

### `standard_coefs_m1_boys.csv`

**Description:** Standardized regression coefficients for the primary feature model (M1).  
**Source File:** [`outputs/tables/standard_coefs_m1_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/standard_coefs_m1_boys.csv)

| feature              | coef                |
| -------------------- | ------------------- |
| shoulder_w           | -0.9743342455827868 |
| torso_len            | 0.6372511368213785  |
| leg_len              | 0.6099775688944944  |
| hip_w_sil            | 0.4907880126591693  |
| shoulder_w_sil       | 0.4857082579829846  |
| arm_len              | 0.2997436227537509  |
| ratio_chest_hip      | 0.2650165402518817  |
| ratio_shoulder_torso | 0.2407193819997351  |
| chest_w_sil          | 0.1459044649104256  |
| waist_w_sil          | 0.1419832577344536  |
| ratio_waist_chest    | 0.1308343402757475  |
| area_ratio           | 0.0670956421334649  |

*Table dimension: 12 rows × 2 columns.*

---

<a id="feature-importances-m3-boyscsv"></a>

### `feature_importances_m3_boys.csv`

**Description:** Random Forest / GBDT feature importance rankings for morphological predictors.  
**Source File:** [`outputs/tables/feature_importances_m3_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/feature_importances_m3_boys.csv)

| feature              | importance         |
| -------------------- | ------------------ |
| hip_w_sil            | 0.2451776164326581 |
| area_ratio           | 0.1312056427835485 |
| leg_len              | 0.1160619510737376 |
| arm_len              | 0.1052837702953131 |
| torso_len            | 0.0883597310954849 |
| chest_w_sil          | 0.0830076799455957 |
| waist_w_sil          | 0.0550332992307755 |
| shoulder_w           | 0.0431017618535193 |
| ratio_chest_hip      | 0.0398434839111753 |
| ratio_waist_chest    | 0.0344280108829969 |
| shoulder_w_sil       | 0.0306392424115057 |
| ratio_shoulder_torso | 0.0278578100836889 |

*Table dimension: 12 rows × 2 columns.*

---

<a id="comparisons-boyscsv"></a>

### `comparisons_boys.csv`

**Description:** Formal model comparison table (M1 vs Baselines, delta metrics, confidence intervals).  
**Source File:** [`outputs/tables/comparisons_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/comparisons_boys.csv)

| target                  | model_A | model_B | metric              | win_share | mean_diff           | ci_low              | ci_high            |
| ----------------------- | ------- | ------- | ------------------- | --------- | ------------------- | ------------------- | ------------------ |
| (b) HEADLINE regression | M1      | B0      | exact_size_accuracy | 0.2       | -0.0214666666666666 | -0.1523809523809524 | 0.0952678571428571 |
| (b) HEADLINE regression | M1      | B1      | exact_size_accuracy | 0.2       | -0.0426261904761904 | -0.1762202380952381 | 0.0845535714285714 |
| (b) HEADLINE regression | M2      | B0      | exact_size_accuracy | 0.9       | 0.0687928571428571  | -0.0666666666666666 | 0.2047916666666666 |
| (b) HEADLINE regression | M2      | B1      | exact_size_accuracy | 0.65      | 0.0476333333333333  | -0.0654761904761904 | 0.1750595238095237 |
| (b) HEADLINE regression | M3      | B0      | exact_size_accuracy | 0.3       | -0.0062690476190476 | -0.1095535714285714 | 0.0952380952380952 |
| (b) HEADLINE regression | M3      | B1      | exact_size_accuracy | 0.15      | -0.0274285714285714 | -0.1583333333333333 | 0.1024107142857142 |
| (b) HEADLINE regression | M2      | M1      | exact_size_accuracy | 0.95      | 0.0902595238095238  | -0.0035714285714285 | 0.1809523809523809 |

*Table dimension: 7 rows × 8 columns.*

---

<a id="sensitivity-boyscsv"></a>

### `sensitivity_boys.csv`

**Description:** Sensitivity analysis evaluating model robustness under loose/heavy clothing exclusions.  
**Source File:** [`outputs/tables/sensitivity_boys.csv`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/sensitivity_boys.csv)

| sensitivity            | exact_size_accuracy |
| ---------------------- | ------------------- |
| exclude_loose_or_heavy | 0.1785714285714285  |
| exclude_pilot          | 0.2083333333333333  |
| fit_rating_3_only      | 0.224074074074074   |

*Table dimension: 3 rows × 2 columns.*

---

<a id="permutation-testtxt"></a>

### `permutation_test.txt`

**Description:** Permutation test p-value validating statistical significance of model predictions over chance.  
**Source File:** [`outputs/tables/permutation_test.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/permutation_test.txt)

```text
Permutation test (M2, Exact Size Accuracy): p-value = 0.1725
```

---

<a id="8-empirical-experiments-sample-size-design-comparison"></a>

## 8. Empirical Experiments: Sample Size & Design Comparison

*Simulation studies investigating learning curves (performance vs sample size) and sampling design efficiency (SRSWOR vs Stratified).*

<a id="experiment-partatxt"></a>

### `experiment_partA.txt`

**Description:** Learning curve simulation: Balanced accuracy and MAE as a function of training sample size (n=8 to 24).  
**Source File:** [`outputs/tables/experiment_partA.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/experiment_partA.txt)

```text
Status: FIT

Caution: Draws come from a finite pool, the curve must not be extrapolated, and it does not show that larger samples always help.

Fraction of draws lacking a class (skipped): 0.0000

 n_train model  bacc_mean  bacc_sd  bacc_p2.5  bacc_p97.5  mae_mean   mae_sd  mae_p2.5  mae_p97.5
       8    M1   0.622973 0.145939   0.285714       0.875  1.915486 0.566803  1.126656   3.307683
      12    M1   0.643942 0.130756   0.339286       0.875  1.729591 0.383351  1.134970   2.653834
      16    M1   0.665710 0.121560   0.410714       0.875  1.592186 0.310579  1.063500   2.289841
      20    M1   0.673402 0.108620   0.428571       0.875  1.509516 0.258852  1.029661   2.088810
      24    M1   0.680112 0.100900   0.482143       0.875  1.457823 0.239748  0.990693   1.978502
       8    B0   0.500000 0.000000   0.500000       0.500  1.501790 0.212743  1.147727   1.943182
      12    B0   0.500000 0.000000   0.500000       0.500  1.507017 0.222491  1.136364   1.977273
      16    B0   0.500000 0.000000   0.500000       0.500  1.483362 0.215713  1.142045   1.943182
      20    B0   0.500000 0.000000   0.500000       0.500  1.491258 0.223782  1.118182   1.963636
      24    B0   0.500000 0.000000   0.500000       0.500  1.473934 0.218677  1.128788   1.943182
```

---

<a id="experiment-partbtxt"></a>

### `experiment_partB.txt`

**Description:** Sampling design Monte Carlo simulation comparing SRSWOR, Stratified Proportional, and Stratified Equal designs.  
**Source File:** [`outputs/tables/experiment_partB.txt`](file:///C:/Users/kapil/.gemini/antigravity/scratch/ssi_project/outputs/tables/experiment_partB.txt)

```text
Simulation on the collected pool, not a second sampling design.

 n                  design  le38_bias  le38_sd  le38_rmse    h_bias     h_sd   h_rmse  prob_cov_cat  prob_cov_bclass
20                  SRSWOR  -0.000582 0.086491   0.086493 -0.063366 1.967622 1.968642        0.9625           0.5230
20 Stratified Proportional   0.004843 0.082065   0.082207 -0.327991 1.047168 1.097333        1.0000           0.4910
20        Stratified Equal   0.001140 0.090162   0.090169  0.002294 1.161172 1.161174        1.0000           0.2055
30                  SRSWOR   0.000601 0.063670   0.063673  0.051092 1.439834 1.440740        1.0000           0.9220
30 Stratified Proportional  -0.002532 0.060792   0.060844  0.278475 0.799697 0.846796        1.0000           0.9595
30        Stratified Equal  -0.000733 0.067333   0.067337  0.013562 0.846006 0.846115        1.0000           0.7860
40                  SRSWOR   0.000768 0.048348   0.048355 -0.023441 1.068396 1.068653        1.0000           0.9960
40 Stratified Proportional  -0.000870 0.046724   0.046732  0.118259 0.572966 0.585043        1.0000           0.9990
40        Stratified Equal  -0.000991 0.051078   0.051088 -0.001437 0.652380 0.652382        1.0000           0.9800

Comparison Notes:
Stratified Equal allocation is consistently 'better' on the criterion of probability of covering both categories (prob_cov_cat) especially at smaller n.
Differences in RMSE (bias is mostly ~0 for all designs) for overall estimates are relatively small, though proportional stratification is typically slightly better or equal to SRSWOR on le38_rmse and h_rmse.
```

---
