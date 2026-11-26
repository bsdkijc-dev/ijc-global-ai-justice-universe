# Kaggle Dataset Card — `judicialcollege/ijc-global-ai-justice-universe`

## Summary
An open-research comparative dataset and 12-dimensional generative ecosystem for **AI, Courts, Criminal Justice, and Judicial Governance (2027–2045)**, created by **Cecep Mustafa** with zero incremental cash expenditure.

## Epistemic Labeling Policy
1. **`EXISTING_REAL_WORLD_RECORD`**: Empirical records audited from 46 verified accessible [Oxford AI Justice Atlas](https://www.techandjustice.bsg.ox.ac.uk/ai-atlas) URLs (`source-registry.{csv,json}`, `jurisdiction_atlas_46.{csv,json}`, `governance_readiness_46.csv`, `ai_systems_inventory.{csv,json}`, `verified_authority_corpus.json`, `precedent_graph_edges.csv`).
2. **`UNVERIFIED_INACCESSIBLE_SOURCE`**: `OXF-AIATLAS-44` (Zambia) could not be accessed during live audit and is retained with null/empty indicator fields (zero imputation).
3. **`PROPOSED_RESEARCH_PROGRAM` (`PROPOSED_UNVALIDATED`)**: Combinatorial 12D research configurations (`programs_curated_1000.{csv,parquet}`, `programs_curated_10000.parquet`, `programs_curated_100000.parquet`, `top10_pilot_prototypes.{csv,json}`, `top10_pilot_aia_dossiers.json`).
4. **`PROTOTYPE_EXPERIMENTAL_NONBINDING`**: Offline CPU benchmark outputs (`prototype_benchmark_results.json`, `anonymisation_benchmark_results.json`, `risk_audit_benchmark_results.json`, `synthetic_media_benchmark_results.json`).

## License & Citation
- **License:** MIT (`LICENSE`)
- **Code Repository:** https://github.com/bsdkijc-dev/ijc-global-ai-justice-universe
