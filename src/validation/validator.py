"""Structural, schema, epistemic, and human-rights validation engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import jsonschema

ROOT = Path(__file__).resolve().parent.parent.parent
PROGRAM_SCHEMA_PATH = ROOT / "schemas" / "program.schema.json"
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
SAMPLE_JSONL = ROOT / "data" / "sample" / "programs_sample_100.jsonl"
REPORT_MD = ROOT / "reports" / "validation_report.md"


def validate_programs(programs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    schema = json.loads(PROGRAM_SCHEMA_PATH.read_text(encoding="utf-8"))
    sources_data = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    accessible_ids = {
        s["source_id"]
        for s in sources_data["sources"]
        if s["verification_status"] == "VERIFIED_ACCESSIBLE"
    }

    valid: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for prog in programs:
        try:
            jsonschema.validate(instance=prog, schema=schema)
            for sid in prog["inspiration_source_ids"]:
                if sid not in accessible_ids:
                    raise ValueError(f"Inspiration source {sid} is not VERIFIED_ACCESSIBLE")
            if prog["epistemic_label"] != "PROPOSED_RESEARCH_PROGRAM":
                raise ValueError("Invalid epistemic_label")
            valid.append(prog)
        except Exception as exc:
            errors.append({"program_id": prog.get("program_id", "UNKNOWN"), "error": str(exc)})

    return valid, errors


def main() -> None:
    programs = [
        json.loads(line)
        for line in SAMPLE_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    valid, errors = validate_programs(programs)

    tier_counts: Dict[str, int] = {}
    for p in valid:
        t = p["human_rights_risk_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    avg_quality = round(sum(p["quality_score"] for p in valid) / max(len(valid), 1), 2)

    lines = [
        "# Structural & Governance Validation Report",
        "",
        f"- **Total Candidates Audited:** {len(programs)}",
        f"- **Schema & Epistemic Pass:** {len(valid)}",
        f"- **Validation Failures:** {len(errors)}",
        f"- **Mean Quality Score:** {avg_quality} / 100.0",
        "",
        "## Human-Rights Risk Tier Distribution",
        "| Risk Tier | Count |",
        "| :--- | :--- |",
    ]
    for tier, count in sorted(tier_counts.items()):
        lines.append(f"| {tier} | {count} |")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Validated {len(valid)}/{len(programs)} programs (errors: {len(errors)}, avg quality: {avg_quality})")
    assert len(errors) == 0, f"Validation errors found: {errors}"


if __name__ == "__main__":
    main()
