import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestV1Release(unittest.TestCase):
    def test_v1_manifest_and_orchestrator_exist(self):
        manifest = json.loads((ROOT / "data" / "manifests" / "release_v1.0.0_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_version"], "1.0.0")
        self.assertEqual(len(manifest["files"]), 19)
        self.assertTrue((ROOT / "src" / "run_all.py").exists())
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "1.0.0"', pyproject)


if __name__ == "__main__":
    unittest.main()
