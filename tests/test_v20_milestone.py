import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestV20Milestone(unittest.TestCase):
    def test_v20_release_20_notebooks_and_metadata(self):
        m = json.loads((ROOT / "data" / "manifests" / "release_v2.0.0_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["release_version"], "2.0.0")
        self.assertEqual(len(m["files"]), 30)
        nbs = list((ROOT / "notebooks").glob("*.ipynb"))
        self.assertEqual(len(nbs), 20)
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "2.0.0"', pyproject)


if __name__ == "__main__":
    unittest.main()
