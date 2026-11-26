"""Unit tests for Phase 3 Task 028 Cross-Jurisdictional Statutory Harmonizer."""

import json
import unittest
from pathlib import Path

from src.prototype.statutory_harmonizer import run_harmonization_mapper

ROOT = Path(__file__).resolve().parent.parent


class TestV28StatutoryHarmonizer(unittest.TestCase):
    def test_harmonization_matrix_30_cells_and_grounded(self) -> None:
        summary = run_harmonization_mapper()
        self.assertEqual(summary["total_cells"], 30)
        self.assertEqual(summary["regions_count"], 5)
        self.assertEqual(summary["norms_count"], 6)
        self.assertEqual(summary["prototype_status"], "PROTOTYPE_EXPERIMENTAL_NONBINDING")

    def test_harmonization_outputs_exist(self) -> None:
        self.assertTrue((ROOT / "data" / "curated" / "statutory_harmonization_matrix.csv").exists())
        self.assertTrue((ROOT / "reports" / "STATUTORY_HARMONIZATION_MAP.md").exists())
        out = json.loads((ROOT / "data" / "sample" / "statutory_harmonization_results.json").read_text(encoding="utf-8"))
        self.assertEqual(len(out["matrix"]), 30)


if __name__ == "__main__":
    unittest.main()
