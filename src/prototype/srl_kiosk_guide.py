"""Offline Low-Bandwidth Legal Aid & Self-Represented Litigant (SRL) Kiosk Prototype."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "srl_kiosk_benchmark_results.json"

RULES = [
    ("DOMESTIC_VIOLENCE_VICTIM_SUPPORT", ["domestic", "abuse", "violence", "threat", "harassment", "shelter"], "GLS-31"),
    ("CRIMINAL_DEFENCE_AID", ["arrested", "bail", "police", "detained", "criminal", "warrant"], "GLS-33"),
    ("LABOR_DISPUTE", ["wage", "dismissed", "employer", "salary", "labor", "overtime"], "GLS-46"),
    ("SMALL_CLAIMS_CIVIL", ["debt", "contract", "rent", "invoice", "deposit", "small claims"], "GLS-32"),
    ("ADMINISTRATIVE_APPEAL", ["permit", "license", "agency", "administrative", "tax", "benefit"], "GLS-25"),
]


def triage_srl_query(text: str) -> Dict[str, Any]:
    low = text.lower()
    matched_domain = "GENERAL_LEGAL_INFORMATION_REFERRAL"
    matched_glossary = "GLS-18"
    for domain, keywords, gls in RULES:
        if any(k in low for k in keywords):
            matched_domain = domain
            matched_glossary = gls
            break

    audit_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12].upper()
    return {
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING_INFORMATION_ONLY",
        "disclaimer": "Informational triage only; not legal advice. Consult a qualified lawyer or legal aid officer.",
        "triage_domain": matched_domain,
        "glossary_ref": matched_glossary,
        "audit_hash": audit_hash,
    }


def build_synthetic_benchmark() -> List[Dict[str, str]]:
    return [
        {"case_id": "SRL-01", "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE", "expected": "DOMESTIC_VIOLENCE_VICTIM_SUPPORT", "text": "Need safe shelter and protection order after domestic violence threat."},
        {"case_id": "SRL-02", "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE", "expected": "CRIMINAL_DEFENCE_AID", "text": "Family member arrested without warrant and seeking bail legal aid."},
        {"case_id": "SRL-03", "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE", "expected": "LABOR_DISPUTE", "text": "Unpaid overtime salary after employer dismissed worker without notice."},
        {"case_id": "SRL-04", "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE", "expected": "SMALL_CLAIMS_CIVIL", "text": "Landlord withheld security deposit and unpaid small claims debt."},
        {"case_id": "SRL-05", "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE", "expected": "ADMINISTRATIVE_APPEAL", "text": "Appealing municipal business permit and administrative agency decision."},
    ]


def run_benchmark() -> Dict[str, Any]:
    cases = build_synthetic_benchmark()
    results = []
    exact = 0
    for c in cases:
        res = triage_srl_query(c["text"])
        if res["triage_domain"] == c["expected"]:
            exact += 1
        results.append({
            "case_id": c["case_id"],
            "record_type": c["record_type"],
            "expected": c["expected"],
            "detected": res["triage_domain"],
            "glossary_ref": res["glossary_ref"],
            "audit_hash": res["audit_hash"],
        })

    acc = round(exact / len(cases), 4)
    summary = {
        "prototype_id": "IJC-GAJIU-SRL-KIOSK-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING_INFORMATION_ONLY",
        "benchmark_cases": len(cases),
        "exact_triage_accuracy": acc,
        "results": results,
    }
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Offline SRL Legal Aid Kiosk Evaluation",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING_INFORMATION_ONLY`  ",
        f"**Exact Triage Accuracy:** {acc * 100:.1f}% ({exact}/{len(cases)})",
        "",
        "| Case ID | Expected Domain | Detected Domain | Glossary Ref | Audit Hash |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        md.append(f"| {r['case_id']} | {r['expected']} | {r['detected']} | {r['glossary_ref']} | `{r['audit_hash']}` |")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "SRL_KIOSK_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"SRL Kiosk benchmark complete: {exact}/{len(cases)} exact accuracy")
    return summary


if __name__ == "__main__":
    run_benchmark()
