import unittest
from src.prototype.citation_and_triage_gate import run_benchmark, verify_citations


class TestPrototype(unittest.TestCase):
    def test_citation_gate_detects_verified_and_unverified(self):
        res = verify_citations("Brief citing [2025] ADGMCFI 0032 and Fake v PhantomCase.")
        self.assertEqual(res["citations_detected"], 2)
        self.assertEqual(len(res["verified_citations"]), 1)
        self.assertEqual(len(res["unverified_citations"]), 1)
        self.assertEqual(res["gate_status"], "FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED")

    def test_benchmark_100_percent_accuracy(self):
        summary = run_benchmark()
        self.assertEqual(summary["exact_citation_detection_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
