"""Offline CPU-first Pilot Prototype: Grounded Citation Verification Gate & Appellate Triage."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

from src.originality.deduplicator import compute_tfidf_matrix, tokenize

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "prototype_benchmark_results.json"

CITATION_RE = re.compile(
    r"(?:\[\d{4}\]\s+[A-Z]{2,10}\s+\d+|\b[A-Z][A-Za-z0-9.\-]+\s+v\.?\s+[A-Z][A-Za-z0-9.\-]+\b|\bLaw\s+No\.?\s+[A-Z0-9\-\/]+\b)"
)

# Verified authority registry seeded from Oxford AI Justice Atlas public case/statute citations
VERIFIED_AUTHORITY_REGISTRY = [
    {"auth_id": "AUTH-01", "citation": "State v Loomis", "jurisdiction": "United States"},
    {"auth_id": "AUTH-02", "citation": "Mata v Avianca", "jurisdiction": "United States"},
    {"auth_id": "AUTH-03", "citation": "Parker v Forsyth", "jurisdiction": "South Africa"},
    {"auth_id": "AUTH-04", "citation": "[2025] ADGMCFI 0032", "jurisdiction": "United Arab Emirates"},
    {"auth_id": "AUTH-05", "citation": "[2025] NZSC 40", "jurisdiction": "New Zealand"},
    {"auth_id": "AUTH-06", "citation": "[2025] UKFTT 1112", "jurisdiction": "United Kingdom"},
    {"auth_id": "AUTH-07", "citation": "Law No. ORK-1115", "jurisdiction": "Uzbekistan"},
    {"auth_id": "AUTH-08", "citation": "Law No. 243-FZ", "jurisdiction": "Russia"},
    {"auth_id": "AUTH-09", "citation": "Williams v Detroit", "jurisdiction": "United States"},
    {"auth_id": "AUTH-10", "citation": "Ewert v Canada", "jurisdiction": "Canada"},
]


def verify_citations(text: str, registry: List[Dict[str, str]] = VERIFIED_AUTHORITY_REGISTRY) -> Dict[str, Any]:
    found = CITATION_RE.findall(text)
    known = {item["citation"].lower(): item for item in registry}

    verified: List[Dict[str, str]] = []
    unverified: List[str] = []

    for cit in found:
        key = cit.strip().lower()
        if key in known:
            verified.append({"citation": cit, "auth_id": known[key]["auth_id"], "status": "VERIFIED_AUTHORITY"})
        else:
            unverified.append(cit)

    gate_status = "PASS_HUMAN_SIGN_OFF_READY" if not unverified else "FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED"
    audit_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12].upper()

    return {
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "audit_hash": audit_hash,
        "citations_detected": len(found),
        "verified_citations": verified,
        "unverified_citations": unverified,
        "gate_status": gate_status,
    }


def cluster_filings(filings: List[Dict[str, str]], similarity_threshold: float = 0.20) -> List[Dict[str, Any]]:
    docs = [tokenize(f["text"]) for f in filings]
    tfidf = compute_tfidf_matrix(docs)
    sim = tfidf @ tfidf.T

    assigned = [-1] * len(filings)
    cluster_id = 0
    for i in range(len(filings)):
        if assigned[i] != -1:
            continue
        assigned[i] = cluster_id
        for j in range(i + 1, len(filings)):
            if assigned[j] == -1 and float(sim[i, j]) >= similarity_threshold:
                assigned[j] = cluster_id
        cluster_id += 1

    results = []
    for i, f in enumerate(filings):
        cit_res = verify_citations(f["text"])
        results.append({
            "case_id": f["case_id"],
            "record_type": f["record_type"],
            "cluster_id": f"CLU-{assigned[i] + 1:02d}",
            "expected_unverified": f["expected_unverified"],
            "detected_unverified": len(cit_res["unverified_citations"]),
            "citations_detected": cit_res["citations_detected"],
            "gate_status": cit_res["gate_status"],
            "audit_hash": cit_res["audit_hash"],
        })
    return results


def build_synthetic_benchmark() -> List[Dict[str, Any]]:
    return [
        {
            "case_id": "SYN-01",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 0,
            "text": "Appellate labor dispute citing State v Loomis and Ewert v Canada on algorithmic risk transparency.",
        },
        {
            "case_id": "SYN-02",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 1,
            "text": "Appeal brief relying on Parker v Forsyth and fabricated precedent Smith v PhantomCorp on AI disclosure.",
        },
        {
            "case_id": "SYN-03",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 0,
            "text": "Constitutional challenge referencing [2025] ADGMCFI 0032 and Mata v Avianca regarding filing verification.",
        },
        {
            "case_id": "SYN-04",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 2,
            "text": "Submission citing non-existent [2099] XYZSC 999 and Jones v NullAuthority in administrative review.",
        },
        {
            "case_id": "SYN-05",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 0,
            "text": "Digital governance appeal citing Law No. ORK-1115 and [2025] UKFTT 1112 on human-in-the-loop review.",
        },
        {
            "case_id": "SYN-06",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "expected_unverified": 1,
            "text": "Biometric proportionality appeal citing Williams v Detroit alongside unverified Doe v GhostCourt.",
        },
    ]


def run_benchmark() -> Dict[str, Any]:
    filings = build_synthetic_benchmark()
    results = cluster_filings(filings)

    exact_matches = sum(1 for r in results if r["detected_unverified"] == r["expected_unverified"])
    gate_accuracy = round(exact_matches / len(results), 4)
    unique_clusters = len({r["cluster_id"] for r in results})

    summary = {
        "prototype_id": "IJC-GAJIU-PILOT-PROTOTYPE-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "benchmark_cases": len(results),
        "exact_citation_detection_accuracy": gate_accuracy,
        "clusters_formed": unique_clusters,
        "results": results,
    }

    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Pilot Prototype Evaluation Report — Citation Gate & Appellate Triage",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Zero-Budget Offline CPU)  ",
        f"**Benchmark Cases (`SYNTHETIC_BENCHMARK_TEST_CASE`):** {len(results)}  ",
        f"**Exact Unverified-Citation Detection Accuracy:** {gate_accuracy * 100:.1f}% ({exact_matches}/{len(results)})  ",
        f"**TF-IDF Issue Clusters Formed:** {unique_clusters}",
        "",
        "## Benchmark Results",
        "| Case ID | Cluster | Citations Detected | Expected Unverified | Detected Unverified | Gate Status | Audit Hash |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        md.append(
            f"| {r['case_id']} | {r['cluster_id']} | {r['citations_detected']} | {r['expected_unverified']} | "
            f"{r['detected_unverified']} | {r['gate_status']} | `{r['audit_hash']}` |"
        )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "PILOT_PROTOTYPE_EVALUATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Prototype benchmark complete: {exact_matches}/{len(results)} exact accuracy | {unique_clusters} clusters")
    return summary


if __name__ == "__main__":
    run_benchmark()
