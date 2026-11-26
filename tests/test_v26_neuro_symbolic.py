import unittest
from pathlib import Path
from src.prototype.neuro_symbolic_reasoner import run_benchmark

ROOT = Path(__file__).resolve().parent.parent


class TestV26NeuroSymbolic(unittest.TestCase):
    def test_neuro_symbolic_6_of_6_and_grounded_precedents(self):
        summary = run_benchmark()
        self.assertEqual(summary["exact_norm_accuracy"], 1.0)
        self.assertEqual(summary["authority_corpus_size"], 238)
        for r in summary["results"]:
            self.assertEqual(len(r["grounded_precedents"]), 3)
            self.assertGreater(r["grounded_precedents"][0]["similarity"], 0.0)


if __name__ == "__main__":
    unittest.main()
