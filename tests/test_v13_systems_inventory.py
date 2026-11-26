import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV13SystemsInventory(unittest.TestCase):
    def test_systems_inventory_and_portal(self):
        df = pd.read_csv(ROOT / "data" / "curated" / "ai_systems_inventory.csv")
        self.assertGreaterEqual(len(df), 300)
        self.assertTrue((df["evidence_label"] == "EXISTING_REAL_WORLD_RECORD").all())
        self.assertNotIn("Zambia", set(df["jurisdiction"]))

        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Real-World Justice AI Systems Inventory", html)


if __name__ == "__main__":
    unittest.main()
