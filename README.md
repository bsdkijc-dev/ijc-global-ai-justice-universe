# IJC Global AI & Justice Innovation Universe (`v1.0.0`)

**Founder:** Cecep Mustafa  
**Horizon:** 2027–2045  
**Budget Policy:** Zero Incremental Cash Expenditure  
**GitHub:** https://github.com/bsdkijc-dev/ijc-global-ai-justice-universe  
**Kaggle:** https://www.kaggle.com/datasets/judicialcollege/ijc-global-ai-justice-universe

## Overview
An independent open-research and open-source ecosystem representing **8,957,952,000,000** (8.958 trillion) addressable AI-and-justice program configurations across a 12-dimensional taxonomy and 30 global research pillars, grounded in the [Oxford AI Justice Atlas](https://www.techandjustice.bsg.ox.ac.uk/ai-atlas).

## Key `v1.0.0` Components
- **Source Audit (`sources/`)**: 47 Oxford AI Justice Atlas URLs audited (46 `VERIFIED_ACCESSIBLE`, 1 `SOURCE_INACCESSIBLE` Zambia with zero-imputation).
- **Comparative Atlas & Authority Corpus (`data/curated/`)**: 46-country Comparative Jurisdiction Atlas, **238** verified real-world authorities, and **50-term** 5-language glossary (`en`, `id_ms`, `es`, `fr`, `ar`).
- **Curated Portfolios (`data/curated/`)**: 100-program sample (`seed=2027`), 1,000-program TF-IDF-screened portfolio (`seed=202702`), 10,000-program scale-up (`seed=202706`), Top-10 Pilot Prototypes, and Top-10 AIA Dossiers.
- **Offline CPU Prototypes (`src/prototype/`, `PROTOTYPE_EXPERIMENTAL_NONBINDING`)**:
  - Grounded Citation Verification Gate & CLI (`src/prototype/cli.py`, 6/6 synthetic accuracy)
  - Judgment Anonymisation & PII Redaction Gate (4/4 synthetic accuracy)
  - Risk-Scoring Disparity & Fairness Audit Simulator (detecting injected 0.2386 FPR disparity)
  - Algorithmic Impact Assessment (AIA) Dossier Generator
- **Interactive Portal & CI**: Zero-CDN GitHub Pages portal (`docs/index.html`) and GitHub Actions CI (`.github/workflows/ci.yml`).

## Quickstart
```bash
python3 -m src.run_all
```
