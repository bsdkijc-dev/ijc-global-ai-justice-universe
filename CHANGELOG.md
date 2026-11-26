# Changelog

## [0.2.0] - 2026-11-26
- Completed Task 002:
  - Built and validated 46-country Comparative Jurisdiction Atlas (`data/curated/jurisdiction_atlas_46.{csv,json}`, `reports/COMPARATIVE_JURISDICTION_ATLAS.md`).
  - Implemented evidence provenance linker (`src/evidence/provenance.py`).
  - Curated 1,000 validated, TF-IDF-screened programs (`data/curated/programs_curated_1000.{csv,jsonl,parquet,sqlite}`, `data/manifests/curated_1000_manifest.json`).
  - Selected Top-10 regionally diverse Pilot Prototypes (`data/curated/top10_pilot_prototypes.{csv,json}`, `reports/PILOT_PROTOTYPE_SELECTION.md`).
  - Added `notebooks/02_comparative_atlas_and_pilots.ipynb`, `tests/test_jurisdiction_atlas.py`, `tests/test_curated_1000.py`, and `docs/INDEX.md`.

## [0.1.0] - 2026-11-25
- Completed Task 001: Workstation audit, 47-URL Oxford AI Justice Atlas source audit (46 accessible, 1 inaccessible), 30-pillar ontology, 12D generative schema (`8,957,952,000,000` addressable configurations), deterministic 100-program generator, JSON Schema validator, TF-IDF/Jaccard originality screener, multi-format exporter (CSV/JSONL/Parquet/SQLite), unit tests, and `01_global_source_audit.ipynb`.
