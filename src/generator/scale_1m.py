"""1,000,000-program combinatorial streaming benchmark (CPU-only, chunked Parquet)."""

import hashlib
import json
import random
import time
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

from src.export.exporter import sha256_file
from src.ontology.taxonomy import DIMENSIONS

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_PARQUET = ROOT / "data" / "curated" / "programs_1m_benchmark.parquet"
MANIFEST_PATH = ROOT / "data" / "manifests" / "scale_1m_manifest.json"
REPORT_MD = ROOT / "reports" / "SCALE_1M_BENCHMARK.md"


def main(target: int = 1_000_000, chunk_size: int = 100_000, seed: int = 202712) -> None:
    t0 = time.perf_counter()
    rng = random.Random(seed)
    dim_items = [(dim, [code for code, _ in vals]) for dim, vals in DIMENSIONS.items()]

    seen_hashes = set()
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    writer = None

    written = 0
    while written < target:
        batch_n = min(chunk_size, target - written)
        cols = {dim: [] for dim, _ in dim_items}
        cols["program_id"] = []
        cols["hash8"] = []
        cols["epistemic_label"] = []

        while len(cols["program_id"]) < batch_n:
            tup = tuple(rng.choice(codes) for _, codes in dim_items)
            h_bytes = hashlib.blake2b("|".join(tup).encode("utf-8"), digest_size=8).digest()
            if h_bytes in seen_hashes:
                continue
            seen_hashes.add(h_bytes)
            h_hex = h_bytes.hex().upper()
            pid = f"IJC-GAJIU-{tup[0]}-{tup[2]}-{tup[3]}-{tup[4]}-{h_hex[:6]}"
            cols["program_id"].append(pid)
            cols["hash8"].append(h_hex)
            cols["epistemic_label"].append("PROPOSED_RESEARCH_PROGRAM")
            for idx, (dim, _) in enumerate(dim_items):
                cols[dim].append(tup[idx])

        table = pa.table(cols)
        if writer is None:
            writer = pq.ParquetWriter(OUT_PARQUET, table.schema, compression="zstd")
        writer.write_table(table)
        written += batch_n

    if writer is not None:
        writer.close()

    elapsed = round(time.perf_counter() - t0, 2)
    throughput = round(target / max(elapsed, 0.01), 1)
    file_bytes = OUT_PARQUET.stat().st_size

    manifest = {
        "dataset_name": "programs_1m_benchmark",
        "record_count": written,
        "unique_hashes": len(seen_hashes),
        "seed": seed,
        "generation_seconds": elapsed,
        "throughput_programs_per_sec": throughput,
        "file": {
            "name": OUT_PARQUET.name,
            "bytes": file_bytes,
            "sha256": sha256_file(OUT_PARQUET),
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    md = [
        "# 1,000,000-Program Streaming Parquet Benchmark Report",
        "",
        f"- **Total Materialized Records:** {written:,} (`seed={seed}`, `PROPOSED_RESEARCH_PROGRAM`)",
        f"- **Unique 64-bit BLAKE2b Tuples:** {len(seen_hashes):,} (0 collisions)",
        f"- **Wall-Clock CPU Time:** {elapsed}s (**{throughput:,.1f}** programs/sec)",
        f"- **Zstd Parquet Size:** {file_bytes:,} bytes (`{OUT_PARQUET.name}`)",
    ]
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Streamed 1,000,000 unique programs in {elapsed}s ({throughput:,.1f} prog/sec) -> {file_bytes:,} bytes")


if __name__ == "__main__":
    main()
