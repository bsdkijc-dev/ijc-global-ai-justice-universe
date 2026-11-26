import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestScale10K(unittest.TestCase):
    def test_10k_parquet_and_policy_brief(self):
        df = pd.read_parquet(ROOT / "data" / "curated" / "programs_curated_10000.parquet")
        self.assertEqual(len(df), 10_000)
        self.assertEqual(df["tuple_sha256"].nunique(), 10_000)
        self.assertTrue((df["epistemic_label"] == "PROPOSED_RESEARCH_PROGRAM").all())
        brief = (ROOT / "reports" / "POLICY_BRIEF_2026_01.md").read_text(encoding="utf-8")
        self.assertIn("PB-GAJIU-2026-01", brief)


if __name__ == "__main__":
    unittest.main()
