"""Unit tests for Phase 3 Task 029 Unified Pipeline & Interactive Portal Simulator."""

import json
import unittest
from pathlib import Path

from src.prototype.phase3_pipeline import run_phase3_pipeline

ROOT = Path(__file__).resolve().parent.parent


class TestV29Phase3Pipeline(unittest.TestCase):
    def test_phase3_unified_pipeline_passes(self) -> None:
        summary = run_phase3_pipeline()
        self.assertEqual(summary["neuro_symbolic"]["exact_norm_accuracy"], 1.0)
        self.assertEqual(summary["adversarial_stress"]["pass_rate"], 1.0)
        self.assertEqual(summary["statutory_harmonization"]["total_cells"], 30)

    def test_portal_contains_neuro_symbolic_simulator(self) -> None:
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("runNeuroSymbolic()", html)
        self.assertIn("NORM-01_NON_DELEGATION_ADJUDICATION", html)
        self.assertTrue((ROOT / "reports" / "PHASE_3_SYNTHESIS.md").exists())
        audit = json.loads((ROOT / "data" / "sample" / "phase3_unified_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["pipeline_id"], "IJC-GAJIU-PHASE3-UNIFIED-01")


if __name__ == "__main__":
    unittest.main()
