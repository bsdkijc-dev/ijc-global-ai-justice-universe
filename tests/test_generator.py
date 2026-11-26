import unittest
from src.generator.program_generator import generate_batch
from src.ontology.taxonomy import compute_cardinality


class TestGenerator(unittest.TestCase):
    def test_determinism_and_cardinality(self):
        total, counts = compute_cardinality()
        self.assertGreaterEqual(total, 1_000_000_000_000)
        self.assertEqual(len(counts), 12)
        b1 = generate_batch(sample_size=10, seed=2027)
        b2 = generate_batch(sample_size=10, seed=2027)
        self.assertEqual([p["program_id"] for p in b1], [p["program_id"] for p in b2])


if __name__ == "__main__":
    unittest.main()
