import json
import unittest
from pathlib import Path
from src.validation.validator import validate_programs

ROOT = Path(__file__).resolve().parent.parent


class TestCurated1000(unittest.TestCase):
    def test_curated_1000_and_top10_pilots(self):
        path = ROOT / "data" / "curated" / "programs_curated_1000.jsonl"
        programs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(programs), 1000)
        valid, errors = validate_programs(programs)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(valid), 1000)

        pilots = json.loads((ROOT / "data" / "curated" / "top10_pilot_prototypes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(pilots), 10)
        for p in pilots:
            self.assertNotEqual(p["human_rights_risk_tier"], "TIER_4_PROHIBITED_OR_MORATORIUM_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
