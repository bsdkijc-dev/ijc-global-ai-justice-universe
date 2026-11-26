"""Phase 3 (Task 028): Cross-Jurisdictional Statutory Conflict & Harmonization Mapper."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from src.prototype.neuro_symbolic_reasoner import retrieve_top_authorities

ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS_JSON = ROOT / "data" / "curated" / "verified_authority_corpus.json"
MATRIX_CSV = ROOT / "data" / "curated" / "statutory_harmonization_matrix.csv"
RESULTS_JSON = ROOT / "data" / "sample" / "statutory_harmonization_results.json"
REPORTS_DIR = ROOT / "reports"

NORMS = [
    ("NORM-01_NON_DELEGATION_ADJUDICATION", "judicial decision-making reserved to human judges non-delegation"),
    ("NORM-02_CITATION_GROUNDING_REQUIRED", "hallucinated citations court filing verification sanction"),
    ("NORM-03_BIOMETRIC_CORROBORATION_REQUIRED", "facial recognition FRT biometric corroboration evidence"),
    ("NORM-04_AUDIT_TRANSPARENCY_REQUIRED", "source code access risk scoring algorithmic transparency"),
    ("NORM-05_CONTESTABILITY_RIGHT_REQUIRED", "automated decision-making explanation contestability right"),
    ("NORM-06_SYNTHETIC_MEDIA_PROVENANCE_REQUIRED", "deepfake synthetic media digital evidence provenance"),
]

REGIONS = [
    ("ASEAN_APAC", ["Australia", "China", "India", "Japan", "Malaysia", "Philippines", "Singapore", "South Korea", "Taiwan", "Thailand", "New Zealand"]),
    ("EUROPE_UK", ["European Union", "France", "Germany", "Italy", "Spain", "The Netherlands", "United Kingdom", "Finland", "Poland", "Sweden"]),
    ("LATAM", ["Argentina", "Brazil", "Chile", "Colombia", "Mexico"]),
    ("SSA_MENA", ["Egypt", "Ethiopia", "Israel", "Kenya", "Morocco", "Nigeria", "Qatar", "Saudi Arabia", "South Africa", "Tunisia", "UAE"]),
    ("NAM_ECA", ["Canada", "United States", "Albania", "Armenia", "Georgia", "Ukraine", "Moldova"]),
]


def run_harmonization_mapper() -> Dict[str, Any]:
    corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
    rows: List[Dict[str, Any]] = []

    for region_code, countries in REGIONS:
        regional_corpus = [c for c in corpus if c["jurisdiction"] in countries]
        if not regional_corpus:
            regional_corpus = corpus
        for norm_id, norm_query in NORMS:
            top_matches = retrieve_top_authorities(norm_query, regional_corpus, top_k=2)
            top = top_matches[0]
            sim = top["similarity"]
            status = (
                "CONVERGENT_ANCHOR"
                if sim >= 0.25
                else ("EMERGING_ALIGNMENT" if sim >= 0.12 else "DIVERGENT_OR_GAP")
            )
            rows.append(
                {
                    "region_code": region_code,
                    "norm_id": norm_id,
                    "harmonization_status": status,
                    "top_auth_id": top["auth_id"],
                    "top_jurisdiction": top["jurisdiction"],
                    "top_citation": top["citation"],
                    "similarity_score": sim,
                    "regional_corpus_size": len(regional_corpus),
                }
            )

    MATRIX_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MATRIX_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "region_code",
                "norm_id",
                "harmonization_status",
                "top_auth_id",
                "top_jurisdiction",
                "top_citation",
                "similarity_score",
                "regional_corpus_size",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    convergent = sum(1 for r in rows if r["harmonization_status"] == "CONVERGENT_ANCHOR")
    emerging = sum(1 for r in rows if r["harmonization_status"] == "EMERGING_ALIGNMENT")
    divergent = sum(1 for r in rows if r["harmonization_status"] == "DIVERGENT_OR_GAP")

    summary = {
        "prototype_id": "IJC-GAJIU-STATUTORY-HARMONIZER-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "total_cells": len(rows),
        "regions_count": len(REGIONS),
        "norms_count": len(NORMS),
        "status_counts": {
            "CONVERGENT_ANCHOR": convergent,
            "EMERGING_ALIGNMENT": emerging,
            "DIVERGENT_OR_GAP": divergent,
        },
        "matrix": rows,
    }
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Phase 3 — Cross-Jurisdictional Statutory Conflict & Harmonization Map",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING` (5 Regions x 6 Symbolic Norms = 30 Grounded Cells)  ",
        f"**Distribution:** `{convergent}` Convergent Anchors | `{emerging}` Emerging Alignment | `{divergent}` Divergent / Gap",
        "",
        "| Region | Norm | Status | Top Grounded Authority |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in rows:
        md.append(
            f"| {r['region_code']} | {r['norm_id']} | {r['harmonization_status']} | "
            f"{r['top_citation']} ({r['top_jurisdiction']}, sim={r['similarity_score']}) |"
        )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "STATUTORY_HARMONIZATION_MAP.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Statutory harmonization complete: {len(rows)} cells ({convergent} convergent, {emerging} emerging, {divergent} gap)")
    return summary


if __name__ == "__main__":
    run_harmonization_mapper()
