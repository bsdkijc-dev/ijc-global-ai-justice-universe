"""Phase 2 (Task 024): Sub-Saharan Africa & MENA Comparative Deep-Dive + 500-Program Portfolio."""

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

SSA_JURISDICTIONS = ["Ethiopia", "Kenya", "Rwanda", "South Africa", "Tanzania", "The Gambia", "Zambia", "Zimbabwe"]
MENA_JURISDICTIONS = ["Egypt", "Iran", "Israel", "Kuwait", "Saudi Arabia", "United Arab Emirates"]


def build_ssa_mena_matrix() -> List[Dict[str, Any]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    by_name = {s["jurisdiction"]: s for s in reg["sources"]}
    rows: List[Dict[str, Any]] = []

    for subreg, jurs in [("SSA", SSA_JURISDICTIONS), ("MENA", MENA_JURISDICTIONS)]:
        for jur in jurs:
            src = by_name[jur]
            rows.append({
                "jurisdiction": jur,
                "subregion": subreg,
                "verification_status": src["verification_status"],
                "source_id": src["source_id"],
                "source_url": src["url"],
                "key_ai_systems": src.get("identified_ai_systems", ""),
                "regulatory_instruments": src.get("regulatory_instruments", ""),
                "evidence_label": src["evidence_label"],
            })
    return rows


def generate_ssa_mena_500_portfolio() -> List[Dict[str, Any]]:
    rng = random.Random(202724)
    verified_sources = load_verified_source_ids()
    atlas = load_accessible_atlas()
    dim_labels = {dim: {c: l for c, l in vals} for dim, vals in DIMENSIONS.items()}

    seen = set()
    ssa_list: List[Dict[str, Any]] = []
    men_list: List[Dict[str, Any]] = []
    while len(ssa_list) < 250 or len(men_list) < 250:
        p = generate_program(rng, verified_sources, dim_labels)
        arch = p["dimensions"]["D01_jurisdiction_archetype"]
        if arch not in ("SSA", "MEN"):
            continue
        if arch == "SSA" and len(ssa_list) >= 250:
            continue
        if arch == "MEN" and len(men_list) >= 250:
            continue
        if p["tuple_sha256"] in seen:
            continue
        seen.add(p["tuple_sha256"])
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)
        if arch == "SSA":
            ssa_list.append(p)
        else:
            men_list.append(p)

    combined = ssa_list + men_list
    valid, errors = validate_programs(combined)
    assert len(errors) == 0, f"Validation failed on SSA/MENA 500: {errors}"
    return valid


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_ssa_mena_matrix()
    (CURATED_DIR / "ssa_mena_comparative_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (CURATED_DIR / "ssa_mena_comparative_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
        writer.writeheader()
        writer.writerows(matrix)

    progs_500 = generate_ssa_mena_500_portfolio()
    df_500 = pd.DataFrame([flatten_program(p) for p in progs_500])
    df_500.to_csv(CURATED_DIR / "ssa_mena_programs_500.csv", index=False, encoding="utf-8")
    df_500.to_parquet(CURATED_DIR / "ssa_mena_programs_500.parquet", index=False)

    accessible = sum(1 for r in matrix if r["verification_status"] == "VERIFIED_ACCESSIBLE")
    md = [
        "# Phase 2 — Sub-Saharan Africa (SSA) & MENA Comparative Deep-Dive",
        "",
        f"**Supplied Oxford Jurisdictions:** {len(matrix)} ({accessible} `VERIFIED_ACCESSIBLE`, 1 `SOURCE_INACCESSIBLE`: Zambia `OXF-AIATLAS-44`)  ",
        f"**Generated SSA + MENA Research Portfolio (`PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`):** {len(progs_500)} (250 SSA + 250 MEN, `seed=202724`)",
        "",
        "| Jurisdiction | Subregion | Status | Source ID |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in matrix:
        md.append(f"| {r['jurisdiction']} | {r['subregion']} | {r['verification_status']} | {r['source_id']} |")
    (REPORTS_DIR / "SSA_MENA_DEEP_DIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built SSA/MENA matrix ({len(matrix)} rows, {accessible} accessible) & validated {len(progs_500)} programs")


if __name__ == "__main__":
    main()
