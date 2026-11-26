"""Compute transparent 46-country Judicial AI Governance Readiness Index from jurisdiction_atlas_46.json."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS_JSON = ROOT / "data" / "curated" / "jurisdiction_atlas_46.json"
OUT_CSV = ROOT / "data" / "curated" / "governance_readiness_46.csv"
OUT_MD = ROOT / "reports" / "GOVERNANCE_READINESS_INDEX.md"


def score_jurisdiction(rec: Dict[str, Any]) -> Dict[str, Any]:
    if rec["verification_status"] != "VERIFIED_ACCESSIBLE":
        return {
            "jurisdiction_code": rec["jurisdiction_code"],
            "jurisdiction_name": rec["jurisdiction_name"],
            "region_archetype": rec["region_archetype"],
            "verification_status": rec["verification_status"],
            "readiness_score": None,
            "tier": "INACCESSIBLE_NO_IMPUTATION",
        }

    score = 0
    if rec["has_judicial_ai_policy"]:
        score += 30
    if rec["has_national_ai_law_or_strategy"]:
        score += 25
    if rec["has_biometric_or_frt_pushback"]:
        score += 15
    if rec["has_multilingual_court_asr"]:
        score += 15
    if rec["has_hallucination_cases"]:
        score += 15

    if score >= 70:
        tier = "HIGH_GOVERNANCE_ACTIVITY"
    elif score >= 40:
        tier = "MODERATE_GOVERNANCE_ACTIVITY"
    else:
        tier = "EMERGING_GOVERNANCE_ACTIVITY"

    return {
        "jurisdiction_code": rec["jurisdiction_code"],
        "jurisdiction_name": rec["jurisdiction_name"],
        "region_archetype": rec["region_archetype"],
        "verification_status": rec["verification_status"],
        "readiness_score": score,
        "tier": tier,
    }


def main() -> None:
    atlas = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    scored: List[Dict[str, Any]] = [score_jurisdiction(r) for r in atlas]
    scored.sort(key=lambda r: (-(r["readiness_score"] if r["readiness_score"] is not None else -1), r["jurisdiction_name"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
        writer.writeheader()
        for r in scored:
            row = dict(r)
            if row["readiness_score"] is None:
                row["readiness_score"] = ""
            writer.writerow(row)

    accessible = [r for r in scored if r["readiness_score"] is not None]
    mean_score = round(sum(r["readiness_score"] for r in accessible) / len(accessible), 2)

    md = [
        "# Judicial AI Governance Readiness Index (46 Countries)",
        "",
        f"**Accessible Countries Scored:** {len(accessible)} / 46 (Zambia `OXF-AIATLAS-44` retained as `INACCESSIBLE_NO_IMPUTATION`)  ",
        f"**Mean Governance Activity Score:** {mean_score} / 100.0",
        "",
        "Scoring rubric (strictly from `jurisdiction_atlas_46.json` indicators): Judicial AI Policy (`+30`), National AI Law/Strategy (`+25`), Biometric/FRT Oversight (`+15`), Multilingual Court ASR (`+15`), Hallucination Enforcement Signal (`+15`).",
        "",
        "## Top 15 Jurisdictions by Observed Governance Activity",
        "| Rank | Code | Country | Region | Score | Tier |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for i, r in enumerate(accessible[:15], 1):
        md.append(f"| {i} | {r['jurisdiction_code']} | {r['jurisdiction_name']} | {r['region_archetype']} | {r['readiness_score']} | {r['tier']} |")

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Computed Governance Readiness Index: {len(accessible)} scored (mean={mean_score})")


if __name__ == "__main__":
    main()
