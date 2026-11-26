import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV25NamEca(unittest.TestCase):
    def test_nam_eca_matrix_and_phase2_synthesis(self):
        mat = pd.read_csv(ROOT / "data" / "curated" / "nam_eca_comparative_matrix.csv")
        self.assertEqual(len(mat), 7)
        self.assertTrue((mat["evidence_label"] == "EXISTING_REAL_WORLD_RECORD").all())

        df = pd.read_parquet(ROOT / "data" / "curated" / "nam_eca_programs_500.parquet")
        self.assertEqual(len(df), 500)
        self.assertEqual((df["D01_jurisdiction_archetype"] == "NAM").sum(), 250)
        self.assertEqual((df["D01_jurisdiction_archetype"] == "ECA").sum(), 250)

        syn = (ROOT / "reports" / "PHASE_2_REGIONAL_SYNTHESIS.md").read_text(encoding="utf-8")
        self.assertIn("2,500", syn)


if __name__ == "__main__":
    unittest.main()
