"""Generate structured Algorithmic Impact Assessment (AIA) dossiers for Top-10 Pilot Prototypes."""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
PILOTS_JSON = ROOT / "data" / "curated" / "top10_pilot_prototypes.json"
OUT_JSON = ROOT / "data" / "curated" / "top10_pilot_aia_dossiers.json"
OUT_MD = ROOT / "reports" / "TOP10_PILOT_AIA_DOSSIERS.md"

RISK_SAFEGUARDS = {
    "TIER_1_LOW_RISK": [
        "Pre-deployment data-minimization check",
        "Immutable audit logging of automated steps",
        "Periodic annual review",
    ],
    "TIER_2_MODERATE_RISK": [
        "Mandatory Human-in-the-Loop (HITL) sign-off before judicial or administrative use",
        "Automated citation-grounding gate to prevent hallucinated authorities",
        "User-facing disclosure tagging (aligned with Thailand Civil Court B.E. 2568 & UNESCO Guidelines)",
    ],
    "TIER_3_HIGH_RISK": [
        "Mandatory Pre-Deployment Algorithmic Impact Assessment (AIA)",
        "Independent source-code and weight auditability (Spain SC 1119/2025 benchmark)",
        "Statutory corroboration mandate and right to adversarial contestability",
        "12-month sunset clause and re-certification",
    ],
}


def build_aia_dossier(pilot: Dict[str, Any]) -> Dict[str, Any]:
    tier = pilot["human_rights_risk_tier"]
    dims = pilot["dimensions"]
    safeguards = RISK_SAFEGUARDS.get(tier, RISK_SAFEGUARDS["TIER_2_MODERATE_RISK"])
    return {
        "program_id": pilot["program_id"],
        "title": pilot["title"],
        "epistemic_label": pilot["epistemic_label"],
        "aia_status": "PROPOSED_UNVALIDATED_AIA_TEMPLATE",
        "human_rights_risk_tier": tier,
        "region_archetype": dims["D01_jurisdiction_archetype"],
        "deployment_tier": dims["D10_deployment_tier"],
        "governance_mechanism": dims["D08_governance_mechanism"],
        "human_rights_focus": dims["D09_human_rights_focus"],
        "mandatory_safeguards": safeguards,
        "comparative_benchmarks": ["CNJ Res 615/2025 (Brazil)", "Acuerdo PCSJA24-12243 (Colombia)", "AM 25-11-28-SC (Philippines)"],
        "inspiration_source_ids": pilot["inspiration_source_ids"],
    }


def main() -> None:
    pilots = json.loads(PILOTS_JSON.read_text(encoding="utf-8"))
    dossiers: List[Dict[str, Any]] = [build_aia_dossier(p) for p in pilots]
    OUT_JSON.write_text(json.dumps(dossiers, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Top-10 Pilot Prototypes — Algorithmic Impact Assessment (AIA) Dossiers",
        "",
        "**Status:** `PROPOSED_UNVALIDATED_AIA_TEMPLATE` (Research governance template; not a legal determination)",
        "",
    ]
    for i, d in enumerate(dossiers, 1):
        md.extend([
            f"## {i}. `{d['program_id']}` — {d['title']}",
            f"- **Risk Tier:** `{d['human_rights_risk_tier']}` | **Region:** `{d['region_archetype']}` | **Deployment:** `{d['deployment_tier']}`",
            f"- **Inspiration Sources:** {', '.join(d['inspiration_source_ids'])}",
            "- **Mandatory Safeguards:**",
        ])
        for s in d["mandatory_safeguards"]:
            md.append(f"  - {s}")
        md.append("")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Generated {len(dossiers)} AIA dossiers -> {OUT_JSON.name}")


if __name__ == "__main__":
    main()
