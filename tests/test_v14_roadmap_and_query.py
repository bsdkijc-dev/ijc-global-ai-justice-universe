import unittest
from pathlib import Path
import pandas as pd
from src.evidence.query_cli import search_all

ROOT = Path(__file__).resolve().parent.parent


class TestV14RoadmapAndQuery(unittest.TestCase):
    def test_horizon_roadmap_and_unified_query(self):
        df = pd.read_csv(ROOT / "data" / "curated" / "horizon_roadmap_2027_2045.csv")
        self.assertEqual(len(df), 10)
        self.assertEqual(int(df["programs_100k_count"].sum()), 100_000)

        res_prom = search_all("PROMETEA")
        self.assertEqual(res_prom["counts"]["systems"], 2)

        res_col = search_all("Colombia")
        self.assertGreaterEqual(res_col["counts"]["authorities"], 1)
        self.assertEqual(res_col["counts"]["readiness"], 1)


if __name__ == "__main__":
    unittest.main()
