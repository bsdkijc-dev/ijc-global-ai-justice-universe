"""Build 2027-2045 Horizon Roadmap matrix across 100,000 curated programs."""

import csv
from pathlib import Path
import pandas as pd
from src.ontology.taxonomy import DIMENSIONS

ROOT = Path(__file__).resolve().parent.parent.parent
PARQUET_100K = ROOT / "data" / "curated" / "programs_curated_100000.parquet"
OUT_CSV = ROOT / "data" / "curated" / "horizon_roadmap_2027_2045.csv"
OUT_MD = ROOT / "reports" / "LONG_HORIZON_ROADMAP_2027_2045.md"


def main() -> None:
    df = pd.read_parquet(PARQUET_100K)
    horizons = DIMENSIONS["D12_horizon_target"]
    counts = df["D12_horizon_target"].value_counts().to_dict()
    mean_q = df.groupby("D12_horizon_target")["quality_score"].mean().round(2).to_dict()

    rows = []
    for code, label in horizons:
        sub = df[df["D12_horizon_target"] == code]
        low_mod_pct = round(
            sub["human_rights_risk_tier"].isin(["TIER_1_LOW_RISK", "TIER_2_MODERATE_RISK"]).mean() * 100, 1
        )
        rows.append({
            "horizon_code": code,
            "horizon_label": label,
            "programs_100k_count": int(counts.get(code, 0)),
            "mean_quality_score": float(mean_q.get(code, 0.0)),
            "low_or_moderate_risk_pct": low_mod_pct,
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# Long-Horizon Research Roadmap (2027–2045)",
        "",
        f"**Evaluated Portfolio:** {len(df):,} validated 12D configurations (`PROPOSED_RESEARCH_PROGRAM`)",
        "",
        "| Horizon | Target Window & Focus | Programs (n=100k) | Mean Quality | Low/Moderate Risk % |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in rows:
        md.append(
            f"| {r['horizon_code']} | {r['horizon_label']} | {r['programs_100k_count']:,} | "
            f"{r['mean_quality_score']} | {r['low_or_moderate_risk_pct']}% |"
        )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built 2027-2045 Horizon Roadmap across {len(df):,} programs -> {OUT_CSV.name}")


if __name__ == "__main__":
    main()
