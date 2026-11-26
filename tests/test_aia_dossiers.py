import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestAIADossiers(unittest.TestCase):
    def test_top10_aia_dossiers_and_portal_features(self):
        dossiers = json.loads((ROOT / "data" / "curated" / "top10_pilot_aia_dossiers.json").read_text(encoding="utf-8"))
        self.assertEqual(len(dossiers), 10)
        for d in dossiers:
            self.assertEqual(d["aia_status"], "PROPOSED_UNVALIDATED_AIA_TEMPLATE")
            self.assertGreaterEqual(len(d["mandatory_safeguards"]), 3)

        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Interactive Judgment Anonymisation Playground", html)
        self.assertIn("5-Language AI &amp; Justice Glossary", html)


if __name__ == "__main__":
    unittest.main()
