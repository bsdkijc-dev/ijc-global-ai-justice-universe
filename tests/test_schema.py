import json
import unittest
from pathlib import Path
from src.validation.validator import validate_programs

ROOT = Path(__file__).resolve().parent.parent


class TestSchemaValidation(unittest.TestCase):
    def test_sample_100_passes_schema(self):
        sample_path = ROOT / "data" / "sample" / "programs_sample_100.jsonl"
        programs = [
            json.loads(line)
            for line in sample_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        valid, errors = validate_programs(programs)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(valid), 100)


if __name__ == "__main__":
    unittest.main()
