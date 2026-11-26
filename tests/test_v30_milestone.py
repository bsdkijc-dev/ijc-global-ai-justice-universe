"""Unit tests for Phase 3 Task 030 (v3.0.0) Milestone Release."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestV30Milestone(unittest.TestCase):
    def test_v30_manifest_and_30_notebooks(self) -> None:
        manifest = json.loads((ROOT / "data" / "manifests" / "release_v3.0.0_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_version"], "3.0.0")
        self.assertEqual(len(manifest["files"]), 45)
        nbs = list((ROOT / "notebooks").glob("*.ipynb"))
        self.assertGreaterEqual(len(nbs), 30)

    def test_v30_version_metadata(self) -> None:
        self.assertIn('version = "3.0.0"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn('version: "3.0.0"', (ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        self.assertIn("## [3.0.0]", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
