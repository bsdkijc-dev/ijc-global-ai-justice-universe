import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV21AseanApac(unittest.TestCase):
    def test_asean_apac_matrix_and_sea_500(self):
        mat = pd.read_csv(ROOT / "data" / "curated" / "asean_apac_comparative_matrix.csv")
        self.assertEqual(len(mat), 17)
        covered = mat[mat["coverage_status"] == "COVERED_OXFORD_VERIFIED"]
        gaps = mat[mat["coverage_status"] == "NOT_IN_OXFORD_INITIAL_CORPUS_GAP_IDENTIFIED"]
        self.assertEqual(len(covered), 11)
        self.assertEqual(len(gaps), 6)

        sea = pd.read_parquet(ROOT / "data" / "curated" / "asean_sea_programs_500.parquet")
        self.assertEqual(len(sea), 500)
        self.assertTrue((sea["D01_jurisdiction_archetype"] == "SEA").all())


if __name__ == "__main__":
    unittest.main()
