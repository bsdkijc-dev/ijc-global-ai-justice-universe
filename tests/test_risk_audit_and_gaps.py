import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestRiskAuditAndGaps(unittest.TestCase):
    def test_risk_audit_flags_disparity_and_30_pillars_covered(self):
        res = json.loads((ROOT / "data" / "sample" / "risk_audit_benchmark_results.json").read_text(encoding="utf-8"))
        self.assertEqual(res["audit_status"], "FLAG_DISPARITY_EXCEEDS_THRESHOLD_HITL_REVIEW")
        self.assertGreater(res["false_positive_rate_gap"], res["fpr_gap_threshold"])

        df = pd.read_csv(ROOT / "data" / "curated" / "pillar_coverage_30.csv")
        self.assertEqual(len(df), 30)
        self.assertEqual(int(df["programs_10k_count"].sum()), 10_000)


if __name__ == "__main__":
    unittest.main()
