# Pilot Prototype Evaluation Report — Citation Gate & Appellate Triage

**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Zero-Budget Offline CPU)  
**Benchmark Cases (`SYNTHETIC_BENCHMARK_TEST_CASE`):** 6  
**Exact Unverified-Citation Detection Accuracy:** 100.0% (6/6)  
**TF-IDF Issue Clusters Formed:** 6

## Benchmark Results
| Case ID | Cluster | Citations Detected | Expected Unverified | Detected Unverified | Gate Status | Audit Hash |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SYN-01 | CLU-01 | 2 | 0 | 0 | PASS_HUMAN_SIGN_OFF_READY | `A7564105F4D2` |
| SYN-02 | CLU-02 | 2 | 1 | 1 | FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED | `62D8090FD0DF` |
| SYN-03 | CLU-03 | 2 | 0 | 0 | PASS_HUMAN_SIGN_OFF_READY | `A1543E646E8A` |
| SYN-04 | CLU-04 | 2 | 2 | 2 | FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED | `2855525E0D1D` |
| SYN-05 | CLU-05 | 2 | 0 | 0 | PASS_HUMAN_SIGN_OFF_READY | `F1CBC5A24CDA` |
| SYN-06 | CLU-06 | 2 | 1 | 1 | FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED | `F44C79E38D1F` |
