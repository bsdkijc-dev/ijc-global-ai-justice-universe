import unittest
from pathlib import Path
from src.validation.verify_manifests import verify_all_manifests

ROOT = Path(__file__).resolve().parent.parent


class TestV15Integrity(unittest.TestCase):
    def test_all_manifests_and_whitepaper(self):
        res = verify_all_manifests()
        self.assertTrue(res["all_passed"])
        self.assertGreaterEqual(res["total_files_verified"], 13)
        wp = (ROOT / "reports" / "SYSTEM_WHITEPAPER_V1_5.md").read_text(encoding="utf-8")
        self.assertIn("8,957,952,000,000", wp)


if __name__ == "__main__":
    unittest.main()
