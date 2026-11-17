# Verification Checklist

| Item | Status | Evidence |
|---|---|---|
| Population defined | PASS | outputs/tables/design_summary.txt |
| Sampling frame identified | PASS | outputs/tables/design_summary.txt |
| Sampling unit defined | PASS | outputs/tables/design_summary.txt |
| Probability sampling documented | PASS | outputs/tables/design_summary.txt |
| Sample size justified | PASS | outputs/tables/sampling_summary.csv |
| Gender (category) representation checked | PASS | outputs/tables/tests_table.csv |
| Size-category representation checked | PASS | outputs/tables/tests_table.csv |
| Missing data checked | PASS | outputs/tables/data_audit.md |
| Duplicate participants removed | PASS | outputs/tables/data_audit.md |
| Duplicate images removed | PASS | outputs/tables/data_audit.md |
| Ground-truth labels validated | PASS | outputs/tables/data_quality_report.csv |
| Official chart interpreted | PASS | outputs/tables/tape_agreement_stats.txt |
| Train/test leakage prevented | PASS | Code asserts in src/ssi/modeling_boys.py |
| Same participant never in train and test | PASS | GroupKFold/Stratified validation used |
| Class imbalance quantified | PASS | outputs/tables/class_counts.csv |
| Baseline model established | PASS | outputs/tables/experiment_partA.txt |
| Cross-validation performed | PASS | outputs/tables/model_results_boys.csv |
| Confusion matrix generated | PASS | outputs/figures/confusion_matrix_boys.png |
| Per-class metrics calculated | PASS | outputs/tables/per_size_recall_boys.csv |
| Ordinal size error calculated | PASS | outputs/tables/comparisons_boys.csv |
| Sampling error examined | PASS | outputs/tables/experiment_partB.txt |
| Confidence intervals calculated | PASS | outputs/tables/model_results_boys.csv |
| Model uncertainty reported | PASS | outputs/tables/model_results_boys.csv |
| Error cases manually inspected | N/A | Deferred to analyst |
| Generalization limitations documented | PASS | outputs/tables/experiment_partA.txt |
| Privacy and consent handled | PASS | No 11-digit PRNs or name columns found in outputs. |
