import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV22Europe(unittest.TestCase):
    def test_europe_matrix_and_eur_500(self):
        mat = pd.read_csv(ROOT / "data" / "curated" / "europe_comparative_matrix.csv")
        self.assertEqual(len(mat), 9)
        self.assertTrue((mat["evidence_label"] == "EXISTING_REAL_WORLD_RECORD").all())

        eur = pd.read_parquet(ROOT / "data" / "curated" / "europe_eur_programs_500.parquet")
        self.assertEqual(len(eur), 500)
        self.assertTrue((eur["D01_jurisdiction_archetype"] == "EUR").all())


if __name__ == "__main__":
    unittest.main()
