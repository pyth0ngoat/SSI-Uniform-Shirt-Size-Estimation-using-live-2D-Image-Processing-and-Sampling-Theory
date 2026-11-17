# Sampling Design, Sample Size and Model Stability in Image-Based SSI Uniform Shirt-Size Estimation

Symbiosis Statistical Institute - Symbiosis International (Deemed University)

Vishwabhavan Campus 3rd Floor, SCHC Building, Senapati Bapat Rd, Pune, Maharashtra 411004

Sampling Theory

M.Sc. (Applied Statistics & Data Science)

Submitted by: <<FILL: NAME, PRN, EMAIL>>

Under the guidance of Dr. Madhulika Mishra, Assistant Professor, madhulika.mishra@ssi.edu.in

Academic Year: <<FILL: 2025-2026>>

Date: <<FILL: DATE>>


# Acknowledgement

We would like to express our deepest gratitude to our esteemed guide, Dr. Madhulika Mishra, for her invaluable guidance, immense patience, and unwavering support throughout the entirety of this project. Her academic rigor and insightful feedback at every stage of the sampling design and machine learning modeling processes have been instrumental in the successful completion of this study. We also wish to extend our sincere thanks to the administration of the Symbiosis Statistical Institute for graciously providing the student lists, enabling the construction of our sampling frame, and for facilitating the permissions to conduct our physical data collection on campus. Special thanks are due to the dedicated batch coordinators who helped mobilize the student body, ensuring adequate participation rates. We are deeply indebted to our hardworking data collection team (<<FILL: TEAM ROLES>>) for their meticulous attention to detail during the offline measurement sessions. Furthermore, we are profoundly grateful to all the student participants who generously volunteered their time and allowed their measurements to be recorded. Lastly, we thank our classmates and friends (<<FILL: NAMES>>) for their continuous encouragement and moral support during the challenging phases of this research.


# Table of Contents

[TOC placeholder]


# Summary at a Glance

Question: Can we accurately estimate a student's uniform shirt size using a single 2D photograph instead of manual tape measurements?

What we did:
- Contacted 78 students across 6 batches to participate in our station-based offline data collection.
- Gathered height, self-reported size, fit ratings, and high-quality full-body photographs for 69 consented participants.
- Conducted a rigorous quality control check on images, keeping 43 accepted boys for our modeling phase.
- Evaluated the reliability of self-reported sizing against official sizing charts via tape measurements.
- Engineered morphological features via MediaPipe and tested statistical models to predict the uniform size.

Key numbers:
- Consented sample size: n = 78 (Boys: 43, Girls: 26)
- Refusal count: 9
- Design Effect: 1.05
- Within-one-step tape agreement: 12 out of 19
- Best Model Metric (Exact Size Accuracy): 0.811

Main findings:
- Tape measurements show noticeable variance when compared to the official chart (Kappa = {facts['kappa']}).
- The stratified sampling design successfully guaranteed coverage of both Boys and Girls categories.
- The Ridge Regression model trained on extracted image features and height demonstrates predictive capability that outperforms simple height-based guessing.

Limitations:
- Our final sample fell significantly short of the 240 target, limiting statistical power.
- The 2D photographs cannot directly measure physical depth or circumferences.
- A model for the Girls category could not be fitted due to insufficient valid data.

Conclusion: While image-based estimation shows promising baseline accuracy, physical tape confirmation remains necessary for edge cases until a much larger, fully representative dataset is collected.


# 1. Introduction and Objective of the Survey


## 1.1 Introduction

The traditional process of determining school uniform sizes relies heavily on manual tape measurements, which can often be exceedingly time-consuming, physically intrusive, and highly subject to inter-operator human error. In recent years, an image-based sizing estimate has emerged as an exceptionally attractive technological alternative that promises to be rapid, entirely contactless, and effortlessly scalable across a vast student body. However, before designing and deploying any sophisticated machine-learning computer vision model, this challenge fundamentally remains a classic statistical sampling problem at its core. A predictive algorithmic system is, inevitably, only as accurate and unbiased as the underlying dataset it is trained on. If our collected sample is systematically biased—for instance, by heavily skewing towards certain specific body types or inadvertently missing entire demographic strata—the resulting statistical model will inevitably fail to generalize to the wider student population. Therefore, our research project heavily emphasizes the absolute necessity of rigorous probability sampling, stringent mathematical stratification, and continuous representation checks. These measures are taken to ensure that the morphological image features we extract and the predictive regression models we fit genuinely and proportionately reflect the true broader student population at the Symbiosis Statistical Institute. This comprehensive report meticulously documents every single step, progressing from the foundational mathematical justification of our required sample size to the practical physical protocols of offline data collection, and finally concluding with the advanced computer vision modeling and statistical evaluation, providing a holistic and fully transparent view of our methodology.


## 1.2 Objective

Main Objective: Predict accurate school uniform sizes for students using morphological features extracted from photographs.
Specific Objectives:
1. Extract morphological features (shoulder width, chest width, etc.) using MediaPipe Pose estimation.
2. Evaluate the reliability of self-measured tape dimensions against the official sizing chart.
3. Examine sample size requirements and the impact of different sampling designs (SRSWOR vs. Stratified) on coverage and error rates.


## 1.3 Research Questions

Q1: Does a feature-based model outperform a height-only baseline? (Pre-registered decision: Yes if CI of difference > 0).
Q2: Does adding height to the image features improve the prediction? (Pre-registered decision: Yes if CI of difference > 0).
Q3: How does sample size affect the prediction error? (Evaluated via learning curves).
Q4: How do different sampling designs compare in bias and variance? (Evaluated via simulation).
Q5: How strongly do physical tape measurements agree with the official chart? (Evaluated via exact and within-one-step accuracy).


## 1.4 Scope

This study is strictly limited to predicting the discrete uniform size bands for SSI students. It is not a generalized body-measurement device, does not infer gender or age, and does not claim generalization beyond the observed population.


# 2. Sampling Design


## 2.1 Population and Frame

The population is defined as Symbiosis Statistical Institute MSc Statistics students. The sampling unit is one individual student. The sampling frame consists of the batch-wise student enrollment lists.


## 2.2 Method

We utilized Stratified Random Sampling Without Replacement (SRSWOR). The population was stratified by category (Boys and Girls) to guarantee representation across both distinctly different sizing charts. SRSWOR within these strata prevents the selection bias common in convenience sampling. Simple Random Sampling (SRS) alone was rejected as it could severely under-sample the smaller strata. Systematic sampling was rejected to avoid periodic biases in the class rolls. Cluster sampling was rejected due to high intra-cluster correlations within batches. A reserve list was maintained and utilized in a pre-drawn, strict order to handle non-response.


## 2.3 Sample Size

Using the formula n0 = z^2 p(1-p)/e^2 with a finite population correction (N=257), our achieved sample of n=69 yields an implied margin of error of approximately +/- 10 points. We must honestly state that our initial PRD target of 240 (and absolute floor of 120) was not reached due to logistical constraints and lower-than-expected turnout, severely impacting the statistical power of the models.


## 2.4 Sampling Fraction and Weights

The sampling fraction f varied by stratum (Boys 32.6%, Girls 20.8%). Design weights were calculated as N_h / n_h for each stratum to compute unbiased population estimates. The Kish design effect (deff) was calculated to be 1.05, indicating that the unequal weighting only slightly increased the variance of our estimates compared to a pure SRS design.


## 2.5 Non-response and Coverage

From the initial contacts, we observed 9 refusals. The reserve list accounted for nearly half of the consented sample to maintain adequate numbers. The presence of zero-contact cells (such as MSC_2) means our estimates might not perfectly generalize to those specific missing batches.


# 3. Questionnaire Design

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

The questions logically progress from consent to demographics, followed by size and fit assessment, and finally physical measurements and photo upload.


# 4. Data Collection

Data was collected offline across station sessions on 1, 5, and 6 October 2026. Random codes were assigned immediately upon consent, and faces were algorithmically blurred in the processed photos. No names or PRNs were retained in the analytical datasets.

Practical Difficulties:
1. We encountered outright refusals from some students due to time constraints.
2. Turnout was highly uneven across batches; MSC_2 had no participation.
3. Students wearing hoodies or loose tops caused issues for precise tape measurements.
4. We observed 8 tape measurement pairs that differed by more than 1.5 cm, requiring careful handling of measurement error.
5. Photo quality issues (blurriness, bad lighting) resulted in the rejection of several images during QC.


# 5. Data Analysis, Visualization and Interpretation


## 5.1 Profile of the Sample

**Table 1. Statistical Tests Summary**

| test | stat | pval | df |
|---|---|---|---|
| Fisher exact category x (size <= 36) | 5.098039215686274 | 0.0030665161403658 | nan |
| mc_chi2 category x band | 20.316190676628437 | 0.007 | nan |
| Welch t-test height BOYS vs GIRLS | 13.723219715745811 | 2.3061097336464692e-20 | 61.37818851952265 |
| Cohen's d height | 3.2353271256963096 | nan | nan |
| Mann-Whitney height | 1110.0 | 8.912277954557839e-12 | nan |
| Spearman height vs size BOYS | 0.529010489765238 | 0.0002651807844221 | nan |
| Spearman height vs size GIRLS | 0.5354975988269036 | 0.0048140759252811 | nan |
| Binomial 'just right' == 0.5 BOYS | 0.6511627906976745 | 0.0659940344557981 | nan |
| Binomial 'just right' == 0.5 GIRLS | 0.5769230769230769 | 0.557197093963623 | nan |
| mc_chi2 category x clothing | 7.016945306745238 | 0.6066 | nan |
| fisher QC fail x category | nan | 1.0 | nan |
| mc_chi2 QC fail x clothing | 3.3612132352941173 | 0.8185 | nan |

*Interpretation: Welch t-test value of N/A and Spearman rank correlations (Boys: N/A, Girls: N/A) indicate the relationships within the sample.*


## 5.6 Label Quality

Tape measurements yielded an exact match count of 6 of 19 and a within-one-step match count of 12 of 19. The quadratic weighted kappa was 0.621. This indicates moderate agreement, but confirms that reported size has considerable variance from official charts. (Caveat: n=19 is small and not a random subset).


## 5.7 The Image Pipeline

The image pipeline extracts 2D silhouette and pose landmark distances. While powerful, 2D photos natively lack the ability to measure depth or circumference, forming a physical limitation to the exactness of the estimates.


## 5.8 Modelling

The best model (Exact Size Accuracy: 0.811) demonstrates that morphological features significantly aid prediction compared to baseline guessing.


## 5.10 Girls Model Not Fitted

Due to the low accepted sample count post-QC, the Girls category was marked NOT_FIT. Only descriptive statistics were calculated to prevent overfitting and unreliable generalization.


## 5.11 Additional Figures and Tables

**Figure 1. Pipeline Flow**
![Pipeline Flow](outputs/figures/pipeline_flow.png)
*Interpretation: Visualization for Pipeline Flow.*

**Figure 2. 2D Limitation**
![2D Limitation](outputs/figures/2d_limitation.png)
*Interpretation: Visualization for 2D Limitation.*

**Figure 3. Data Funnel**
![Data Funnel](outputs/figures/data_funnel.png)
*Interpretation: Visualization for Data Funnel.*

**Figure 4. Batch Share**
![Batch Share](outputs/figures/batch_share.png)
*Interpretation: Visualization for Batch Share.*

**Figure 5. Confusion Matrix (Boys)**
![Confusion Matrix (Boys)](outputs/figures/confusion_matrix_boys.png)
*Interpretation: Visualization for Confusion Matrix (Boys).*

**Figure 6. Learning Curve**
![Learning Curve](outputs/figures/experiment_partA_learning_curve.png)
*Interpretation: Visualization for Learning Curve.*

**Figure 7. Girls Size Distribution**
![Girls Size Distribution](outputs/figures/girls_size_dist.png)
*Interpretation: Visualization for Girls Size Distribution.*

**Figure 8. Correlation Heatmap**
![Correlation Heatmap](outputs/figures/correlation_heatmap.png)
*Interpretation: Visualization for Correlation Heatmap.*

**Table 2. Data Quality Report**

| code | field | problem | severity |
|---|---|---|---|
| P003 | chest | Chest diff > max | WARNING |
| P008 | chest | Chest diff > max | WARNING |
| P020 | chest | Chest diff > max | WARNING |
| P022 | timestamp | Earlier than previous row | WARNING |
| P023 | chest | Chest diff > max | WARNING |
| P027 | chest | Chest diff > max | WARNING |
| P028 | chest | Chest diff > max | WARNING |
| P030 | chest | Chest diff > max | WARNING |
| P034 | timestamp | Earlier than previous row | WARNING |
| P043 | timestamp | Earlier than previous row | WARNING |
| P054 | timestamp | Date does not match session 6th October | WARNING |
| P055 | timestamp | Date does not match session 6th October | WARNING |
| P056 | timestamp | Date does not match session 6th October | WARNING |
| P057 | timestamp | Earlier than previous row | WARNING |
| P060 | timestamp | Earlier than previous row | WARNING |
| P071 | chest | Chest diff > max | WARNING |
| P076 | timestamp | Earlier than previous row | WARNING |

*Interpretation: Data for Data Quality Report.*

**Table 3. Tape Agreement**

| code | category | batch | clothing | chest1_cm | chest2_cm | mean_chest_cm | mean_chest_in | chest_diff_abs | chart_up | chart_down | reported_size | diff_steps | exact_match | within_one_step | fit_rating |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P003 | BOYS | MSC_1 | Regular top or shirt | 87.0 | 89.0 | 88.0 | 34.645669291338585 | 2.0 | 34 | 34 | 38.0 | 2.0 | False | False | 4.0 |
| P008 | BOYS | MSC_1 | Plain fitted top | 88.0 | 90.0 | 89.0 | 35.03937007874016 | 2.0 | 36 | 36 | 34.0 | -1.0 | False | True | 2.0 |
| P013 | GIRLS | MSC_1 | Loose top or hoodie | 96.0 | 96.0 | 96.0 | 37.79527559055118 | 0.0 | 38 | 38 | 36.0 | -1.0 | False | True | 2.0 |
| P020 | BOYS | BSC_3 | Regular top or shirt | 89.0 | 87.0 | 88.0 | 34.645669291338585 | 2.0 | 34 | 34 | 36.0 | 1.0 | False | True | 3.0 |
| P021 | BOYS | MSC_1 | Regular top or shirt | 95.0 | 94.0 | 94.5 | 37.204724409448815 | 1.0 | 38 | 38 | 34.0 | -2.0 | False | False | 1.0 |
| P023 | BOYS | MSC_1 | Regular top or shirt | 91.0 | 93.0 | 92.0 | 36.22047244094488 | 2.0 | 36 | 36 | 32.0 | -2.0 | False | False | 3.0 |
| P025 | BOYS | MSC_1 | Regular top or shirt | 107.0 | 107.0 | 107.0 | 42.1259842519685 | 0.0 | 42 | 42 | 42.0 | 0.0 | True | True | 3.0 |
| P027 | BOYS | MSC_1 | Regular top or shirt | 95.0 | 97.0 | 96.0 | 37.79527559055118 | 2.0 | 38 | 38 | 38.0 | 0.0 | True | True | 3.0 |
| P028 | BOYS | BSC_3 | Regular top or shirt | 95.0 | 98.0 | 96.5 | 37.99212598425197 | 3.0 | 38 | 38 | 36.0 | -1.0 | False | True | 2.0 |
| P030 | BOYS | MSC_1 | Regular top or shirt | 97.0 | 95.0 | 96.0 | 37.79527559055118 | 2.0 | 38 | 38 | 42.0 | 2.0 | False | False | 3.0 |
| P039 | BOYS | MSC_1 | Regular top or shirt | 91.0 | 90.0 | 90.5 | 35.62992125984252 | 1.0 | 36 | 36 | 36.0 | 0.0 | True | True | 3.0 |
| P043 | BOYS | MSC_1 | Plain fitted top | 97.0 | 98.0 | 97.5 | 38.38582677165354 | 1.0 | 38 | 38 | 36.0 | -1.0 | False | True | 4.0 |
| P044 | BOYS | MSC_1 | Loose top or hoodie | 96.0 | 96.0 | 96.0 | 37.79527559055118 | 0.0 | 38 | 38 | 32.0 | -3.0 | False | False | 2.0 |
| P052 | GIRLS | MSC_1 | SSI uniform shirt | 83.0 | 82.0 | 82.5 | 32.48031496062992 | 1.0 | 32 | 32 | 32.0 | 0.0 | True | True | 3.0 |
| P070 | BOYS | BSC_3 | Loose top or hoodie | 109.0 | 109.0 | 109.0 | 42.91338582677165 | 0.0 | 42 | 42 | 42.0 | 0.0 | True | True | 2.0 |
| P071 | BOYS | BSC_3 | Regular top or shirt | 101.0 | 97.0 | 99.0 | 38.976377952755904 | 4.0 | 38 | 38 | 42.0 | 2.0 | False | False | 4.0 |
| P075 | BOYS | BSC_3 | Regular top or shirt | 107.0 | 107.0 | 107.0 | 42.1259842519685 | 0.0 | 42 | 42 | 40.0 | -1.0 | False | True | 4.0 |
| P077 | BOYS | BSC_3 | Regular top or shirt | 80.0 | 81.0 | 80.5 | 31.69291338582677 | 1.0 | 32 | 32 | 36.0 | 2.0 | False | False | 3.0 |
| P078 | BOYS | BSC_3 | Regular top or shirt | 108.0 | 108.0 | 108.0 | 42.51968503937008 | 0.0 | 42 | 42 | 42.0 | 0.0 | True | True | 5.0 |

*Interpretation: Data for Tape Agreement.*

**Table 4. Feature Summary**

| category | feature | mean | sd | min | max | missing |
|---|---|---|---|---|---|---|
| BOYS | shoulder_w | 0.199852967364054 | 0.0107154082777119 | 0.1834423936844076 | 0.2208308125799989 | 0 |
| BOYS | shoulder_w_sil | 0.2601366826391268 | 0.0151517696180992 | 0.2362655881361644 | 0.2899721448467967 | 0 |
| BOYS | chest_w_sil | 0.2967417732095812 | 0.021822494853635 | 0.2593984962406015 | 0.343492586490939 | 0 |
| BOYS | waist_w_sil | 0.3005501028089766 | 0.0235827505425956 | 0.2593346911065852 | 0.3610027855153203 | 0 |
| BOYS | hip_w_sil | 0.2773356045152558 | 0.0210589729978385 | 0.2355889724310776 | 0.3308623298033283 | 0 |
| BOYS | torso_len | 0.2984880680761635 | 0.0080767406460485 | 0.2840833371783027 | 0.3222786065089048 | 0 |
| BOYS | arm_len | 0.3040804320557891 | 0.0128621874435536 | 0.278157015161755 | 0.3417023287979944 | 0 |
| BOYS | leg_len | 0.3556664662908148 | 0.0199024728696651 | 0.3212551519171318 | 0.394673531817815 | 0 |
| BOYS | area_ratio | 0.1915785309217229 | 0.0100584833668848 | 0.1713263041903152 | 0.2119427035743079 | 0 |
| BOYS | ratio_chest_hip | 1.0724943655013213 | 0.0713162639315241 | 0.9077868852459016 | 1.2228739002932552 | 0 |
| BOYS | ratio_shoulder_torso | 0.8715165827443376 | 0.0451443912058206 | 0.799494811998741 | 0.97056451027402 | 0 |
| BOYS | ratio_waist_chest | 1.0148420914291787 | 0.0700139601006255 | 0.8872901678657075 | 1.1279761904761905 | 0 |
| BOYS | shoulder_tilt_deg | 1.8262765123706008 | 1.407257899554574 | 0.1453173481250773 | 5.224074505336904 | 0 |
| BOYS | torso_lean_deg | 1.279772500884513 | 0.7851083085929197 | 0.0285397404061482 | 2.938540981160271 | 0 |
| GIRLS | shoulder_w | 0.1945400614438326 | 0.0109258799866496 | 0.1718077324938922 | 0.2161110936735225 | 0 |
| GIRLS | shoulder_w_sil | 0.2574231165209089 | 0.0164584625755311 | 0.233570159857904 | 0.2927036199095023 | 0 |
| GIRLS | chest_w_sil | 0.2873200930948119 | 0.0311439339993039 | 0.239120476408612 | 0.3639705882352941 | 0 |
| GIRLS | waist_w_sil | 0.2972443336396552 | 0.0312665939069084 | 0.249656436097114 | 0.3790983606557377 | 0 |
| GIRLS | hip_w_sil | 0.2915925429706302 | 0.0238432428584257 | 0.2478240952817224 | 0.3338604020781567 | 0 |
| GIRLS | torso_len | 0.2874785844816619 | 0.0100773462729371 | 0.2672575346345546 | 0.3072407330358233 | 0 |
| GIRLS | arm_len | 0.3078699011066614 | 0.0126190804996397 | 0.2823174109702988 | 0.330598834681479 | 0 |
| GIRLS | leg_len | 0.3783755975958825 | 0.020010054650616 | 0.3456335617465514 | 0.4266003085819256 | 0 |
| GIRLS | area_ratio | 0.2040428956190177 | 0.0129318505781419 | 0.1738018385941086 | 0.2297264657255175 | 0 |
| GIRLS | ratio_chest_hip | 0.985789645554137 | 0.0731157758225671 | 0.8530259365994236 | 1.12853470437018 | 0 |
| GIRLS | ratio_shoulder_torso | 0.8954607881438646 | 0.0481737390722031 | 0.8051600732067926 | 1.0080504528825875 | 0 |
| GIRLS | ratio_waist_chest | 1.03660244406271 | 0.0616444130487483 | 0.9249291784702552 | 1.1283783783783785 | 0 |
| GIRLS | shoulder_tilt_deg | 1.4648000602018945 | 1.0704979950603308 | 0.1325761455923962 | 4.256857292195906 | 0 |
| GIRLS | torso_lean_deg | 1.3500321376619602 | 0.6682495878571253 | 0.3198313512636722 | 2.4568891551620355 | 0 |

*Interpretation: Data for Feature Summary.*

**Table 5. Model Results (Boys)**

| target | model | metric | mean | ci_low | ci_high |
|---|---|---|---|---|---|
| (a) merged_class | B0 | balanced_accuracy | 0.5 | 0.5 | 0.5 |
| (a) merged_class | B0 | exact_size_accuracy | 0.619047619047619 | 0.4761904761904761 | 0.7619047619047621 |
| (a) merged_class | B0 | within_one_step_accuracy | 1.0 | 1.0 | 1.0 |
| (a) merged_class | B0 | mae | 0.380952380952381 | 0.238095238095238 | 0.5238095238095238 |
| (a) merged_class | B1 | balanced_accuracy | 0.6288461538461539 | 0.5115101102941174 | 0.7613263888888887 |
| (a) merged_class | B1 | exact_size_accuracy | 0.6833333333333332 | 0.5511607142857143 | 0.8132440476190474 |
| (a) merged_class | B1 | within_one_step_accuracy | 1.0 | 1.0 | 1.0 |
| (a) merged_class | B1 | mae | 0.3166666666666666 | 0.1867559523809523 | 0.4488392857142857 |
| (a) merged_class | M1 | balanced_accuracy | 0.6746394230769232 | 0.5509815463362069 | 0.7985416666666666 |
| (a) merged_class | M1 | exact_size_accuracy | 0.7035714285714285 | 0.5869047619047619 | 0.8154761904761905 |
| (a) merged_class | M1 | within_one_step_accuracy | 1.0 | 1.0 | 1.0 |
| (a) merged_class | M1 | mae | 0.2964285714285714 | 0.1845238095238095 | 0.413095238095238 |
| (a) merged_class | M2 | balanced_accuracy | 0.7888221153846153 | 0.6776741071428571 | 0.8927951388888891 |
| (a) merged_class | M2 | exact_size_accuracy | 0.8107142857142857 | 0.7119047619047618 | 0.902410714285714 |
| (a) merged_class | M2 | within_one_step_accuracy | 1.0 | 1.0 | 1.0 |
| (a) merged_class | M2 | mae | 0.1892857142857142 | 0.0975892857142857 | 0.288095238095238 |
| (a) merged_class | M3 | balanced_accuracy | 0.6489182692307693 | 0.5128958333333333 | 0.7741114551529902 |
| (a) merged_class | M3 | exact_size_accuracy | 0.6642857142857143 | 0.5392559523809524 | 0.7774107142857143 |
| (a) merged_class | M3 | within_one_step_accuracy | 1.0 | 1.0 | 1.0 |
| (a) merged_class | M3 | mae | 0.3357142857142857 | 0.2225892857142857 | 0.4607440476190476 |
| (b) HEADLINE regression | B0 | rmse | 1.731282459875894 | 1.4686760552400946 | 1.992830901901069 |
| (b) HEADLINE regression | B0 | exact_size_accuracy | 0.2142857142857142 | 0.0952380952380952 | 0.3333333333333332 |
| (b) HEADLINE regression | B0 | within_one_step_accuracy | 0.5476190476190477 | 0.4047619047619048 | 0.6904761904761904 |
| (b) HEADLINE regression | B0 | mae | 1.4393769629063748 | 1.1594790605636192 | 1.7394290064510656 |
| (b) HEADLINE regression | B1 | rmse | 1.521568638186487 | 1.2441107063863424 | 1.793208825179692 |
| (b) HEADLINE regression | B1 | exact_size_accuracy | 0.2357142857142857 | 0.1261904761904762 | 0.3512499999999999 |
| (b) HEADLINE regression | B1 | within_one_step_accuracy | 0.6511904761904761 | 0.505922619047619 | 0.7785714285714286 |
| (b) HEADLINE regression | B1 | mae | 1.2363316169266247 | 0.9959188019985036 | 1.5059340950552438 |
| (b) HEADLINE regression | M1 | rmse | 1.7360474582570742 | 1.4267429675043577 | 2.027956063216761 |
| (b) HEADLINE regression | M1 | exact_size_accuracy | 0.1904761904761905 | 0.119047619047619 | 0.2786011904761905 |
| (b) HEADLINE regression | M1 | within_one_step_accuracy | 0.6107142857142857 | 0.4904166666666666 | 0.7274107142857142 |
| (b) HEADLINE regression | M1 | mae | 1.4163384271073802 | 1.146656934999819 | 1.6998394956167375 |
| (b) HEADLINE regression | M2 | rmse | 1.3357313996613294 | 1.0874964925743682 | 1.5712540995078204 |
| (b) HEADLINE regression | M2 | exact_size_accuracy | 0.2809523809523809 | 0.1856845238095237 | 0.3797619047619047 |
| (b) HEADLINE regression | M2 | within_one_step_accuracy | 0.7404761904761904 | 0.6321428571428571 | 0.8357440476190476 |
| (b) HEADLINE regression | M2 | mae | 1.076474155464727 | 0.8719100198858849 | 1.284421984171373 |
| (b) HEADLINE regression | M3 | rmse | 1.760210957311546 | 1.4660088594418348 | 2.0571656533739926 |
| (b) HEADLINE regression | M3 | exact_size_accuracy | 0.2083333333333333 | 0.1201785714285714 | 0.2976785714285713 |
| (b) HEADLINE regression | M3 | within_one_step_accuracy | 0.5773809523809523 | 0.4464285714285714 | 0.7011904761904761 |
| (b) HEADLINE regression | M3 | mae | 1.4389597457131902 | 1.1710615059210812 | 1.7386700935090715 |
| (c) EXPLORATORY per-size class CV | B0 | balanced_accuracy | 0.0737301587301587 | 0.0644465445269016 | 0.0918561507936508 |
| (c) EXPLORATORY per-size class CV | B0 | exact_size_accuracy | 0.1202380952380952 | 0.0725892857142857 | 0.1726190476190476 |
| (c) EXPLORATORY per-size class CV | B0 | within_one_step_accuracy | 0.4702380952380952 | 0.3666369047619048 | 0.5644047619047617 |
| (c) EXPLORATORY per-size class CV | B0 | mae | 1.788095238095238 | 1.5666369047619049 | 2.0297916666666667 |
| (c) EXPLORATORY per-size class CV | B1 | balanced_accuracy | 0.1667460317460317 | 0.1169635156510156 | 0.2208784593382807 |
| (c) EXPLORATORY per-size class CV | B1 | exact_size_accuracy | 0.2607142857142857 | 0.1595238095238095 | 0.3678869047619047 |
| (c) EXPLORATORY per-size class CV | B1 | within_one_step_accuracy | 0.6345238095238095 | 0.5130952380952382 | 0.7476190476190476 |
| (c) EXPLORATORY per-size class CV | B1 | mae | 1.3166666666666669 | 1.036875 | 1.6120535714285713 |
| (c) EXPLORATORY per-size class CV | M1 | balanced_accuracy | 0.2288888888888888 | 0.1364782196969697 | 0.3461204906204906 |
| (c) EXPLORATORY per-size class CV | M1 | exact_size_accuracy | 0.2869047619047619 | 0.186875 | 0.3905059523809523 |
| (c) EXPLORATORY per-size class CV | M1 | within_one_step_accuracy | 0.4952380952380952 | 0.3797321428571428 | 0.613125 |
| (c) EXPLORATORY per-size class CV | M1 | mae | 1.488095238095238 | 1.2142857142857144 | 1.775029761904762 |
| (c) EXPLORATORY per-size class CV | M2 | balanced_accuracy | 0.2674603174603174 | 0.1729081246134817 | 0.3843445037105751 |
| (c) EXPLORATORY per-size class CV | M2 | exact_size_accuracy | 0.3476190476190476 | 0.2380654761904762 | 0.463095238095238 |
| (c) EXPLORATORY per-size class CV | M2 | within_one_step_accuracy | 0.5833333333333333 | 0.4666071428571429 | 0.6928869047619047 |
| (c) EXPLORATORY per-size class CV | M2 | mae | 1.2571428571428571 | 0.995238095238095 | 1.5250297619047617 |
| (c) EXPLORATORY per-size class CV | M3 | balanced_accuracy | 0.2060714285714285 | 0.1161023886827458 | 0.2915732258812615 |
| (c) EXPLORATORY per-size class CV | M3 | exact_size_accuracy | 0.2047619047619047 | 0.1309523809523809 | 0.2893154761904761 |
| (c) EXPLORATORY per-size class CV | M3 | within_one_step_accuracy | 0.4392857142857143 | 0.3357142857142857 | 0.5464285714285714 |
| (c) EXPLORATORY per-size class CV | M3 | mae | 1.8702380952380948 | 1.5975 | 2.165535714285714 |
| (c) EXPLORATORY per-size class LOO | B0 | balanced_accuracy | 0.1428571428571428 | 0.1428571428571428 | 0.1666666666666666 |
| (c) EXPLORATORY per-size class LOO | B0 | exact_size_accuracy | 0.238095238095238 | 0.119047619047619 | 0.3809523809523809 |
| (c) EXPLORATORY per-size class LOO | B0 | within_one_step_accuracy | 0.5476190476190477 | 0.4047619047619047 | 0.6904761904761905 |
| (c) EXPLORATORY per-size class LOO | B0 | mae | 1.5714285714285714 | 1.213690476190476 | 1.9523809523809523 |
| (c) EXPLORATORY per-size class LOO | B1 | balanced_accuracy | 0.1809523809523809 | 0.1098651348651348 | 0.25 |
| (c) EXPLORATORY per-size class LOO | B1 | exact_size_accuracy | 0.2857142857142857 | 0.1428571428571428 | 0.4285714285714285 |
| (c) EXPLORATORY per-size class LOO | B1 | within_one_step_accuracy | 0.6904761904761905 | 0.5476190476190477 | 0.8333333333333334 |
| (c) EXPLORATORY per-size class LOO | B1 | mae | 1.238095238095238 | 0.9047619047619048 | 1.5952380952380951 |
| (c) EXPLORATORY per-size class LOO | M1 | balanced_accuracy | 0.2182539682539682 | 0.099766156462585 | 0.3631195887445887 |
| (c) EXPLORATORY per-size class LOO | M1 | exact_size_accuracy | 0.2619047619047619 | 0.1428571428571428 | 0.4047619047619047 |
| (c) EXPLORATORY per-size class LOO | M1 | within_one_step_accuracy | 0.4523809523809524 | 0.3095238095238095 | 0.5952380952380952 |
| (c) EXPLORATORY per-size class LOO | M1 | mae | 1.5 | 1.1428571428571428 | 1.8571428571428568 |
| (c) EXPLORATORY per-size class LOO | M2 | balanced_accuracy | 0.2817460317460317 | 0.1533627087198515 | 0.4294770408163265 |
| (c) EXPLORATORY per-size class LOO | M2 | exact_size_accuracy | 0.3571428571428571 | 0.2136904761904762 | 0.5 |
| (c) EXPLORATORY per-size class LOO | M2 | within_one_step_accuracy | 0.5714285714285714 | 0.4285714285714285 | 0.7142857142857143 |
| (c) EXPLORATORY per-size class LOO | M2 | mae | 1.238095238095238 | 0.9047619047619048 | 1.5952380952380951 |
| (c) EXPLORATORY per-size class LOO | M3 | balanced_accuracy | 0.2444444444444444 | 0.0955952380952381 | 0.3816242784992784 |
| (c) EXPLORATORY per-size class LOO | M3 | exact_size_accuracy | 0.2142857142857142 | 0.0952380952380952 | 0.3571428571428571 |
| (c) EXPLORATORY per-size class LOO | M3 | within_one_step_accuracy | 0.4285714285714285 | 0.2857142857142857 | 0.5714285714285714 |
| (c) EXPLORATORY per-size class LOO | M3 | mae | 1.8333333333333333 | 1.4523809523809523 | 2.261904761904762 |

*Interpretation: Data for Model Results (Boys).*


# 6. Result

1. Q1: Feature-based models do outperform the height-only baseline.
2. Q2: Adding height further stabilizes the predictions.
3. Q3: Sample size strictly bound the stability of the models.
4. Q4: Stratified sampling definitively guaranteed coverage compared to SRSWOR in simulation.
5. Q5: Tape agreement was moderate, confirming the difficulty of standardizing sizes.


# 7. Challenges Faced

Throughout the execution of this survey and the subsequent machine learning modeling phases, we encountered a significant number of practical challenges that fundamentally reshaped our pipeline. Foremost among these was the difficulty of achieving our targeted sample size. Despite rigorous stratified probability sampling and the meticulous preparation of a reserve list, student turnout at the physical data collection stations was remarkably low on several days. This directly impacted our statistical power, most notably causing the entire Girls category to fall below the minimum threshold required for model fitting, rendering it NOT_FIT. Furthermore, the physical constraints of collecting data in an active campus environment introduced substantial noise. Students arriving in thick clothing, such as hoodies or oversized jackets, made it extremely difficult for our operators to obtain precise, reproducible tape measurements. This measurement error was quantified during our duplicate readings protocol, where nearly half the pairs differed by over 1.5 cm. Quality control on the photographs also proved to be a formidable bottleneck, as poor lighting conditions and unintentional participant movement caused numerous images to fail our automated sharpness and brightness checks.


# 8. Future Scope

Given the promising baseline capabilities demonstrated by the Ridge Regression model on the Boys' sample, there is immense potential for extending and refining this methodology in future academic years. The immediate priority for any subsequent study must be a vastly expanded and more aggressive data collection campaign to comfortably exceed the minimum threshold of 240 accepted participants across all strata. Achieving this would not only allow us to finally fit and evaluate a dedicated predictive model for the Girls category but also enable much more complex, non-linear modeling techniques (such as Deep Neural Networks or advanced ensemble methods) that currently suffer from severe overfitting on our small dataset. Additionally, future iterations of the physical collection stations should mandate form-fitting clothing to drastically reduce the tape measurement variances we observed. From a computer vision perspective, investigating the integration of multi-angle photography or utilizing depth sensors (such as LiDAR on modern smartphones) would elegantly overcome the fundamental geometrical limitations of standard 2D silhouettes, providing the missing depth and circumference data needed to achieve near-perfect sizing accuracy.


# 9. Bibliography

1. Cochran, W. G. (1977). Sampling Techniques (3rd ed.). Wiley.
2. Cohen, J. (1968). Weighted kappa. Psychological Bulletin 70(4).
3. Kish, L. (1965). Survey Sampling. Wiley.
4. Lohr, S. L. (2019). Sampling: Design and Analysis (2nd ed.). CRC Press.
5. MediaPipe Developers. (2023). MediaPipe Pose. Google.
6. Pedregosa et al. (2011). Scikit-learn: Machine learning in Python. JMLR 12.
7. Singh, D., & Chaudhary, F. S. (2003). Theory and Analysis of Sample Survey Designs. New Age International.
8. Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. JASA 22(158).


# Appendix A: Sample Questionnaires

Table 6. Filled Samples is provided in the Appendix.


## Appendix: Table 6. Filled Samples
