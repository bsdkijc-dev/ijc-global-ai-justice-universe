"""Scale deterministic 12D program generation and validation to 10,000 unique records."""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from src.evidence.provenance import enrich_inspiration_sources, load_accessible_atlas
from src.export.exporter import flatten_program, sha256_file
from src.generator.curate_portfolio import compute_pilot_priority
from src.generator.program_generator import generate_batch
from src.validation.validator import validate_programs

ROOT = Path(__file__).resolve().parent.parent.parent
CURATED_DIR = ROOT / "data" / "curated"
MANIFEST_PATH = ROOT / "data" / "manifests" / "curated_10000_manifest.json"
REPORT_MD = ROOT / "reports" / "TEN_THOUSAND_PROGRAM_ANALYTICS.md"


def main() -> None:
    t0 = time.perf_counter()
    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    atlas = load_accessible_atlas()
    programs = generate_batch(sample_size=10_000, seed=202706)
    for p in programs:
        p["inspiration_source_ids"] = enrich_inspiration_sources(p, atlas)

    valid, errors = validate_programs(programs)
    assert len(errors) == 0, f"Schema validation errors: {len(errors)}"

    hashes = {p["tuple_sha256"] for p in valid}
    assert len(hashes) == 10_000, "Exact hash collision detected"

    for p in valid:
        p["pilot_priority_score"] = compute_pilot_priority(p)

    rows: List[Dict[str, Any]] = []
    for p in valid:
        r = flatten_program(p)
        r["pilot_priority_score"] = p["pilot_priority_score"]
        rows.append(r)

    df = pd.DataFrame(rows)
    parquet_path = CURATED_DIR / "programs_curated_10000.parquet"
    sqlite_path = CURATED_DIR / "programs_curated_10000.sqlite"

    df.to_parquet(parquet_path, index=False)
    if sqlite_path.exists():
        sqlite_path.unlink()
    with sqlite3.connect(sqlite_path) as conn:
        df.to_sql("programs_curated_10k", conn, if_exists="replace", index=False)

    elapsed = round(time.perf_counter() - t0, 2)
    manifest = {
        "dataset_name": "programs_curated_10000",
        "record_count": len(df),
        "seed": 202706,
        "exact_hash_duplicates": 0,
        "schema_errors": 0,
        "generation_seconds": elapsed,
        "files": {
            f.name: {"bytes": f.stat().st_size, "sha256": sha256_file(f)}
            for f in [parquet_path, sqlite_path]
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    tier_counts = df["human_rights_risk_tier"].value_counts().to_dict()
    reg_counts = df["D01_jurisdiction_archetype"].value_counts().to_dict()
    md = [
        "# 10,000-Program Scale-Up Analytics Report",
        "",
        f"- **Total Validated Programs:** {len(df):,} (`seed=202706`, `PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`)",
        f"- **Exact SHA-256 Duplicates:** 0",
        f"- **Schema Validation Errors:** 0",
        f"- **End-to-End CPU Generation + Validation Time:** {elapsed}s",
        f"- **Mean Quality Score:** {round(df['quality_score'].mean(), 2)} / 100.0",
        "",
        "## Human-Rights Risk Tier Distribution (n=10,000)",
        "| Risk Tier | Count | Share |",
        "| :--- | :--- | :--- |",
    ]
    for tier, cnt in sorted(tier_counts.items()):
        md.append(f"| {tier} | {cnt:,} | {cnt / len(df) * 100:.1f}% |")

    md.extend([
        "",
        "## Regional Archetype Coverage (n=10,000)",
        "| Archetype | Count |",
        "| :--- | :--- |",
    ])
    for arch, cnt in sorted(reg_counts.items()):
        md.append(f"| {arch} | {cnt:,} |")

    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Generated, validated & exported 10,000 programs in {elapsed}s (0 errors, 0 duplicates)")


if __name__ == "__main__":
    main()
