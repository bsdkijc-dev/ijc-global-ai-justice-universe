import unittest
from pathlib import Path
from src.prototype.procurement_auditor import run_benchmark

ROOT = Path(__file__).resolve().parent.parent


class TestV19Procurement(unittest.TestCase):
    def test_procurement_benchmark_and_exec_summary(self):
        summary = run_benchmark()
        self.assertEqual(summary["exact_audit_accuracy"], 1.0)
        es = (ROOT / "reports" / "EXECUTIVE_SUMMARY_2027_2045.md").read_text(encoding="utf-8")
        self.assertIn("8,957,952,000,000", es)


if __name__ == "__main__":
    unittest.main()
