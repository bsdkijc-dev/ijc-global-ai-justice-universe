"""Analyze 30-pillar coverage across the 10,000-program portfolio."""

import csv
from pathlib import Path
import pandas as pd
from src.ontology.taxonomy import PILLARS

ROOT = Path(__file__).resolve().parent.parent.parent
PARQUET_10K = ROOT / "data" / "curated" / "programs_curated_10000.parquet"
OUT_CSV = ROOT / "data" / "curated" / "pillar_coverage_30.csv"
OUT_MD = ROOT / "reports" / "PILLAR_COVERAGE_AND_GAP_MATRIX.md"


def main() -> None:
    df = pd.read_parquet(PARQUET_10K)
    counts = df["D11_research_pillar"].value_counts().to_dict()
    mean_q = df.groupby("D11_research_pillar")["quality_score"].mean().round(2).to_dict()
    high_risk_share = (
        df.assign(is_hr=df["human_rights_risk_tier"].isin(["TIER_3_HIGH_RISK", "TIER_4_PROHIBITED_OR_MORATORIUM_CANDIDATE"]))
        .groupby("D11_research_pillar")["is_hr"]
        .mean()
        .mul(100)
        .round(1)
        .to_dict()
    )

    rows = []
    for pid, title in PILLARS:
        rows.append({
            "pillar_id": pid,
            "pillar_title": title,
            "programs_10k_count": int(counts.get(pid, 0)),
            "mean_quality_score": float(mean_q.get(pid, 0.0)),
            "high_risk_or_prohibited_pct": float(high_risk_share.get(pid, 0.0)),
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# 30-Pillar Coverage & Research Gap Matrix (n=10,000 Programs)",
        "",
        "| Pillar | Title | Count (n=10,000) | Mean Quality | High-Risk / Moratorium % |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in rows:
        md.append(
            f"| {r['pillar_id']} | {r['pillar_title']} | {r['programs_10k_count']} | "
            f"{r['mean_quality_score']} | {r['high_risk_or_prohibited_pct']}% |"
        )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built 30-pillar coverage matrix -> {OUT_CSV.name}")


if __name__ == "__main__":
    main()
