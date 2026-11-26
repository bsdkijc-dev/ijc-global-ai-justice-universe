"""Extract structured inventory of documented real-world justice AI systems from Oxford AI Justice Atlas."""

import csv
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
OUT_CSV = ROOT / "data" / "curated" / "ai_systems_inventory.csv"
OUT_JSON = ROOT / "data" / "curated" / "ai_systems_inventory.json"
OUT_MD = ROOT / "reports" / "AI_SYSTEMS_INVENTORY_REPORT.md"


def build_inventory() -> List[Dict[str, str]]:
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    items: List[Dict[str, str]] = []
    idx = 1
    for src in reg["sources"]:
        if src["verification_status"] != "VERIFIED_ACCESSIBLE" or src["jurisdiction"] == "Global (Hub)":
            continue
        raw = src.get("identified_ai_systems", "").strip()
        if not raw:
            continue
        for sys_name in [s.strip() for s in raw.split(";") if s.strip()]:
            items.append({
                "system_id": f"SYS-{idx:03d}",
                "system_name": sys_name,
                "jurisdiction": src["jurisdiction"],
                "source_id": src["source_id"],
                "source_url": src["url"],
                "evidence_label": "EXISTING_REAL_WORLD_RECORD",
            })
            idx += 1
    return items


def main() -> None:
    items = build_inventory()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(items[0].keys()))
        writer.writeheader()
        writer.writerows(items)

    by_jur: Dict[str, int] = {}
    for it in items:
        by_jur[it["jurisdiction"]] = by_jur.get(it["jurisdiction"], 0) + 1
    top_jurs = sorted(by_jur.items(), key=lambda x: (-x[1], x[0]))[:10]

    md = [
        "# Real-World Justice AI Systems Inventory",
        "",
        f"**Total Documented Systems (`EXISTING_REAL_WORLD_RECORD`):** {len(items)} across {len(by_jur)} verified accessible jurisdictions",
        "",
        "## Top 10 Jurisdictions by Documented System Count",
        "| Jurisdiction | Documented Systems |",
        "| :--- | :--- |",
    ]
    for jur, cnt in top_jurs:
        md.append(f"| {jur} | {cnt} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Extracted {len(items)} documented real-world AI systems across {len(by_jur)} jurisdictions")


if __name__ == "__main__":
    main()
