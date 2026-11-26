"""Multi-format dataset exporter (CSV, JSONL, Parquet, SQLite) and SHA-256 manifest builder."""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_DIR = ROOT / "data" / "sample"
MANIFEST_PATH = ROOT / "data" / "manifests" / "sample_100_manifest.json"
SAMPLE_JSONL = SAMPLE_DIR / "programs_sample_100.jsonl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten_program(p: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "program_id": p["program_id"],
        "title": p["title"],
        "epistemic_label": p["epistemic_label"],
        "verification_status": p["verification_status"],
        "maturity_state": p["maturity_state"],
        "human_rights_risk_tier": p["human_rights_risk_tier"],
        "quality_score": p["quality_score"],
        "originality_score": p["originality_score"],
        "inspiration_source_ids": ";".join(p["inspiration_source_ids"]),
        "rationale": p["rationale"],
        "potential_value": p["potential_value"],
        "implementation_pathway": p["implementation_pathway"],
        "tuple_sha256": p["tuple_sha256"],
    }
    row.update(p["dimensions"])
    return row


def main() -> None:
    programs = [
        json.loads(line)
        for line in SAMPLE_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rows: List[Dict[str, Any]] = [flatten_program(p) for p in programs]
    df = pd.DataFrame(rows)

    csv_path = SAMPLE_DIR / "programs_sample_100.csv"
    parquet_path = SAMPLE_DIR / "programs_sample_100.parquet"
    sqlite_path = SAMPLE_DIR / "programs_sample_100.sqlite"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_parquet(parquet_path, index=False)

    if sqlite_path.exists():
        sqlite_path.unlink()
    with sqlite3.connect(sqlite_path) as conn:
        df.to_sql("programs", conn, if_exists="replace", index=False)

    files = [SAMPLE_JSONL, csv_path, parquet_path, sqlite_path]
    manifest = {
        "dataset_name": "programs_sample_100",
        "record_count": len(programs),
        "seed": 2027,
        "files": {
            f.name: {"bytes": f.stat().st_size, "sha256": sha256_file(f)}
            for f in files
        },
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Exported {len(programs)} programs to CSV, JSONL, Parquet, SQLite + manifest")


if __name__ == "__main__":
    main()
