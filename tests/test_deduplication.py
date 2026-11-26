import json
import unittest
from pathlib import Path
from src.originality.deduplicator import screen_originality

ROOT = Path(__file__).resolve().parent.parent


class TestDeduplication(unittest.TestCase):
    def test_no_exact_or_near_duplicates(self):
        sample_path = ROOT / "data" / "sample" / "programs_sample_100.jsonl"
        programs = [
            json.loads(line)
            for line in sample_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        _, stats = screen_originality(programs, threshold=0.85)
        self.assertEqual(stats["exact_hash_duplicates"], 0)
        self.assertEqual(stats["flagged_near_duplicate_pairs"], 0)


if __name__ == "__main__":
    unittest.main()
