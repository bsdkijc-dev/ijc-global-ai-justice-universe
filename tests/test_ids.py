import re
import unittest
from src.generator.program_generator import generate_batch


class TestProgramIDs(unittest.TestCase):
    def test_canonical_id_format_and_uniqueness(self):
        programs = generate_batch(sample_size=25, seed=2027)
        pattern = re.compile(r"^IJC-GAJIU-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-F0-9]{6}$")
        ids = [p["program_id"] for p in programs]
        for pid in ids:
            self.assertRegex(pid, pattern)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
