"""Phase 3 (Task 029): Unified Phase 3 Audit Pipeline & Synthesis."""

import json
from pathlib import Path
from typing import Any, Dict

from src.prototype.neuro_symbolic_reasoner import run_benchmark as run_nsy
from src.prototype.adversarial_stress_tester import run_stress_tests as run_adv
from src.prototype.statutory_harmonizer import run_harmonization_mapper as run_harm

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_OUT = ROOT / "data" / "sample" / "phase3_unified_audit.json"
REPORTS_DIR = ROOT / "reports"


def run_phase3_pipeline() -> Dict[str, Any]:
    nsy = run_nsy()
    adv = run_adv()
    harm = run_harm()

    summary = {
        "pipeline_id": "IJC-GAJIU-PHASE3-UNIFIED-01",
        "prototype_status": "PROTOTYPE_EXPERIMENTAL_NONBINDING",
        "neuro_symbolic": {
            "benchmark_cases": nsy["benchmark_cases"],
            "exact_norm_accuracy": nsy["exact_norm_accuracy"],
            "authority_corpus_size": nsy["authority_corpus_size"],
        },
        "adversarial_stress": {
            "total_tests": adv["total_tests"],
            "passed_tests": adv["passed_tests"],
            "pass_rate": adv["pass_rate"],
        },
        "statutory_harmonization": {
            "total_cells": harm["total_cells"],
            "status_counts": harm["status_counts"],
        },
    }
    AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Phase 3 Synthesis — Neuro-Symbolic, Adversarial & Statutory Harmonization",
        "",
        "**Prototype Status:** `PROTOTYPE_EXPERIMENTAL_NONBINDING`",
        "",
        "## Integrated Phase 3 Benchmarks",
        f"- **Task 026 (Neuro-Symbolic Engine):** `{nsy['exact_norm_accuracy']*100:.1f}%` exact norm accuracy (`{nsy['benchmark_cases']}/{nsy['benchmark_cases']}`) over `{nsy['authority_corpus_size']}` verified Oxford authorities.",
        f"- **Task 027 (Adversarial & Epistemic Stress-Test):** `{adv['pass_rate']*100:.1f}%` pass rate (`{adv['passed_tests']}/{adv['total_tests']}`) including counterfactual flips, prompt-injection immunity, and `OXF-AIATLAS-44` Zambia non-imputation.",
        f"- **Task 028 (Statutory Harmonization Mapper):** `{harm['total_cells']}` grounded regional cells (`{harm['status_counts']['CONVERGENT_ANCHOR']}` convergent, `{harm['status_counts']['EMERGING_ALIGNMENT']}` emerging, `{harm['status_counts']['DIVERGENT_OR_GAP']}` gap).",
        "- **Task 029 (Interactive Portal Simulator):** Zero-CDN client-side Neuro-Symbolic Safeguard Simulator embedded in `docs/index.html`.",
    ]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "PHASE_3_SYNTHESIS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("Phase 3 unified pipeline complete")
    return summary


if __name__ == "__main__":
    run_phase3_pipeline()
