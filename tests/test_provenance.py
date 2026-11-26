import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestProvenance(unittest.TestCase):
    def test_only_verified_accessible_sources_linked(self):
        reg = json.loads((ROOT / "sources" / "source-registry.json").read_text(encoding="utf-8"))
        inaccessible = {
            s["source_id"]
            for s in reg["sources"]
            if s["verification_status"] != "VERIFIED_ACCESSIBLE"
        }
        self.assertIn("OXF-AIATLAS-44", inaccessible)
        sample_path = ROOT / "data" / "sample" / "programs_sample_100.jsonl"
        for line in sample_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                prog = json.loads(line)
                for sid in prog["inspiration_source_ids"]:
                    self.assertNotIn(sid, inaccessible)


if __name__ == "__main__":
    unittest.main()
