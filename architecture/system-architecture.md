# System Architecture — IJC Global AI & Justice Innovation Universe

## 1. Design Constraints
- **Solo Founder Operations**: Modular Python 3.11 architecture runnable on a single workstation (Dell Precision 7540 or standard CPU Linux VM) with zero paid APIs or cloud lock-in.
- **Trillion-Scale Combinatorial Representation**: The `1,000,000,000,000` (`10^12`) program universe is represented **mathematically and deterministically** via a 12-dimensional taxonomy (`|D1| x |D2| x ... x |D12| >= 10^12`). Only sampled, validated, and ranked subsets are materialized to disk.
- **Zero-Cost Open Stack**: Python stdlib, `pandas`, `pyarrow`, `jsonschema`, `matplotlib`, `sqlite3`, Git, and Kaggle-ready Parquet/CSV/JSONL exports.

## 2. Pipeline Stages
1. **Source Ingestion & Audit (`sources/`)**: Verified external corpus (Oxford AI Justice Atlas) with strict `EXISTING_REAL_WORLD_RECORD` vs. `SOURCE_INACCESSIBLE` tagging.
2. **Ontology & Taxonomy (`src/ontology/`)**: 30 research pillars and 12 orthogonal generative dimensions.
3. **Deterministic Generator (`src/generator/`)**: Seeded combinatorial sampler producing canonical IDs `IJC-GAJIU-[JUR]-[DOM]-[INST]-[WF]-[HASH6]`.
4. **Structural & Rights Validation (`src/validation/`)**: JSON Schema validation, epistemic label enforcement, human-rights risk tiering, and 100-point quality scoring.
5. **Originality & Deduplication Engine (`src/originality/`)**: Exact hash deduplication, token Jaccard similarity, and TF-IDF cosine screening.
6. **Evidence & Export (`src/evidence/`, `src/export/`)**: Multi-format export (CSV, JSONL, Parquet, SQLite) and manifest generation with SHA-256 checksums.
