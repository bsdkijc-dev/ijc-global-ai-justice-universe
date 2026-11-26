import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestJurisdictionAtlas(unittest.TestCase):
    def test_46_countries_and_zambia_inaccessible(self):
        data = json.loads((ROOT / "data" / "curated" / "jurisdiction_atlas_46.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data), 46)
        accessible = [r for r in data if r["verification_status"] == "VERIFIED_ACCESSIBLE"]
        self.assertEqual(len(accessible), 45)
        zambia = [r for r in data if r["jurisdiction_name"] == "Zambia"][0]
        self.assertEqual(zambia["verification_status"], "SOURCE_INACCESSIBLE")
        self.assertIsNone(zambia["has_hallucination_cases"])


if __name__ == "__main__":
    unittest.main()
