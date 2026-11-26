"""Phase 2 (Task 021): ASEAN & Asia-Pacific Comparative Deep-Dive + 500-Program SEA Portfolio."""

import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from src.evidence.provenance import enrich_inspiration_sources, load_accessible_atlas
from src.export.exporter import flatten_program
from src.generator.program_generator import generate_program, load_verified_source_ids
from src.ontology.taxonomy import DIMENSIONS
from src.validation.validator import validate_programs

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
CURATED_DIR = ROOT / "data" / "curated"
REPORTS_DIR = ROOT / "reports"

APAC_OXFORD_JURISDICTIONS = [
    "Malaysia", "Singapore", "Thailand", "The Philippines",
    "Australia", "New Zealand", "China", "India", "Japan", "South Korea", "Taiwan",
]
ASEAN_UNCOVERED_GAPS = ["Indonesia", "Vietnam", "Brunei Darussalam", "Cambodia", "Lao PDR", "Myanmar"]


def build_asean_apac_matrix() -> List[Dict[str, Any]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    by_name = {s["jurisdiction"]: s for s in reg["sources"]}
    rows: List[Dict[str, Any]] = []

    for jur in APAC_OXFORD_JURISDICTIONS:
        src = by_name[jur]
        rows.append({
            "jurisdiction": jur,
            "subregion": "ASEAN" if jur in ("Malaysia", "Singapore", "Thailand", "The Philippines") else "Asia-Pacific",
            "coverage_status": "COVERED_OXFORD_VERIFIED",
            "source_id": src["source_id"],
            "source_url": src["url"],
            "key_ai_systems": src["identified_ai_systems"],
            "key_regulations_and_policies": f"{src['regulatory_instruments']} | {src['judicial_policies']}".strip(" |"),
            "evidence_label": "EXISTING_REAL_WORLD_RECORD",
        })

    for jur in ASEAN_UNCOVERED_GAPS:
        rows.append({
            "jurisdiction": jur,
            "subregion": "ASEAN",
            "coverage_status": "NOT_IN_OXFORD_INITIAL_CORPUS_GAP_IDENTIFIED",
            "source_id": "",
            "source_url": "",
            "key_ai_systems": "",
            "key_regulations_and_policies": "",
            "evidence_label": "RESEARCH_GAP_IDENTIFIED",
        })
    return rows


def generate_sea_500_portfolio() -> List[Dict[str, Any]]:
    rng = random.Random(202721)
    verified_sources = load_verified_source_ids()
    atlas = load_accessible_atlas()
    dim_labels = {dim: {c: l for c, l in vals} for dim, vals in DIMENSIONS.items()}

    seen = set()
    progs: List[Dict[str, Any]] = []
    while len(progs) < 500:
        p = generate_program(rng, verified_sources, dim_labels)
        if p["dimensions"]["D01_jurisdiction_archetype"] != "SEA":
            continue
        if p["tuple_sha256"] in seen:
            continue
        seen.add(p["tuple_sha256"])
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)
        progs.append(p)

    valid, errors = validate_programs(progs)
    assert len(errors) == 0, f"Validation failed on SEA 500: {errors}"
    return valid


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_asean_apac_matrix()
    (CURATED_DIR / "asean_apac_comparative_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (CURATED_DIR / "asean_apac_comparative_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
        writer.writeheader()
        writer.writerows(matrix)

    sea_500 = generate_sea_500_portfolio()
    df_sea = pd.DataFrame([flatten_program(p) for p in sea_500])
    df_sea.to_csv(CURATED_DIR / "asean_sea_programs_500.csv", index=False, encoding="utf-8")
    df_sea.to_parquet(CURATED_DIR / "asean_sea_programs_500.parquet", index=False)

    md = [
        "# Phase 2 — ASEAN & Asia-Pacific Comparative Justice AI Deep-Dive",
        "",
        "**Covered Oxford Jurisdictions (`EXISTING_REAL_WORLD_RECORD`):** 11 (4 ASEAN + 7 Asia-Pacific)  ",
        "**Identified ASEAN Corpus Gaps (`RESEARCH_GAP_IDENTIFIED`):** 6 (Indonesia, Vietnam, Brunei Darussalam, Cambodia, Lao PDR, Myanmar — not in initial Oxford corpus; zero fabricated entries)  ",
        "**Generated SEA Research Portfolio (`PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`):** 500 validated configurations (`seed=202721`)",
        "",
        "## ASEAN & Asia-Pacific Matrix",
        "| Jurisdiction | Subregion | Coverage Status | Source ID |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in matrix:
        md.append(f"| {r['jurisdiction']} | {r['subregion']} | {r['coverage_status']} | {r['source_id'] or 'N/A'} |")
    (REPORTS_DIR / "ASEAN_APAC_DEEP_DIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built ASEAN/APAC matrix ({len(matrix)} rows) & validated {len(sea_500)} SEA research programs")


if __name__ == "__main__":
    main()
