import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV11SyntheticMediaAnd100K(unittest.TestCase):
    def test_synthetic_media_gate_and_100k_parquet(self):
        bench = json.loads((ROOT / "data" / "sample" / "synthetic_media_benchmark_results.json").read_text(encoding="utf-8"))
        self.assertEqual(bench["exact_gate_accuracy"], 1.0)
        df = pd.read_parquet(ROOT / "data" / "curated" / "programs_curated_100000.parquet")
        self.assertEqual(len(df), 100_000)
        self.assertEqual(df["tuple_sha256"].nunique(), 100_000)


if __name__ == "__main__":
    unittest.main()
