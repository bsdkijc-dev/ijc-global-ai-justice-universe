"""Offline Legal Tech Procurement & Data Sovereignty Auditor (Pillar P25)."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "procurement_audit_benchmark_results.json"


def audit_procurement(proposal: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "auditable_or_open_source": bool(proposal.get("auditable_or_open_source", False)),
        "sovereign_data_residency": bool(proposal.get("sovereign_data_residency", False)),
        "open_export_no_lock_in": bool(proposal.get("open_export_no_lock_in", False)),
        "aia_disclosure_included": bool(proposal.get("aia_disclosure_included", False)),
        "exit_and_sunset_clause": bool(proposal.get("exit_and_sunset_clause", False)),
    }
    passed = sum(1 for v in checks.values() if v)
    score = round((passed / len(checks)) * 100.0, 1)

    if not checks["sovereign_data_residency"] or not checks["auditable_or_open_source"]:
        status = "FLAG_SOVEREIGNTY_OR_AUDITABILITY_GAP"
    elif passed == len(checks):
        status = "PASS_SOVEREIGN_PROCUREMENT_READY"
    else:
        status = "CONDITIONAL_REMEDIATION_REQUIRED"

    audit_hash = hashlib.sha256(json.dumps(proposal, sort_keys=True).encode("utf-8")).hexdigest()[:12].upper()
    return {
        "proposal_id": proposal["proposal_id"],
        "record_type": proposal["record_type"],
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "sovereignty_score": score,
        "expected_status": proposal["expected_status"],
        "detected_status": status,
        "audit_hash": audit_hash,
    }


def build_synthetic_benchmark() -> List[Dict[str, Any]]:
    return [
        {
            "proposal_id": "PROC-01",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "auditable_or_open_source": True,
            "sovereign_data_residency": True,
            "open_export_no_lock_in": True,
            "aia_disclosure_included": True,
            "exit_and_sunset_clause": True,
            "expected_status": "PASS_SOVEREIGN_PROCUREMENT_READY",
        },
        {
            "proposal_id": "PROC-02",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "auditable_or_open_source": False,
            "sovereign_data_residency": True,
            "open_export_no_lock_in": True,
            "aia_disclosure_included": True,
            "exit_and_sunset_clause": True,
            "expected_status": "FLAG_SOVEREIGNTY_OR_AUDITABILITY_GAP",
        },
        {
            "proposal_id": "PROC-03",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "auditable_or_open_source": True,
            "sovereign_data_residency": False,
            "open_export_no_lock_in": False,
            "aia_disclosure_included": True,
            "exit_and_sunset_clause": True,
            "expected_status": "FLAG_SOVEREIGNTY_OR_AUDITABILITY_GAP",
        },
        {
            "proposal_id": "PROC-04",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "auditable_or_open_source": True,
            "sovereign_data_residency": True,
            "open_export_no_lock_in": False,
            "aia_disclosure_included": True,
            "exit_and_sunset_clause": True,
            "expected_status": "CONDITIONAL_REMEDIATION_REQUIRED",
        },
    ]


def run_benchmark() -> Dict[str, Any]:
    cases = build_synthetic_benchmark()
    results = [audit_procurement(c) for c in cases]
    exact = sum(1 for r in results if r["detected_status"] == r["expected_status"])
    acc = round(exact / len(cases), 4)

    summary = {
        "prototype_id": "IJC-GAJIU-PROCUREMENT-AUDITOR-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "benchmark_cases": len(cases),
        "exact_audit_accuracy": acc,
        "results": results,
    }
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Legal Tech Procurement & Data Sovereignty Audit Evaluation",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Pillar `P25`)  ",
        f"**Exact Audit Accuracy:** {acc * 100:.1f}% ({exact}/{len(cases)})",
        "",
        "| Proposal ID | Sovereignty Score | Detected Status | Audit Hash |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        md.append(f"| {r['proposal_id']} | {r['sovereignty_score']} | {r['detected_status']} | `{r['audit_hash']}` |")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "PROCUREMENT_AUDIT_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Procurement auditor benchmark complete: {exact}/{len(cases)} exact accuracy")
    return summary


if __name__ == "__main__":
    run_benchmark()
