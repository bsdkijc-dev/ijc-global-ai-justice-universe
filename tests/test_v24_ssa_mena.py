import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV24SsaMena(unittest.TestCase):
    def test_ssa_mena_matrix_and_500_programs(self):
        mat = pd.read_csv(ROOT / "data" / "curated" / "ssa_mena_comparative_matrix.csv")
        self.assertEqual(len(mat), 14)
        zambia = mat[mat["jurisdiction"] == "Zambia"].iloc[0]
        self.assertEqual(zambia["verification_status"], "SOURCE_INACCESSIBLE")

        df = pd.read_parquet(ROOT / "data" / "curated" / "ssa_mena_programs_500.parquet")
        self.assertEqual(len(df), 500)
        self.assertEqual((df["D01_jurisdiction_archetype"] == "SSA").sum(), 250)
        self.assertEqual((df["D01_jurisdiction_archetype"] == "MEN").sum(), 250)
        for src_list in df["inspiration_source_ids"]:
            self.assertNotIn("OXF-AIATLAS-44", str(src_list))


if __name__ == "__main__":
    unittest.main()
