"""Phase 2 (Task 022): Europe, UK & EU AI Act Comparative Deep-Dive + 500-Program EUR Portfolio."""

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

EUROPE_JURISDICTIONS = [
    ("Estonia", "EU Member"),
    ("Finland", "EU Member"),
    ("France", "EU Member"),
    ("Germany", "EU Member"),
    ("Italy", "EU Member"),
    ("Spain", "EU Member"),
    ("The Netherlands", "EU Member"),
    ("United Kingdom", "Council of Europe (Non-EU)"),
    ("Ukraine", "Council of Europe / EU Candidate"),
]


def build_europe_matrix() -> List[Dict[str, Any]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    by_name = {s["jurisdiction"]: s for s in reg["sources"]}
    rows: List[Dict[str, Any]] = []

    for jur, status in EUROPE_JURISDICTIONS:
        src = by_name[jur]
        rows.append({
            "jurisdiction": jur,
            "regional_framework": status,
            "source_id": src["source_id"],
            "source_url": src["url"],
            "key_ai_systems": src["identified_ai_systems"],
            "regulatory_instruments": src["regulatory_instruments"],
            "reported_cases": src["reported_cases"],
            "evidence_label": "EXISTING_REAL_WORLD_RECORD",
        })
    return rows


def generate_eur_500_portfolio() -> List[Dict[str, Any]]:
    rng = random.Random(202722)
    verified_sources = load_verified_source_ids()
    atlas = load_accessible_atlas()
    dim_labels = {dim: {c: l for c, l in vals} for dim, vals in DIMENSIONS.items()}

    seen = set()
    progs: List[Dict[str, Any]] = []
    while len(progs) < 500:
        p = generate_program(rng, verified_sources, dim_labels)
        if p["dimensions"]["D01_jurisdiction_archetype"] != "EUR":
            continue
        if p["tuple_sha256"] in seen:
            continue
        seen.add(p["tuple_sha256"])
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)
        progs.append(p)

    valid, errors = validate_programs(progs)
    assert len(errors) == 0, f"Validation failed on EUR 500: {errors}"
    return valid


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_europe_matrix()
    (CURATED_DIR / "europe_comparative_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (CURATED_DIR / "europe_comparative_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
        writer.writeheader()
        writer.writerows(matrix)

    eur_500 = generate_eur_500_portfolio()
    df_eur = pd.DataFrame([flatten_program(p) for p in eur_500])
    df_eur.to_csv(CURATED_DIR / "europe_eur_programs_500.csv", index=False, encoding="utf-8")
    df_eur.to_parquet(CURATED_DIR / "europe_eur_programs_500.parquet", index=False)

    md = [
        "# Phase 2 — Europe, UK & EU AI Act Comparative Deep-Dive",
        "",
        f"**Covered Verified Jurisdictions (`EXISTING_REAL_WORLD_RECORD`):** {len(matrix)} (7 EU Member States + UK + Ukraine)  ",
        f"**Generated EUR Research Portfolio (`PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`):** {len(eur_500)} validated configurations (`seed=202722`)",
        "",
        "| Jurisdiction | Framework | Source ID | Key Reported Cases |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in matrix:
        md.append(f"| {r['jurisdiction']} | {r['regional_framework']} | {r['source_id']} | {r['reported_cases'] or 'None documented in source'} |")
    (REPORTS_DIR / "EUROPE_EU_AI_ACT_DEEP_DIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built Europe/UK matrix ({len(matrix)} rows) & validated {len(eur_500)} EUR research programs")


if __name__ == "__main__":
    main()
