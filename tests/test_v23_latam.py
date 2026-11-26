import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV23Latam(unittest.TestCase):
    def test_latam_matrix_and_lat_500(self):
        mat = pd.read_csv(ROOT / "data" / "curated" / "latam_comparative_matrix.csv")
        self.assertEqual(len(mat), 5)
        self.assertTrue((mat["evidence_label"] == "EXISTING_REAL_WORLD_RECORD").all())

        lat = pd.read_parquet(ROOT / "data" / "curated" / "latam_lat_programs_500.parquet")
        self.assertEqual(len(lat), 500)
        self.assertTrue((lat["D01_jurisdiction_archetype"] == "LAT").all())


if __name__ == "__main__":
    unittest.main()
