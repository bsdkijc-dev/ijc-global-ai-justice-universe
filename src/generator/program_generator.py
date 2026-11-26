"""Deterministic 12-dimensional program configuration generator."""

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List

from src.ontology.taxonomy import DIMENSIONS

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
OUT_JSONL = ROOT / "data" / "sample" / "programs_sample_100.jsonl"

ARCHETYPE_SOURCE_HINTS = {
    "EUR": ["OXF-AIATLAS-10", "OXF-AIATLAS-12", "OXF-AIATLAS-13", "OXF-AIATLAS-14", "OXF-AIATLAS-17", "OXF-AIATLAS-31", "OXF-AIATLAS-35", "OXF-AIATLAS-41"],
    "NAM": ["OXF-AIATLAS-05", "OXF-AIATLAS-42"],
    "LAT": ["OXF-AIATLAS-01", "OXF-AIATLAS-04", "OXF-AIATLAS-06", "OXF-AIATLAS-08", "OXF-AIATLAS-23"],
    "SEA": ["OXF-AIATLAS-22", "OXF-AIATLAS-28", "OXF-AIATLAS-33", "OXF-AIATLAS-36"],
    "EAS": ["OXF-AIATLAS-07", "OXF-AIATLAS-18", "OXF-AIATLAS-30", "OXF-AIATLAS-32"],
    "SAS": ["OXF-AIATLAS-15"],
    "MEN": ["OXF-AIATLAS-09", "OXF-AIATLAS-16", "OXF-AIATLAS-21", "OXF-AIATLAS-27", "OXF-AIATLAS-40", "OXF-AIATLAS-46"],
    "SSA": ["OXF-AIATLAS-11", "OXF-AIATLAS-20", "OXF-AIATLAS-26", "OXF-AIATLAS-29", "OXF-AIATLAS-34", "OXF-AIATLAS-37", "OXF-AIATLAS-45"],
    "ECA": ["OXF-AIATLAS-03", "OXF-AIATLAS-19", "OXF-AIATLAS-25", "OXF-AIATLAS-38", "OXF-AIATLAS-39", "OXF-AIATLAS-43"],
    "OCE": ["OXF-AIATLAS-02", "OXF-AIATLAS-24"],
    "SUP": ["OXF-AIATLAS-00", "OXF-AIATLAS-39"],
    "LOW": ["OXF-AIATLAS-11", "OXF-AIATLAS-34", "OXF-AIATLAS-37"],
}


def load_verified_source_ids() -> Dict[str, Dict[str, Any]]:
    data = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    return {
        s["source_id"]: s
        for s in data["sources"]
        if s["verification_status"] == "VERIFIED_ACCESSIBLE"
    }


def assign_risk_tier(dims: Dict[str, str]) -> str:
    wf = dims["D05_workflow_stage"]
    mod = dims["D07_data_modality"]
    gov = dims["D08_governance_mechanism"]
    if gov == "BAN":
        return "TIER_4_PROHIBITED_OR_MORATORIUM_CANDIDATE"
    if mod == "BIO" or wf in ("BAI", "SEN", "INV", "ADM"):
        return "TIER_3_HIGH_RISK"
    if wf in ("RES", "DRF", "ASR", "INT", "APP"):
        return "TIER_2_MODERATE_RISK"
    return "TIER_1_LOW_RISK"


def compute_quality_score(dims: Dict[str, str], risk_tier: str) -> float:
    score = 72.0
    if dims["D08_governance_mechanism"] in ("HIT", "AIA", "CIT", "UNE", "SRC", "CON"):
        score += 10.0
    if dims["D10_deployment_tier"] in ("OFF", "CPU", "ONP", "OPN"):
        score += 8.0
    if risk_tier in ("TIER_1_LOW_RISK", "TIER_2_MODERATE_RISK"):
        score += 5.0
    elif dims["D08_governance_mechanism"] in ("HIT", "SRC", "COR", "BAN"):
        score += 4.0
    return round(min(score, 98.0), 2)


def generate_program(
    rng: random.Random,
    verified_sources: Dict[str, Dict[str, Any]],
    dim_labels: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    dims: Dict[str, str] = {}
    for dim_name, options in DIMENSIONS.items():
        code, _ = rng.choice(options)
        dims[dim_name] = code

    canonical_json = json.dumps(dims, sort_keys=True)
    tuple_sha256 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    hash6 = tuple_sha256[:6].upper()

    jur = dims["D01_jurisdiction_archetype"]
    dom = dims["D03_justice_domain"]
    inst = dims["D04_institutional_actor"]
    wf = dims["D05_workflow_stage"]
    program_id = f"IJC-GAJIU-{jur}-{dom}-{inst}-{wf}-{hash6}"

    jur_label = dim_labels["D01_jurisdiction_archetype"][jur]
    leg_label = dim_labels["D02_legal_system"][dims["D02_legal_system"]]
    dom_label = dim_labels["D03_justice_domain"][dom]
    inst_label = dim_labels["D04_institutional_actor"][inst]
    wf_label = dim_labels["D05_workflow_stage"][wf]
    ai_label = dim_labels["D06_ai_paradigm"][dims["D06_ai_paradigm"]]
    mod_label = dim_labels["D07_data_modality"][dims["D07_data_modality"]]
    gov_label = dim_labels["D08_governance_mechanism"][dims["D08_governance_mechanism"]]
    hr_label = dim_labels["D09_human_rights_focus"][dims["D09_human_rights_focus"]]
    dep_label = dim_labels["D10_deployment_tier"][dims["D10_deployment_tier"]]
    pil_label = dim_labels["D11_research_pillar"][dims["D11_research_pillar"]]
    hor_label = dim_labels["D12_horizon_target"][dims["D12_horizon_target"]]

    title = f"{ai_label} for {wf_label} in {dom_label} ({jur} / {inst})"
    rationale = (
        f"Proposed research configuration addressing {pil_label} for {inst_label} in {jur_label} "
        f"({leg_label}), combining {ai_label} over {mod_label} with {gov_label} to safeguard {hr_label}."
    )
    potential_value = (
        f"Supports comparative empirical evaluation of {wf_label} within {dom_label} "
        f"under zero-incremental-cost constraints ({dep_label})."
    )
    implementation_pathway = (
        f"Stage 1: Baseline legal-institutional mapping in {jur_label}; "
        f"Stage 2: Open-source prototype on {dep_label} with {gov_label}; "
        f"Stage 3: Independent rights audit targeting {hor_label}."
    )

    candidate_sources = [s for s in ARCHETYPE_SOURCE_HINTS.get(jur, ["OXF-AIATLAS-00"]) if s in verified_sources]
    if not candidate_sources:
        candidate_sources = ["OXF-AIATLAS-00"]

    risk_tier = assign_risk_tier(dims)
    quality_score = compute_quality_score(dims, risk_tier)

    return {
        "program_id": program_id,
        "title": title,
        "epistemic_label": "PROPOSED_RESEARCH_PROGRAM",
        "verification_status": "PROPOSED_UNVALIDATED",
        "maturity_state": "CONCEPTUAL_SPEC",
        "dimensions": dims,
        "rationale": rationale,
        "potential_value": potential_value,
        "implementation_pathway": implementation_pathway,
        "human_rights_risk_tier": risk_tier,
        "quality_score": quality_score,
        "originality_score": 1.0,
        "inspiration_source_ids": candidate_sources[:2],
        "tuple_sha256": tuple_sha256,
    }


def generate_batch(sample_size: int = 100, seed: int = 2027) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    verified_sources = load_verified_source_ids()
    dim_labels = {
        dim: {code: label for code, label in vals}
        for dim, vals in DIMENSIONS.items()
    }
    seen_hashes = set()
    programs: List[Dict[str, Any]] = []
    while len(programs) < sample_size:
        prog = generate_program(rng, verified_sources, dim_labels)
        if prog["tuple_sha256"] not in seen_hashes:
            seen_hashes.add(prog["tuple_sha256"])
            programs.append(prog)
    return programs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic 12D program sample")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2027)
    args = parser.parse_args()

    programs = generate_batch(sample_size=args.sample_size, seed=args.seed)
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for p in programs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"Generated {len(programs)} unique candidate programs -> {OUT_JSONL}")


if __name__ == "__main__":
    main()
