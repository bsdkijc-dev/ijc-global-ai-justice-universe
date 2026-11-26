import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCLIAndCI(unittest.TestCase):
    def test_ci_workflow_and_interactive_pages_exist(self):
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("unittest discover -s tests -v", ci)
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Interactive Citation Verification Gate", html)
        self.assertIn("runGate()", html)

    def test_cli_outputs_valid_json_audit(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.prototype.cli",
                "--text",
                "Brief citing [2025] ADGMCFI 0032 and Fake v GhostCase.",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["gate_status"], "FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED")
        self.assertEqual(len(data["verified_citations"]), 1)
        self.assertEqual(len(data["unverified_citations"]), 1)


if __name__ == "__main__":
    unittest.main()
