import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestV16PrecedentGraph(unittest.TestCase):
    def test_precedent_graph_and_dataset_card(self):
        df = pd.read_csv(ROOT / "data" / "curated" / "precedent_graph_edges.csv")
        self.assertGreaterEqual(len(df), 90)
        self.assertNotIn("Zambia", set(df["jurisdiction"]))
        self.assertTrue((df["evidence_label"] == "EXISTING_REAL_WORLD_RECORD").all())
        card = (ROOT / "reports" / "KAGGLE_DATASET_CARD.md").read_text(encoding="utf-8")
        self.assertIn("judicialcollege/ijc-global-ai-justice-universe", card)


if __name__ == "__main__":
    unittest.main()
