"""Unit tests for Phase 3 Task 027 Adversarial Robustness & Epistemic Boundary Stress-Test."""

import json
import unittest
from pathlib import Path

from src.prototype.adversarial_stress_tester import run_stress_tests

ROOT = Path(__file__).resolve().parent.parent


class TestV27AdversarialStress(unittest.TestCase):
    def test_adversarial_stress_suite_passes_100_percent(self) -> None:
        summary = run_stress_tests()
        self.assertEqual(summary["total_tests"], 10)
        self.assertEqual(summary["passed_tests"], 10)
        self.assertEqual(summary["pass_rate"], 1.0)
        self.assertEqual(summary["prototype_status"], "PROTOTYPE_EXPERIMENTAL_NONBINDING")

    def test_stress_results_and_v27_manifest_exist(self) -> None:
        out = json.loads((ROOT / "data" / "sample" / "adversarial_stress_test_results.json").read_text(encoding="utf-8"))
        self.assertEqual(len(out["case_results"]), 8)
        self.assertEqual(len(out["epistemic_checks"]), 2)
        self.assertTrue((ROOT / "reports" / "ADVERSARIAL_STRESS_TEST.md").exists())


if __name__ == "__main__":
    unittest.main()
