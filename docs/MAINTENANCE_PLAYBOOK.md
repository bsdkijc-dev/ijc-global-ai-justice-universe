# Solo-Founder Maintenance & Operations Playbook

**Owner:** Cecep Mustafa  
**Budget Policy:** Zero Incremental Cash Expenditure  
**Target Workstation:** Dell Precision 7540 (or any Python 3.11+ Linux/CPU host)

## 1. Full Local Verification
Run the entire pipeline and test suite with one command:
```bash
python3 -m src.run_all
```

## 2. Quarterly Oxford AI Justice Atlas Re-Audit
1. Re-check `OXF-AIATLAS-44` (Zambia) and any updated country profiles on `https://www.techandjustice.bsg.ox.ac.uk/ai-atlas`.
2. Update `sources/build_registry.py`, regenerate `sources/source-registry.{csv,json}`, and run `python3 -m src.evidence.jurisdiction_atlas`.
3. Never backfill inaccessible URLs; preserve `SOURCE_INACCESSIBLE` until live access succeeds.

## 3. GitHub & Kaggle Release Sync
```bash
git add -A && git commit -m "Release vX.Y.Z"
git tag -a vX.Y.Z -m "IJC Global AI & Justice Innovation Universe vX.Y.Z"
git push -u origin main --tags
kaggle datasets version -p data/releases/ijc-gajiu-vX.Y.Z -m "Release vX.Y.Z"
```
