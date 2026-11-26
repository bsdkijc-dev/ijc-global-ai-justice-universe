import json
import unittest
from pathlib import Path
from src.prototype.anonymisation_gate import anonymise_text, run_benchmark

ROOT = Path(__file__).resolve().parent.parent


class TestAnonymisationAndGlossary(unittest.TestCase):
    def test_anonymisation_preserves_legal_citations_and_redacts_pii(self):
        res = anonymise_text("Contact test@court.org, phone +62 812-3456-7890, citing State v Loomis.")
        self.assertEqual(res["total_redactions"], 2)
        self.assertIn("State v Loomis", res["anonymised_text"])
        self.assertNotIn("test@court.org", res["anonymised_text"])

    def test_anonymisation_benchmark_100_percent(self):
        summary = run_benchmark()
        self.assertEqual(summary["exact_redaction_accuracy"], 1.0)

    def test_multilingual_glossary_50_terms_5_languages(self):
        terms = json.loads((ROOT / "data" / "curated" / "multilingual_glossary_50.json").read_text(encoding="utf-8"))
        self.assertEqual(len(terms), 50)
        for t in terms:
            for lang in ["en", "id_ms", "es", "fr", "ar"]:
                self.assertTrue(bool(t[lang].strip()))


if __name__ == "__main__":
    unittest.main()
