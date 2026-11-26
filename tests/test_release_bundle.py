import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestReleaseBundle(unittest.TestCase):
    def test_release_v030_manifest_and_archive_exist(self):
        manifest = json.loads((ROOT / "data" / "manifests" / "release_v0.3.0_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_version"], "0.3.0")
        self.assertEqual(manifest["publication_status"], "STAGED_LOCALLY_NOT_PUBLISHED")
        archive_path = ROOT / "data" / "releases" / manifest["archive"]["filename"]
        self.assertTrue(archive_path.exists())
        self.assertEqual(len(manifest["files"]), 10)


if __name__ == "__main__":
    unittest.main()
