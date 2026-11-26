"""Offline CPU-first Risk-Scoring Disparity & Fairness Audit Simulator (Synthetic Benchmark)."""

import json
import random
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "risk_audit_benchmark_results.json"


def generate_synthetic_cohort(n: int = 200, seed: int = 202709) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []
    for i in range(n):
        group = "GROUP_A" if i < n // 2 else "GROUP_B"
        actual_outcome = 1 if rng.random() < 0.30 else 0
        # Inject intentional false-positive disparity in GROUP_B to test audit detection
        fp_prob = 0.12 if group == "GROUP_A" else 0.34
        tp_prob = 0.72
        if actual_outcome == 1:
            pred_high = 1 if rng.random() < tp_prob else 0
        else:
            pred_high = 1 if rng.random() < fp_prob else 0
        records.append({
            "record_id": f"SYN-RISK-{i+1:03d}",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "group": group,
            "actual_outcome": actual_outcome,
            "predicted_high_risk": pred_high,
        })
    return records


def audit_disparity(records: List[Dict[str, Any]], fpr_gap_threshold: float = 0.10) -> Dict[str, Any]:
    metrics: Dict[str, Dict[str, float]] = {}
    for grp in sorted({r["group"] for r in records}):
        sub = [r for r in records if r["group"] == grp]
        neg = [r for r in sub if r["actual_outcome"] == 0]
        pos = [r for r in sub if r["actual_outcome"] == 1]
        fp = sum(1 for r in neg if r["predicted_high_risk"] == 1)
        tp = sum(1 for r in pos if r["predicted_high_risk"] == 1)
        sel = sum(1 for r in sub if r["predicted_high_risk"] == 1)
        metrics[grp] = {
            "count": len(sub),
            "selection_rate": round(sel / max(len(sub), 1), 4),
            "false_positive_rate": round(fp / max(len(neg), 1), 4),
            "true_positive_rate": round(tp / max(len(pos), 1), 4),
        }

    fpr_gap = round(abs(metrics["GROUP_A"]["false_positive_rate"] - metrics["GROUP_B"]["false_positive_rate"]), 4)
    sel_gap = round(abs(metrics["GROUP_A"]["selection_rate"] - metrics["GROUP_B"]["selection_rate"]), 4)
    status = (
        "FLAG_DISPARITY_EXCEEDS_THRESHOLD_HITL_REVIEW"
        if fpr_gap > fpr_gap_threshold
        else "PASS_WITHIN_THRESHOLD"
    )
    return {
        "prototype_id": "IJC-GAJIU-RISK-AUDIT-SIM-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "cohort_size": len(records),
        "fpr_gap_threshold": fpr_gap_threshold,
        "false_positive_rate_gap": fpr_gap,
        "selection_rate_gap": sel_gap,
        "audit_status": status,
        "group_metrics": metrics,
    }


def main() -> None:
    cohort = generate_synthetic_cohort()
    res = audit_disparity(cohort)
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(res, indent=2), encoding="utf-8")

    md = [
        "# Risk-Scoring Disparity & Fairness Audit Simulator Report",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Synthetic Cohort `n=200`, Zero PII)  ",
        f"**FPR Disparity Gap:** `{res['false_positive_rate_gap']}` (Threshold: `{res['fpr_gap_threshold']}`)  ",
        f"**Selection Rate Gap:** `{res['selection_rate_gap']}`  ",
        f"**Audit Status:** `{res['audit_status']}`",
        "",
        "## Group Metrics",
        "| Group | Count | Selection Rate | False Positive Rate | True Positive Rate |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for grp, m in res["group_metrics"].items():
        md.append(f"| {grp} | {m['count']} | {m['selection_rate']} | {m['false_positive_rate']} | {m['true_positive_rate']} |")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "RISK_AUDIT_SIMULATOR_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Risk audit simulator complete: FPR gap={res['false_positive_rate_gap']} | {res['audit_status']}")


if __name__ == "__main__":
    main()
