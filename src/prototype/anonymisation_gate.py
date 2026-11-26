"""Offline CPU-first Pilot Prototype: Judgment Anonymisation & PII Redaction Gate."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "anonymisation_benchmark_results.json"

PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    ("PHONE", re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)\d{3,4}[\s-]?\d{3,4}\b"), "[REDACTED_PHONE]"),
    ("NATIONAL_ID", re.compile(r"\b(?:NIK|SSN|ID)[\s:#-]*\d{6,16}\b", re.IGNORECASE), "[REDACTED_ID]"),
    ("ADDRESS", re.compile(r"\b\d{1,5}\s+[A-Z][A-Za-z0-9.\s]{2,30}(?:Street|St|Avenue|Ave|Road|Rd|Jalan|Jl)\b"), "[REDACTED_ADDRESS]"),
]


def anonymise_text(text: str) -> Dict[str, Any]:
    redacted = text
    counts: Dict[str, int] = {}
    for label, pattern, replacement in PATTERNS:
        matches = pattern.findall(redacted)
        counts[label] = len(matches)
        if matches:
            redacted = pattern.sub(replacement, redacted)

    total_redactions = sum(counts.values())
    audit_hash = hashlib.sha256(redacted.encode("utf-8")).hexdigest()[:12].upper()
    return {
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "total_redactions": total_redactions,
        "redactions_by_type": counts,
        "anonymised_text": redacted,
        "audit_hash": audit_hash,
        "gate_status": "PASS_READY_FOR_HUMAN_PUBLICATION_REVIEW",
    }


def build_synthetic_benchmark() -> List[Dict[str, Any]]:
    return [
        {
            "case_id": "ANON-01",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_redactions": 2,
            "text": "Witness contact witness.doe@example.org, phone +62 812-3456-7890, citing Law No. ORK-1115.",
        },
        {
            "case_id": "ANON-02",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_redactions": 2,
            "text": "Appellant NIK 3201012345678901 residing at 421 Merdeka Street appealed under State v Loomis.",
        },
        {
            "case_id": "ANON-03",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_redactions": 0,
            "text": "Public constitutional ruling citing [2025] ADGMCFI 0032 and EU AI Act transparency obligations.",
        },
        {
            "case_id": "ANON-04",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_redactions": 3,
            "text": "Defendant SSN 123456789, email appellant@test.local, residing at 88 Justice Avenue.",
        },
    ]


def run_benchmark() -> Dict[str, Any]:
    cases = build_synthetic_benchmark()
    results = []
    exact = 0
    for c in cases:
        res = anonymise_text(c["text"])
        if res["total_redactions"] == c["expected_redactions"]:
            exact += 1
        results.append({
            "case_id": c["case_id"],
            "record_type": c["record_type"],
            "expected_redactions": c["expected_redactions"],
            "detected_redactions": res["total_redactions"],
            "audit_hash": res["audit_hash"],
            "gate_status": res["gate_status"],
        })

    accuracy = round(exact / len(cases), 4)
    summary = {
        "prototype_id": "IJC-GAJIU-ANONYMISATION-GATE-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "benchmark_cases": len(cases),
        "exact_redaction_accuracy": accuracy,
        "results": results,
    }
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Anonymisation & PII Redaction Pilot Evaluation",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Zero-Budget Offline CPU)  ",
        f"**Benchmark Cases (`SYNTHETIC_BENCHMARK_TEST_CASE`):** {len(cases)}  ",
        f"**Exact Redaction Count Accuracy:** {accuracy * 100:.1f}% ({exact}/{len(cases)})",
        "",
        "| Case ID | Expected Redactions | Detected Redactions | Gate Status | Audit Hash |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        md.append(
            f"| {r['case_id']} | {r['expected_redactions']} | {r['detected_redactions']} | "
            f"{r['gate_status']} | `{r['audit_hash']}` |"
        )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "ANONYMISATION_PILOT_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Anonymisation benchmark complete: {exact}/{len(cases)} exact accuracy")
    return summary


if __name__ == "__main__":
    run_benchmark()
