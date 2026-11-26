import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV12ReadinessAnd1M(unittest.TestCase):
    def test_governance_readiness_and_1m_manifest(self):
        df = pd.read_csv(ROOT / "data" / "curated" / "governance_readiness_46.csv")
        self.assertEqual(len(df), 46)
        zambia = df[df["jurisdiction_name"] == "Zambia"].iloc[0]
        self.assertEqual(zambia["tier"], "INACCESSIBLE_NO_IMPUTATION")
        self.assertTrue(pd.isna(zambia["readiness_score"]))

        m = json.loads((ROOT / "data" / "manifests" / "scale_1m_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["record_count"], 1_000_000)
        self.assertEqual(m["unique_hashes"], 1_000_000)


if __name__ == "__main__":
    unittest.main()
