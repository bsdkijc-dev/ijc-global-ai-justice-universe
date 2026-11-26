# Risk-Scoring Disparity & Fairness Audit Simulator Report

**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Synthetic Cohort `n=200`, Zero PII)  
**FPR Disparity Gap:** `0.2386` (Threshold: `0.1`)  
**Selection Rate Gap:** `0.24`  
**Audit Status:** `FLAG_DISPARITY_EXCEEDS_THRESHOLD_HITL_REVIEW`

## Group Metrics
| Group | Count | Selection Rate | False Positive Rate | True Positive Rate |
| :--- | :--- | :--- | :--- | :--- |
| GROUP_A | 100 | 0.24 | 0.1143 | 0.5333 |
| GROUP_B | 100 | 0.48 | 0.3529 | 0.75 |
