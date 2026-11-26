"""Offline Synthetic Media & Digital Evidence Chain-of-Custody Gate (PROTOTYPE_EXPERIMENTAL_NONBINDING)."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "synthetic_media_benchmark_results.json"


def evaluate_evidence_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    has_sha256 = bool(bundle.get("media_sha256", "").strip())
    has_provenance = bool(bundle.get("c2pa_or_device_signature", False))
    corroborated = bool(bundle.get("independent_corroboration", False))
    synthetic_flag = bool(bundle.get("deepfake_or_synthetic_indicator", False))

    if synthetic_flag and not corroborated:
        status = "FLAG_SYNTHETIC_UNCORROBORATED_EXCLUDED_PENDING_HEARING"
    elif not has_sha256 or not has_provenance:
        status = "FLAG_INCOMPLETE_CHAIN_OF_CUSTODY_HITL_REQUIRED"
    else:
        status = "PASS_CHAIN_OF_CUSTODY_VERIFIED_FOR_JUDICIAL_REVIEW"

    audit_hash = hashlib.sha256(json.dumps(bundle, sort_keys=True).encode("utf-8")).hexdigest()[:12].upper()
    return {
        "evidence_id": bundle["evidence_id"],
        "record_type": bundle["record_type"],
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "expected_status": bundle["expected_status"],
        "detected_status": status,
        "audit_hash": audit_hash,
    }


def build_synthetic_benchmark() -> List[Dict[str, Any]]:
    return [
        {
            "evidence_id": "EVID-01",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "media_sha256": "a" * 64,
            "c2pa_or_device_signature": True,
            "independent_corroboration": True,
            "deepfake_or_synthetic_indicator": False,
            "expected_status": "PASS_CHAIN_OF_CUSTODY_VERIFIED_FOR_JUDICIAL_REVIEW",
        },
        {
            "evidence_id": "EVID-02",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "media_sha256": "b" * 64,
            "c2pa_or_device_signature": True,
            "independent_corroboration": False,
            "deepfake_or_synthetic_indicator": True,
            "expected_status": "FLAG_SYNTHETIC_UNCORROBORATED_EXCLUDED_PENDING_HEARING",
        },
        {
            "evidence_id": "EVID-03",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "media_sha256": "",
            "c2pa_or_device_signature": False,
            "independent_corroboration": True,
            "deepfake_or_synthetic_indicator": False,
            "expected_status": "FLAG_INCOMPLETE_CHAIN_OF_CUSTODY_HITL_REQUIRED",
        },
        {
            "evidence_id": "EVID-04",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "media_sha256": "c" * 64,
            "c2pa_or_device_signature": True,
            "independent_corroboration": True,
            "deepfake_or_synthetic_indicator": True,
            "expected_status": "PASS_CHAIN_OF_CUSTODY_VERIFIED_FOR_JUDICIAL_REVIEW",
        },
    ]


def run_benchmark() -> Dict[str, Any]:
    cases = build_synthetic_benchmark()
    results = [evaluate_evidence_bundle(c) for c in cases]
    exact = sum(1 for r in results if r["detected_status"] == r["expected_status"])
    acc = round(exact / len(cases), 4)

    summary = {
        "prototype_id": "IJC-GAJIU-SYNTHETIC-MEDIA-GATE-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "benchmark_cases": len(cases),
        "exact_gate_accuracy": acc,
        "results": results,
    }
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Synthetic Media & Chain-of-Custody Gate Evaluation",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Zero-Budget Offline CPU)  ",
        f"**Benchmark Cases (`SYNTHETIC_BENCHMARK_TEST_CASE`):** {len(cases)}  ",
        f"**Exact Gate Accuracy:** {acc * 100:.1f}% ({exact}/{len(cases)})",
        "",
        "| Evidence ID | Detected Status | Audit Hash |",
        "| :--- | :--- | :--- |",
    ]
    for r in results:
        md.append(f"| {r['evidence_id']} | {r['detected_status']} | `{r['audit_hash']}` |")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "SYNTHETIC_MEDIA_GATE_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Synthetic media gate benchmark complete: {exact}/{len(cases)} exact accuracy")
    return summary


if __name__ == "__main__":
    run_benchmark()
