import json
import unittest
from pathlib import Path
from src.prototype.srl_kiosk_guide import run_benchmark, triage_srl_query

ROOT = Path(__file__).resolve().parent.parent


class TestV18SRLKiosk(unittest.TestCase):
    def test_srl_kiosk_benchmark_and_disclaimer(self):
        summary = run_benchmark()
        self.assertEqual(summary["exact_triage_accuracy"], 1.0)
        res = triage_srl_query("Unpaid salary and employer dismissed worker.")
        self.assertEqual(res["triage_domain"], "LABOR_DISPUTE")
        self.assertIn("not legal advice", res["disclaimer"])
        dash = (ROOT / "reports" / "ECOSYSTEM_STATUS_V1_8.md").read_text(encoding="utf-8")
        self.assertIn("Tasks 001–018", dash)


if __name__ == "__main__":
    unittest.main()
