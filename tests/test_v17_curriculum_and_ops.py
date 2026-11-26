import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV17CurriculumAndOps(unittest.TestCase):
    def test_curriculum_10_modules_and_playbook(self):
        df = pd.read_csv(ROOT / "data" / "curated" / "judicial_ai_curriculum_10.csv")
        self.assertEqual(len(df), 10)
        for lab in df["lab_module"]:
            self.assertTrue((ROOT / lab).exists(), f"Missing lab module {lab}")
        playbook = (ROOT / "docs" / "MAINTENANCE_PLAYBOOK.md").read_text(encoding="utf-8")
        self.assertIn("python3 -m src.run_all", playbook)


if __name__ == "__main__":
    unittest.main()
