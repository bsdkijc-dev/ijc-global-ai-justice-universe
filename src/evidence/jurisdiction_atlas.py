"""Build and validate the 46-country Comparative Jurisdiction Atlas from source-registry.json."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List
import jsonschema

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
JUR_SCHEMA_PATH = ROOT / "schemas" / "jurisdiction.schema.json"
CURATED_DIR = ROOT / "data" / "curated"
REPORTS_DIR = ROOT / "reports"

JURISDICTION_META: Dict[str, Dict[str, str]] = {
    "Argentina": {"code": "ARG", "archetype": "LAT", "family": "CIV"},
    "Australia": {"code": "AUS", "archetype": "OCE", "family": "COM"},
    "Azerbaijan": {"code": "AZE", "archetype": "ECA", "family": "CIV"},
    "Brazil": {"code": "BRA", "archetype": "LAT", "family": "CIV"},
    "Canada": {"code": "CAN", "archetype": "NAM", "family": "MIX"},
    "Chile": {"code": "CHL", "archetype": "LAT", "family": "CIV"},
    "China": {"code": "CHN", "archetype": "EAS", "family": "SOC"},
    "Colombia": {"code": "COL", "archetype": "LAT", "family": "CIV"},
    "Egypt": {"code": "EGY", "archetype": "MEN", "family": "MIX"},
    "Estonia": {"code": "EST", "archetype": "EUR", "family": "CIV"},
    "Ethiopia": {"code": "ETH", "archetype": "SSA", "family": "MIX"},
    "Finland": {"code": "FIN", "archetype": "EUR", "family": "CIV"},
    "France": {"code": "FRA", "archetype": "EUR", "family": "CIV"},
    "Germany": {"code": "DEU", "archetype": "EUR", "family": "CIV"},
    "India": {"code": "IND", "archetype": "SAS", "family": "COM"},
    "Iran": {"code": "IRN", "archetype": "MEN", "family": "ISL"},
    "Italy": {"code": "ITA", "archetype": "EUR", "family": "CIV"},
    "Japan": {"code": "JPN", "archetype": "EAS", "family": "CIV"},
    "Kazakhstan": {"code": "KAZ", "archetype": "ECA", "family": "CIV"},
    "Kenya": {"code": "KEN", "archetype": "SSA", "family": "COM"},
    "Kuwait": {"code": "KWT", "archetype": "MEN", "family": "ISL"},
    "Malaysia": {"code": "MYS", "archetype": "SEA", "family": "MIX"},
    "Mexico": {"code": "MEX", "archetype": "LAT", "family": "CIV"},
    "New Zealand": {"code": "NZL", "archetype": "OCE", "family": "COM"},
    "Russia": {"code": "RUS", "archetype": "ECA", "family": "CIV"},
    "Rwanda": {"code": "RWA", "archetype": "SSA", "family": "MIX"},
    "Saudi Arabia": {"code": "SAU", "archetype": "MEN", "family": "ISL"},
    "Singapore": {"code": "SGP", "archetype": "SEA", "family": "COM"},
    "South Africa": {"code": "ZAF", "archetype": "SSA", "family": "MIX"},
    "South Korea": {"code": "KOR", "archetype": "EAS", "family": "CIV"},
    "Spain": {"code": "ESP", "archetype": "EUR", "family": "CIV"},
    "Taiwan": {"code": "TWN", "archetype": "EAS", "family": "CIV"},
    "Thailand": {"code": "THA", "archetype": "SEA", "family": "CIV"},
    "The Gambia": {"code": "GMB", "archetype": "SSA", "family": "MIX"},
    "The Netherlands": {"code": "NLD", "archetype": "EUR", "family": "CIV"},
    "The Philippines": {"code": "PHL", "archetype": "SEA", "family": "MIX"},
    "Tanzania": {"code": "TZA", "archetype": "SSA", "family": "COM"},
    "Türkiye": {"code": "TUR", "archetype": "ECA", "family": "CIV"},
    "Ukraine": {"code": "UKR", "archetype": "ECA", "family": "CIV"},
    "United Arab Emirates": {"code": "ARE", "archetype": "MEN", "family": "MIX"},
    "United Kingdom": {"code": "GBR", "archetype": "EUR", "family": "COM"},
    "United States": {"code": "USA", "archetype": "NAM", "family": "COM"},
    "Uzbekistan": {"code": "UZB", "archetype": "ECA", "family": "CIV"},
    "Zambia": {"code": "ZMB", "archetype": "SSA", "family": "COM"},
    "Zimbabwe": {"code": "ZWE", "archetype": "SSA", "family": "MIX"},
    "Israel": {"code": "ISR", "archetype": "MEN", "family": "MIX"},
}


def _contains_any(text: str, keywords: List[str]) -> bool:
    low = text.lower()
    return any(k in low for k in keywords)


def build_atlas() -> List[Dict[str, Any]]:
    registry = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    schema = json.loads(JUR_SCHEMA_PATH.read_text(encoding="utf-8"))

    records: List[Dict[str, Any]] = []
    for src in registry["sources"]:
        jur = src["jurisdiction"]
        if jur == "Global (Hub)":
            continue
        meta = JURISDICTION_META[jur]
        is_accessible = src["verification_status"] == "VERIFIED_ACCESSIBLE"

        combined_text = " ".join([
            src.get("identified_ai_systems", ""),
            src.get("ai_use_cases", ""),
            src.get("regulatory_instruments", ""),
            src.get("judicial_policies", ""),
            src.get("reported_cases", ""),
            src.get("human_rights_implications", ""),
            src.get("technology_domain", ""),
        ])

        rec: Dict[str, Any] = {
            "jurisdiction_code": meta["code"],
            "jurisdiction_name": jur,
            "region_archetype": meta["archetype"],
            "legal_system_family": meta["family"],
            "source_ids": [src["source_id"]],
            "verification_status": src["verification_status"],
            "evidence_label": src["evidence_label"],
            "has_hallucination_cases": (
                _contains_any(combined_text, ["hallucination", "nullified", "fabricated", "wasted costs", "citation"])
                if is_accessible else None
            ),
            "has_biometric_or_frt_pushback": (
                _contains_any(combined_text, ["banned", "halted", "suspended", "blocked", "reprimand", "fine", "hessen", "bridges", "williams", "glukhin", "corroborat"])
                if is_accessible else None
            ),
            "has_judicial_ai_policy": (
                bool(src.get("judicial_policies", "").strip())
                if is_accessible else None
            ),
            "has_national_ai_law_or_strategy": (
                _contains_any(src.get("regulatory_instruments", ""), ["ai act", "ai law", "law on ai", "ai strategy", "ai policy", "ai basic", "ai framework", "132/2025", "ork-1115", "230-viii"])
                if is_accessible else None
            ),
            "has_multilingual_court_asr": (
                _contains_any(combined_text, ["transcription", "speech-to-text", "asr", "suvas", "salme", "scriptix", "kiswahili", "taglish", "afaan oromo", "aleks"])
                if is_accessible else None
            ),
            "source_url": src["url"],
        }
        jsonschema.validate(instance=rec, schema=schema)
        records.append(rec)

    return records


def main() -> None:
    records = build_atlas()
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = CURATED_DIR / "jurisdiction_atlas_46.json"
    json_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = CURATED_DIR / "jurisdiction_atlas_46.csv"
    fieldnames = list(records[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = dict(r)
            row["source_ids"] = ";".join(r["source_ids"])
            for k in [
                "has_hallucination_cases",
                "has_biometric_or_frt_pushback",
                "has_judicial_ai_policy",
                "has_national_ai_law_or_strategy",
                "has_multilingual_court_asr",
            ]:
                if row[k] is None:
                    row[k] = ""
            writer.writerow(row)

    accessible = [r for r in records if r["verification_status"] == "VERIFIED_ACCESSIBLE"]
    counts = {
        "Hallucination / Citation Sanctions": sum(1 for r in accessible if r["has_hallucination_cases"]),
        "Biometric / FRT Pushback or Limits": sum(1 for r in accessible if r["has_biometric_or_frt_pushback"]),
        "Documented Judicial AI Policy": sum(1 for r in accessible if r["has_judicial_ai_policy"]),
        "National AI Law / Strategy": sum(1 for r in accessible if r["has_national_ai_law_or_strategy"]),
        "Multilingual Court ASR / Translation": sum(1 for r in accessible if r["has_multilingual_court_asr"]),
    }

    md_lines = [
        "# Comparative Jurisdiction Atlas (46 Countries)",
        "",
        f"**Verified Accessible Countries:** {len(accessible)} / {len(records)}  ",
        f"**Inaccessible (Zero-Imputation Preserved):** 1 (`Zambia` / `OXF-AIATLAS-44`)",
        "",
        "## Cross-Jurisdictional Indicator Summary (n=45 Accessible)",
        "| Comparative Indicator | Countries |",
        "| :--- | :--- |",
    ]
    for label, cnt in counts.items():
        md_lines.append(f"| {label} | {cnt} |")

    md_lines.extend([
        "",
        "## Jurisdiction Matrix",
        "| Code | Country | Archetype | Family | Status | Hallucinations | FRT Pushback | Judicial Policy | AI Law/Strategy | Multilingual ASR |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in records:
        def fmt(v):
            return "Yes" if v is True else ("No" if v is False else "N/A (Inaccessible)")
        md_lines.append(
            f"| {r['jurisdiction_code']} | {r['jurisdiction_name']} | {r['region_archetype']} | "
            f"{r['legal_system_family']} | {r['verification_status']} | "
            f"{fmt(r['has_hallucination_cases'])} | {fmt(r['has_biometric_or_frt_pushback'])} | "
            f"{fmt(r['has_judicial_ai_policy'])} | {fmt(r['has_national_ai_law_or_strategy'])} | "
            f"{fmt(r['has_multilingual_court_asr'])} |"
        )

    (REPORTS_DIR / "COMPARATIVE_JURISDICTION_ATLAS.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Built Comparative Jurisdiction Atlas: {len(records)} countries ({len(accessible)} verified accessible)")


if __name__ == "__main__":
    main()
