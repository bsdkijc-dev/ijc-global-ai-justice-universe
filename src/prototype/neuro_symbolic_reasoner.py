"""Phase 3 (Task 026): Neuro-Symbolic Legal Reasoning & Comparative Precedent Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

from src.originality.deduplicator import compute_tfidf_matrix, tokenize

ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS_JSON = ROOT / "data" / "curated" / "verified_authority_corpus.json"
REPORTS_DIR = ROOT / "reports"
BENCHMARK_OUT = ROOT / "data" / "sample" / "neuro_symbolic_benchmark_results.json"


def retrieve_top_authorities(query_text: str, corpus: List[Dict[str, str]], top_k: int = 3) -> List[Dict[str, Any]]:
    docs = [tokenize(f"{c['citation']} {c['authority_type']} {c['jurisdiction']}") for c in corpus]
    q_tokens = tokenize(query_text)
    mat = compute_tfidf_matrix(docs + [q_tokens])
    sims = mat[:-1] @ mat[-1]
    top_idx = np.argsort(-sims)[:top_k]
    return [
        {
            "auth_id": corpus[i]["auth_id"],
            "citation": corpus[i]["citation"],
            "jurisdiction": corpus[i]["jurisdiction"],
            "similarity": round(float(sims[i]), 4),
        }
        for i in top_idx
    ]


def evaluate_neuro_symbolic(fact_pattern: Dict[str, Any], corpus: List[Dict[str, str]]) -> Dict[str, Any]:
    triggered_norms: List[str] = []
    if not fact_pattern.get("human_judge_final_authority", True):
        triggered_norms.append("NORM-01_NON_DELEGATION_ADJUDICATION")
    if fact_pattern.get("unverified_citations_present", False):
        triggered_norms.append("NORM-02_CITATION_GROUNDING_REQUIRED")
    if fact_pattern.get("sole_basis_biometric_frt", False) and not fact_pattern.get("independent_corroboration", False):
        triggered_norms.append("NORM-03_BIOMETRIC_CORROBORATION_REQUIRED")
    if fact_pattern.get("opaque_proprietary_risk_score", False) and not fact_pattern.get("source_code_auditable", False):
        triggered_norms.append("NORM-04_AUDIT_TRANSPARENCY_REQUIRED")
    if fact_pattern.get("solely_automated_decision", False) and not fact_pattern.get("contestability_right_provided", False):
        triggered_norms.append("NORM-05_CONTESTABILITY_RIGHT_REQUIRED")
    if fact_pattern.get("unverified_synthetic_media", False):
        triggered_norms.append("NORM-06_SYNTHETIC_MEDIA_PROVENANCE_REQUIRED")

    precedents = retrieve_top_authorities(fact_pattern["query_context"], corpus, top_k=3)
    verdict = "COMPLIANT_WITH_SYMBOLIC_NORMS" if not triggered_norms else "NON_COMPLIANT_SAFEGUARDS_TRIGGERED"
    return {
        "case_id": fact_pattern["case_id"],
        "record_type": fact_pattern["record_type"],
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "expected_norm": fact_pattern["expected_norm"],
        "triggered_norms": triggered_norms,
        "verdict": verdict,
        "grounded_precedents": precedents,
    }


def build_synthetic_benchmark() -> List[Dict[str, Any]]:
    return [
        {
            "case_id": "NSY-01",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "human_judge_final_authority": False,
            "query_context": "Law 132/2025 judicial decision-making reserved to human judges",
            "expected_norm": "NORM-01_NON_DELEGATION_ADJUDICATION",
        },
        {
            "case_id": "NSY-02",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "unverified_citations_present": True,
            "query_context": "Mata v Avianca Ayinde hallucinated citations court filing",
            "expected_norm": "NORM-02_CITATION_GROUNDING_REQUIRED",
        },
        {
            "case_id": "NSY-03",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "sole_basis_biometric_frt": True,
            "independent_corroboration": False,
            "query_context": "114 Tai-Shang 5166 FRT corroboration facial recognition",
            "expected_norm": "NORM-03_BIOMETRIC_CORROBORATION_REQUIRED",
        },
        {
            "case_id": "NSY-04",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "opaque_proprietary_risk_score": True,
            "source_code_auditable": False,
            "query_context": "State v Loomis 1119/2025 source code access risk scoring",
            "expected_norm": "NORM-04_AUDIT_TRANSPARENCY_REQUIRED",
        },
        {
            "case_id": "NSY-05",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "solely_automated_decision": True,
            "contestability_right_provided": False,
            "query_context": "Proclamation 1321/2024 PIPA Art 37-2 automated decision right",
            "expected_norm": "NORM-05_CONTESTABILITY_RIGHT_REQUIRED",
        },
        {
            "case_id": "NSY-06",
            "record_type": "SYNTHETIC_BENCHMARK_TEST_CASE",
            "unverified_synthetic_media": True,
            "query_context": "Proposed FRE Rule 707 Digital Evidence deepfake",
            "expected_norm": "NORM-06_SYNTHETIC_MEDIA_PROVENANCE_REQUIRED",
        },
    ]


def run_benchmark() -> Dict[str, Any]:
    corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
    cases = build_synthetic_benchmark()
    results = [evaluate_neuro_symbolic(c, corpus) for c in cases]
    exact = sum(1 for r in results if r["expected_norm"] in r["triggered_norms"])
    acc = round(exact / len(cases), 4)

    summary = {
        "prototype_id": "IJC-GAJIU-NEURO-SYMBOLIC-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "authority_corpus_size": len(corpus),
        "benchmark_cases": len(cases),
        "exact_norm_accuracy": acc,
        "results": results,
    }
    BENCHMARK_OUT.parent.mkdir(parents=True, exist_ok=True)
    BENCHMARK_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Phase 3 — Neuro-Symbolic Legal Reasoning Benchmark",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (Symbolic Norms + TF-IDF Retrieval over 238 Oxford Authorities)  ",
        f"**Exact Symbolic Norm Accuracy:** {acc * 100:.1f}% ({exact}/{len(cases)})",
        "",
        "| Case ID | Triggered Norm | Top Retrieved Precedent |",
        "| :--- | :--- | :--- |",
    ]
    for r in results:
        top_p = r["grounded_precedents"][0]
        md.append(f"| {r['case_id']} | {', '.join(r['triggered_norms'])} | {top_p['citation']} ({top_p['jurisdiction']}, sim={top_p['similarity']}) |")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "NEURO_SYMBOLIC_BENCHMARK.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Neuro-Symbolic benchmark complete: {exact}/{len(cases)} exact accuracy (corpus={len(corpus)})")
    return summary


if __name__ == "__main__":
    run_benchmark()
