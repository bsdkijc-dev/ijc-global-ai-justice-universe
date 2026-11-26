"""Unified offline CLI to query real-world systems, authorities, readiness scores, and glossary terms."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEMS_JSON = ROOT / "data" / "curated" / "ai_systems_inventory.json"
CORPUS_JSON = ROOT / "data" / "curated" / "verified_authority_corpus.json"
READINESS_CSV = ROOT / "data" / "curated" / "governance_readiness_46.csv"
GLOSSARY_JSON = ROOT / "data" / "curated" / "multilingual_glossary_50.json"


def search_all(query: str) -> Dict[str, Any]:
    q = query.strip().lower()
    systems: List[Dict[str, str]] = [
        s for s in json.loads(SYSTEMS_JSON.read_text(encoding="utf-8"))
        if q in s["system_name"].lower() or q in s["jurisdiction"].lower()
    ]
    authorities: List[Dict[str, str]] = [
        a for a in json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
        if q in a["citation"].lower() or q in a["jurisdiction"].lower()
    ]
    readiness: List[Dict[str, str]] = []
    with READINESS_CSV.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if q in row["jurisdiction_name"].lower() or q in row["jurisdiction_code"].lower():
                readiness.append(row)
    glossary: List[Dict[str, str]] = [
        g for g in json.loads(GLOSSARY_JSON.read_text(encoding="utf-8"))
        if any(q in str(v).lower() for v in g.values())
    ]
    return {
        "query": query,
        "counts": {
            "systems": len(systems),
            "authorities": len(authorities),
            "readiness": len(readiness),
            "glossary": len(glossary),
        },
        "systems": systems[:10],
        "authorities": authorities[:10],
        "readiness": readiness[:5],
        "glossary": glossary[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified offline query CLI for IJC-GAJIU")
    parser.add_argument("--query", required=True, help="Search keyword (country, system, case, or term)")
    args = parser.parse_args()
    print(json.dumps(search_all(args.query), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
