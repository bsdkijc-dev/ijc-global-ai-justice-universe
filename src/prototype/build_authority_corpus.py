"""Build verified cross-jurisdictional authority corpus from accessible Oxford AI Justice Atlas records."""

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
CORPUS_OUT = ROOT / "data" / "curated" / "verified_authority_corpus.json"


def build_corpus() -> List[Dict[str, str]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    entries: List[Dict[str, str]] = []
    seen = set()

    idx = 1
    for src in reg["sources"]:
        if src["verification_status"] != "VERIFIED_ACCESSIBLE":
            continue
        jur = src["jurisdiction"]
        sid = src["source_id"]
        url = src["url"]

        for field, auth_type in [
            ("reported_cases", "REPORTED_CASE"),
            ("regulatory_instruments", "REGULATORY_INSTRUMENT"),
            ("judicial_policies", "JUDICIAL_POLICY"),
        ]:
            raw = src.get(field, "").strip()
            if not raw:
                continue
            for item in [x.strip() for x in raw.split(";") if x.strip()]:
                key = (jur.lower(), item.lower())
                if key in seen:
                    continue
                seen.add(key)
                entries.append({
                    "auth_id": f"AUTH-{idx:03d}",
                    "citation": item,
                    "authority_type": auth_type,
                    "jurisdiction": jur,
                    "source_id": sid,
                    "source_url": url,
                    "evidence_label": "EXISTING_REAL_WORLD_RECORD",
                })
                idx += 1

    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    CORPUS_OUT.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Built verified authority corpus: {len(entries)} entries from {SOURCES_JSON.name}")
    return entries


if __name__ == "__main__":
    build_corpus()
