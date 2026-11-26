import json
import unittest
from pathlib import Path
from src.prototype.citation_and_triage_gate import verify_citations

ROOT = Path(__file__).resolve().parent.parent


class TestCorpusAndPages(unittest.TestCase):
    def test_authority_corpus_and_real_case_detection(self):
        corpus = json.loads((ROOT / "data" / "curated" / "verified_authority_corpus.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(corpus), 200)
        res = verify_citations("Appeal citing Nash v DPP and Pulserate Investments v Zuze.")
        self.assertGreaterEqual(len(res["verified_citations"]), 1)

    def test_github_pages_index_exists(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("IJC Global AI &amp; Justice Innovation Universe", html)
        self.assertIn("8,957,952,000,000", html)


if __name__ == "__main__":
    unittest.main()
