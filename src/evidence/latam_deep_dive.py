"""Phase 2 (Task 023): Latin America Constitutional & Judicial AI Deep-Dive + 500-Program LAT Portfolio."""

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

LATAM_JURISDICTIONS = ["Argentina", "Brazil", "Chile", "Colombia", "Mexico"]


def build_latam_matrix() -> List[Dict[str, Any]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    by_name = {s["jurisdiction"]: s for s in reg["sources"]}
    rows: List[Dict[str, Any]] = []

    for jur in LATAM_JURISDICTIONS:
        src = by_name[jur]
        rows.append({
            "jurisdiction": jur,
            "source_id": src["source_id"],
            "source_url": src["url"],
            "key_ai_systems": src["identified_ai_systems"],
            "regulatory_instruments": src["regulatory_instruments"],
            "judicial_policies": src["judicial_policies"],
            "reported_cases": src["reported_cases"],
            "evidence_label": "EXISTING_REAL_WORLD_RECORD",
        })
    return rows


def generate_lat_500_portfolio() -> List[Dict[str, Any]]:
    rng = random.Random(202723)
    verified_sources = load_verified_source_ids()
    atlas = load_accessible_atlas()
    dim_labels = {dim: {c: l for c, l in vals} for dim, vals in DIMENSIONS.items()}

    seen = set()
    progs: List[Dict[str, Any]] = []
    while len(progs) < 500:
        p = generate_program(rng, verified_sources, dim_labels)
        if p["dimensions"]["D01_jurisdiction_archetype"] != "LAT":
            continue
        if p["tuple_sha256"] in seen:
            continue
        seen.add(p["tuple_sha256"])
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)
        progs.append(p)

    valid, errors = validate_programs(progs)
    assert len(errors) == 0, f"Validation failed on LAT 500: {errors}"
    return valid


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_latam_matrix()
    (CURATED_DIR / "latam_comparative_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (CURATED_DIR / "latam_comparative_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
        writer.writeheader()
        writer.writerows(matrix)

    lat_500 = generate_lat_500_portfolio()
    df_lat = pd.DataFrame([flatten_program(p) for p in lat_500])
    df_lat.to_csv(CURATED_DIR / "latam_lat_programs_500.csv", index=False, encoding="utf-8")
    df_lat.to_parquet(CURATED_DIR / "latam_lat_programs_500.parquet", index=False)

    md = [
        "# Phase 2 — Latin America Constitutional & Judicial AI Deep-Dive",
        "",
        f"**Covered Verified Jurisdictions (`EXISTING_REAL_WORLD_RECORD`):** {len(matrix)} (Argentina, Brazil, Chile, Colombia, Mexico)  ",
        f"**Generated LAT Research Portfolio (`PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`):** {len(lat_500)} validated configurations (`seed=202723`)",
        "",
        "| Jurisdiction | Source ID | Regulatory & Judicial Policies | Reported Cases |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in matrix:
        pol = f"{r['regulatory_instruments']} | {r['judicial_policies']}".strip(" |")
        md.append(f"| {r['jurisdiction']} | {r['source_id']} | {pol} | {r['reported_cases'] or 'None documented in source'} |")
    (REPORTS_DIR / "LATAM_CONSTITUTIONAL_AI_DEEP_DIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built LATAM matrix ({len(matrix)} rows) & validated {len(lat_500)} LAT research programs")


if __name__ == "__main__":
    main()
