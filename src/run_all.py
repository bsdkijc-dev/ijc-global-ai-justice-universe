"""Single-command end-to-end pipeline orchestrator for IJC-GAJIU v2.0.0."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULES = [
    "src.ontology.verify_cardinality",
    "src.evidence.jurisdiction_atlas",
    "src.evidence.governance_readiness_index",
    "src.evidence.ai_systems_inventory",
    "src.evidence.precedent_graph",
    "src.prototype.build_authority_corpus",
    "src.prototype.multilingual_glossary",
    "src.prototype.citation_and_triage_gate",
    "src.prototype.anonymisation_gate",
    "src.prototype.risk_audit_simulator",
    "src.prototype.synthetic_media_gate",
    "src.prototype.srl_kiosk_guide",
    "src.prototype.procurement_auditor",
    "src.prototype.aia_generator",
    "src.ontology.pillar_gap_analysis",
    "src.ontology.roadmap_2045",
    "src.ontology.curriculum_generator",
    "src.export.build_pages_portal",
    "src.export.release_packager",
    "src.validation.verify_manifests",
]


def main() -> None:
    for mod in MODULES:
        print(f"==> Running {mod}")
        subprocess.run([sys.executable, "-m", mod], cwd=ROOT, check=True)
    print("==> Running full unittest suite")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    print("All v2.0.0 modules and tests completed cleanly.")


if __name__ == "__main__":
    main()
