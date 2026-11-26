"""Phase 2 (Task 025): North America & Eastern Europe/Central Asia Deep-Dive + 500-Program Portfolio."""

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

NAM_JURISDICTIONS = ["Canada", "United States"]
ECA_JURISDICTIONS = ["Azerbaijan", "Kazakhstan", "Russia", "Türkiye", "Uzbekistan"]


def build_nam_eca_matrix() -> List[Dict[str, Any]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    by_name = {s["jurisdiction"]: s for s in reg["sources"]}
    rows: List[Dict[str, Any]] = []

    for subreg, jurs in [("NAM", NAM_JURISDICTIONS), ("ECA", ECA_JURISDICTIONS)]:
        for jur in jurs:
            src = by_name[jur]
            rows.append({
                "jurisdiction": jur,
                "subregion": subreg,
                "source_id": src["source_id"],
                "source_url": src["url"],
                "key_ai_systems": src["identified_ai_systems"],
                "regulatory_instruments": src["regulatory_instruments"],
                "reported_cases": src["reported_cases"],
                "evidence_label": "EXISTING_REAL_WORLD_RECORD",
            })
    return rows


def generate_nam_eca_500_portfolio() -> List[Dict[str, Any]]:
    rng = random.Random(202725)
    verified_sources = load_verified_source_ids()
    atlas = load_accessible_atlas()
    dim_labels = {dim: {c: l for c, l in vals} for dim, vals in DIMENSIONS.items()}

    seen = set()
    nam_list: List[Dict[str, Any]] = []
    eca_list: List[Dict[str, Any]] = []
    while len(nam_list) < 250 or len(eca_list) < 250:
        p = generate_program(rng, verified_sources, dim_labels)
        arch = p["dimensions"]["D01_jurisdiction_archetype"]
        if arch not in ("NAM", "ECA"):
            continue
        if arch == "NAM" and len(nam_list) >= 250:
            continue
        if arch == "ECA" and len(eca_list) >= 250:
            continue
        if p["tuple_sha256"] in seen:
            continue
        seen.add(p["tuple_sha256"])
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)
        if arch == "NAM":
            nam_list.append(p)
        else:
            eca_list.append(p)

    valid, errors = validate_programs(nam_list + eca_list)
    assert len(errors) == 0, f"Validation failed on NAM/ECA 500: {errors}"
    return valid


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_nam_eca_matrix()
    (CURATED_DIR / "nam_eca_comparative_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (CURATED_DIR / "nam_eca_comparative_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
        writer.writeheader()
        writer.writerows(matrix)

    progs_500 = generate_nam_eca_500_portfolio()
    df_500 = pd.DataFrame([flatten_program(p) for p in progs_500])
    df_500.to_csv(CURATED_DIR / "nam_eca_programs_500.csv", index=False, encoding="utf-8")
    df_500.to_parquet(CURATED_DIR / "nam_eca_programs_500.parquet", index=False)

    md = [
        "# Phase 2 — North America (NAM) & Eastern Europe/Central Asia (ECA) Deep-Dive",
        "",
        f"**Covered Verified Jurisdictions (`EXISTING_REAL_WORLD_RECORD`):** {len(matrix)} (2 NAM + 5 ECA)  ",
        f"**Generated NAM + ECA Research Portfolio (`PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`):** {len(progs_500)} (250 NAM + 250 ECA, `seed=202725`)",
        "",
        "| Jurisdiction | Subregion | Source ID | Reported Cases |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in matrix:
        md.append(f"| {r['jurisdiction']} | {r['subregion']} | {r['source_id']} | {r['reported_cases'] or 'None documented in source'} |")
    (REPORTS_DIR / "NAM_ECA_DEEP_DIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built NAM/ECA matrix ({len(matrix)} rows) & validated {len(progs_500)} programs")


if __name__ == "__main__":
    main()
