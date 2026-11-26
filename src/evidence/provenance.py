"""Evidence provenance linker connecting proposed programs to verified Oxford AI Atlas records."""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS_JSON = ROOT / "data" / "curated" / "jurisdiction_atlas_46.json"


def load_accessible_atlas() -> List[Dict[str, Any]]:
    data = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    return [r for r in data if r["verification_status"] == "VERIFIED_ACCESSIBLE"]


def enrich_inspiration_sources(program: Dict[str, Any], atlas: List[Dict[str, Any]]) -> List[str]:
    """Select up to 3 verified Oxford source IDs matching archetype, legal family, or theme."""
    dims = program["dimensions"]
    jur = dims["D01_jurisdiction_archetype"]
    fam = dims["D02_legal_system"]
    wf = dims["D05_workflow_stage"]
    mod = dims["D07_data_modality"]

    scored: List[tuple] = []
    for rec in atlas:
        score = 0
        if rec["region_archetype"] == jur:
            score += 4
        if rec["legal_system_family"] == fam:
            score += 2
        if wf in ("RES", "DRF") and rec["has_hallucination_cases"]:
            score += 2
        if mod == "BIO" and rec["has_biometric_or_frt_pushback"]:
            score += 2
        if wf == "ASR" and rec["has_multilingual_court_asr"]:
            score += 2
        if score > 0:
            scored.append((score, rec["source_ids"][0]))

    scored.sort(key=lambda x: (-x[0], x[1]))
    selected = []
    for _, sid in scored:
        if sid not in selected:
            selected.append(sid)
        if len(selected) == 3:
            break

    return selected if selected else ["OXF-AIATLAS-00"]
