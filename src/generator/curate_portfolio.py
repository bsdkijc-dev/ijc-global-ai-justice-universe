"""Generate, validate, deduplicate, rank, and curate 1,000 programs + Top-10 Pilot Prototypes."""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from src.evidence.provenance import enrich_inspiration_sources, load_accessible_atlas
from src.export.exporter import flatten_program, sha256_file
from src.generator.program_generator import generate_batch
from src.originality.deduplicator import screen_originality
from src.validation.validator import validate_programs

ROOT = Path(__file__).resolve().parent.parent.parent
CURATED_DIR = ROOT / "data" / "curated"
MANIFEST_PATH = ROOT / "data" / "manifests" / "curated_1000_manifest.json"
REPORTS_DIR = ROOT / "reports"


def compute_pilot_priority(prog: Dict[str, Any]) -> float:
    dims = prog["dimensions"]
    base = prog["quality_score"] * 0.65 + (prog["originality_score"] * 100.0) * 0.20
    if dims["D10_deployment_tier"] in ("OFF", "CPU", "OPN", "MOB", "LOW"):
        base += 8.0
    if prog["human_rights_risk_tier"] in ("TIER_1_LOW_RISK", "TIER_2_MODERATE_RISK"):
        base += 5.0
    if dims["D12_horizon_target"] in ("H27", "H29"):
        base += 2.0
    return round(base, 2)


def select_top_10_diverse_pilots(programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked = sorted(programs, key=lambda p: (-p["pilot_priority_score"], p["program_id"]))
    selected: List[Dict[str, Any]] = []
    used_archetypes = set()

    # First pass: pick highest-priority feasible candidate per distinct region archetype
    for p in ranked:
        arch = p["dimensions"]["D01_jurisdiction_archetype"]
        if arch not in used_archetypes and p["human_rights_risk_tier"] != "TIER_4_PROHIBITED_OR_MORATORIUM_CANDIDATE":
            selected.append(p)
            used_archetypes.add(arch)
        if len(selected) == 10:
            break

    # Backfill if fewer than 10
    if len(selected) < 10:
        selected_ids = {p["program_id"] for p in selected}
        for p in ranked:
            if p["program_id"] not in selected_ids and p["human_rights_risk_tier"] != "TIER_4_PROHIBITED_OR_MORATORIUM_CANDIDATE":
                selected.append(p)
                if len(selected) == 10:
                    break
    return selected


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    atlas = load_accessible_atlas()
    programs = generate_batch(sample_size=1000, seed=202702)
    for p in programs:
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)

    valid, errors = validate_programs(programs)
    assert len(errors) == 0, f"Validation failed on {len(errors)} programs"

    screened, orig_stats = screen_originality(valid, threshold=0.85)
    for p in screened:
        p["pilot_priority_score"] = compute_pilot_priority(p)

    # Export 1,000 curated programs
    jsonl_path = CURATED_DIR / "programs_curated_1000.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for p in screened:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    rows = []
    for p in screened:
        r = flatten_program(p)
        r["pilot_priority_score"] = p["pilot_priority_score"]
        rows.append(r)

    df = pd.DataFrame(rows)
    csv_path = CURATED_DIR / "programs_curated_1000.csv"
    parquet_path = CURATED_DIR / "programs_curated_1000.parquet"
    sqlite_path = CURATED_DIR / "programs_curated_1000.sqlite"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_parquet(parquet_path, index=False)
    if sqlite_path.exists():
        sqlite_path.unlink()
    with sqlite3.connect(sqlite_path) as conn:
        df.to_sql("programs_curated", conn, if_exists="replace", index=False)

    # Select and export Top 10 Pilot Prototypes
    pilots = select_top_10_diverse_pilots(screened)
    pilots_json = CURATED_DIR / "top10_pilot_prototypes.json"
    pilots_csv = CURATED_DIR / "top10_pilot_prototypes.csv"
    pilots_json.write_text(json.dumps(pilots, indent=2, ensure_ascii=False), encoding="utf-8")
    pilot_rows = []
    for p in pilots:
        r = flatten_program(p)
        r["pilot_priority_score"] = p["pilot_priority_score"]
        pilot_rows.append(r)
    pd.DataFrame(pilot_rows).to_csv(pilots_csv, index=False, encoding="utf-8")

    # Manifest
    files = [jsonl_path, csv_path, parquet_path, sqlite_path, pilots_json, pilots_csv]
    manifest = {
        "dataset_name": "programs_curated_1000",
        "record_count": len(screened),
        "seed": 202702,
        "originality_stats": {
            "exact_hash_duplicates": orig_stats["exact_hash_duplicates"],
            "flagged_near_duplicate_pairs": orig_stats["flagged_near_duplicate_pairs"],
            "mean_originality_score": orig_stats["mean_originality_score"],
            "min_originality_score": orig_stats["min_originality_score"],
        },
        "files": {
            f.name: {"bytes": f.stat().st_size, "sha256": sha256_file(f)}
            for f in files
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Pilot selection report
    md = [
        "# Top-10 Pilot Prototype Selection Report (2027–2028)",
        "",
        f"**Curated Pool:** {len(screened)} validated, deduplicated programs (`seed=202702`)  ",
        f"**Exact Duplicates:** {orig_stats['exact_hash_duplicates']} | **Near-Duplicate Pairs (>=0.85):** {orig_stats['flagged_near_duplicate_pairs']}  ",
        f"**Mean Quality Score:** {round(df['quality_score'].mean(), 2)} / 100.0 | **Mean Originality:** {orig_stats['mean_originality_score']}",
        "",
        "## Selected Top-10 Pilot Prototypes (Regionally Diverse, Non-Prohibited)",
        "| Rank | Program ID | Region | Risk Tier | Priority | Quality | Sources | Title |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for idx, p in enumerate(pilots, 1):
        md.append(
            f"| {idx} | `{p['program_id']}` | {p['dimensions']['D01_jurisdiction_archetype']} | "
            f"{p['human_rights_risk_tier']} | {p['pilot_priority_score']} | {p['quality_score']} | "
            f"{', '.join(p['inspiration_source_ids'])} | {p['title']} |"
        )
    (REPORTS_DIR / "PILOT_PROTOTYPE_SELECTION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(
        f"Curated {len(screened)} programs | Exact dups: {orig_stats['exact_hash_duplicates']} | "
        f"Near-dups: {orig_stats['flagged_near_duplicate_pairs']} | Selected {len(pilots)} diverse pilots"
    )


if __name__ == "__main__":
    main()
