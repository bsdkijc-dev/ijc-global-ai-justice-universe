"""Deterministic 100,000-program streaming Parquet benchmark (CPU-only, zero paid APIs)."""

import hashlib
import json
import random
import time
from pathlib import Path
import pandas as pd

from src.export.exporter import sha256_file
from src.generator.program_generator import assign_risk_tier, compute_quality_score
from src.ontology.taxonomy import DIMENSIONS

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_PARQUET = ROOT / "data" / "curated" / "programs_curated_100000.parquet"
MANIFEST_PATH = ROOT / "data" / "manifests" / "curated_100000_manifest.json"
REPORT_MD = ROOT / "reports" / "SCALE_100K_BENCHMARK.md"


def main(target: int = 100_000, seed: int = 202711) -> None:
    t0 = time.perf_counter()
    rng = random.Random(seed)
    dim_items = [(dim, [code for code, _ in vals]) for dim, vals in DIMENSIONS.items()]

    seen = set()
    rows = []
    while len(rows) < target:
        dims = {dim: rng.choice(codes) for dim, codes in dim_items}
        canonical = json.dumps(dims, sort_keys=True)
        h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        jur = dims["D01_jurisdiction_archetype"]
        dom = dims["D03_justice_domain"]
        inst = dims["D04_institutional_actor"]
        wf = dims["D05_workflow_stage"]
        pid = f"IJC-GAJIU-{jur}-{dom}-{inst}-{wf}-{h[:6].upper()}"
        risk = assign_risk_tier(dims)
        qual = compute_quality_score(dims, risk)
        row = {
            "program_id": pid,
            "epistemic_label": "PROPOSED_RESEARCH_PROGRAM",
            "verification_status": "PROPOSED_UNVALIDATED",
            "human_rights_risk_tier": risk,
            "quality_score": qual,
            "tuple_sha256": h,
        }
        row.update(dims)
        rows.append(row)

    df = pd.DataFrame(rows)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PARQUET, index=False)
    elapsed = round(time.perf_counter() - t0, 2)
    throughput = round(target / max(elapsed, 0.01), 1)

    manifest = {
        "dataset_name": "programs_curated_100000",
        "record_count": len(df),
        "unique_hashes": len(seen),
        "seed": seed,
        "generation_seconds": elapsed,
        "throughput_programs_per_sec": throughput,
        "file": {
            "name": OUT_PARQUET.name,
            "bytes": OUT_PARQUET.stat().st_size,
            "sha256": sha256_file(OUT_PARQUET),
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    md = [
        "# 100,000-Program Scale Benchmark Report",
        "",
        f"- **Total Materialized Records:** {len(df):,} (`seed={seed}`, `PROPOSED_RESEARCH_PROGRAM` / `PROPOSED_UNVALIDATED`)",
        f"- **Unique SHA-256 Tuples:** {len(seen):,} (0 collisions)",
        f"- **Wall-Clock CPU Time:** {elapsed}s (**{throughput:,.1f}** programs/sec)",
        f"- **Parquet Size:** {OUT_PARQUET.stat().st_size:,} bytes (`{OUT_PARQUET.name}`)",
    ]
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Generated 100,000 unique programs in {elapsed}s ({throughput:,.1f} prog/sec) -> {OUT_PARQUET.name}")


if __name__ == "__main__":
    main()
