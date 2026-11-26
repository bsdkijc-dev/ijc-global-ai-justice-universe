"""Package a reproducible local release bundle (v2.9.0) with Kaggle metadata and SHA-256 manifest."""

import json
import shutil
import tarfile
from pathlib import Path
from src.export.exporter import sha256_file

ROOT = Path(__file__).resolve().parent.parent.parent
RELEASE_NAME = "ijc-gajiu-v2.9.0"
RELEASE_DIR = ROOT / "data" / "releases" / RELEASE_NAME
ARCHIVE_PATH = ROOT / "data" / "releases" / f"{RELEASE_NAME}.tar.gz"
MANIFEST_PATH = ROOT / "data" / "manifests" / "release_v2.9.0_manifest.json"

BUNDLE_FILES = [
    "sources/source-registry.csv",
    "sources/source-registry.json",
    "sources/access-log.csv",
    "data/curated/jurisdiction_atlas_46.csv",
    "data/curated/jurisdiction_atlas_46.json",
    "data/curated/governance_readiness_46.csv",
    "data/curated/asean_apac_comparative_matrix.csv",
    "data/curated/asean_sea_programs_500.parquet",
    "data/curated/europe_comparative_matrix.csv",
    "data/curated/europe_eur_programs_500.parquet",
    "data/curated/latam_comparative_matrix.csv",
    "data/curated/latam_lat_programs_500.parquet",
    "data/curated/ssa_mena_comparative_matrix.csv",
    "data/curated/ssa_mena_programs_500.parquet",
    "data/curated/nam_eca_comparative_matrix.csv",
    "data/curated/nam_eca_programs_500.parquet",
    "data/curated/ai_systems_inventory.csv",
    "data/curated/ai_systems_inventory.json",
    "data/curated/precedent_graph_edges.csv",
    "data/curated/horizon_roadmap_2027_2045.csv",
    "data/curated/judicial_ai_curriculum_10.csv",
    "data/curated/programs_curated_1000.csv",
    "data/curated/programs_curated_1000.parquet",
    "data/curated/programs_curated_10000.parquet",
    "data/curated/programs_curated_100000.parquet",
    "data/curated/top10_pilot_prototypes.csv",
    "data/curated/top10_pilot_prototypes.json",
    "data/curated/top10_pilot_aia_dossiers.json",
    "data/curated/verified_authority_corpus.json",
    "data/curated/multilingual_glossary_50.csv",
    "data/curated/multilingual_glossary_50.json",
    "data/curated/pillar_coverage_30.csv",
    "data/curated/statutory_harmonization_matrix.csv",
    "data/sample/prototype_benchmark_results.json",
    "data/sample/anonymisation_benchmark_results.json",
    "data/sample/risk_audit_benchmark_results.json",
    "data/sample/synthetic_media_benchmark_results.json",
    "data/sample/srl_kiosk_benchmark_results.json",
    "data/sample/procurement_audit_benchmark_results.json",
    "data/sample/neuro_symbolic_benchmark_results.json",
    "data/sample/adversarial_stress_test_results.json",
    "data/sample/statutory_harmonization_results.json",
    "data/sample/phase3_unified_audit.json",
    "data/manifests/cardinality_verification.json",
    "data/manifests/scale_1m_manifest.json",
]

KAGGLE_METADATA = {
    "title": "IJC Global AI & Justice Innovation Universe",
    "id": "judicialcollege/ijc-global-ai-justice-universe",
    "licenses": [{"name": "MIT"}],
    "subtitle": "v2.9.0: Phase 3 Unified Audit, Simulator Portal & 100k",
    "description": (
        "# IJC Global AI & Justice Innovation Universe (v2.9.0 — Phase 3)\n\n"
        "**Founder:** Cecep Mustafa  \n"
        "**Repository:** https://github.com/bsdkijc-dev/ijc-global-ai-justice-universe\n\n"
        "## What's New in v2.9.0 (Phase 3 — Task 029)\n"
        "- Added `phase3_unified_audit.json` unifying Neuro-Symbolic Reasoning (`6/6`), Adversarial Stress-Testing (`10/10`), and Statutory Harmonization (`30` regional cells).\n"
        "- Upgraded zero-CDN GitHub Pages portal (`docs/index.html`) with an interactive client-side Neuro-Symbolic Safeguard Simulator (`NORM-01`–`NORM-06`).\n"
    ),
    "keywords": ["law", "artificial intelligence"],
    "isPrivate": True,
    "resources": [
        {"path": Path(f).name, "description": f"Released from {f}"}
        for f in BUNDLE_FILES
    ],
}


def main() -> None:
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    file_hashes = {}
    for rel in BUNDLE_FILES:
        src = ROOT / rel
        dst = RELEASE_DIR / Path(rel).name
        shutil.copy2(src, dst)
        file_hashes[dst.name] = {
            "source_path": rel,
            "bytes": dst.stat().st_size,
            "sha256": sha256_file(dst),
        }

    meta_path = RELEASE_DIR / "dataset-metadata.json"
    meta_path.write_text(json.dumps(KAGGLE_METADATA, indent=2), encoding="utf-8")

    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(RELEASE_DIR, arcname=RELEASE_NAME)

    manifest = {
        "release_version": "2.9.0",
        "release_name": RELEASE_NAME,
        "publication_status": "STAGED_FOR_GITHUB_AND_KAGGLE",
        "archive": {
            "filename": ARCHIVE_PATH.name,
            "bytes": ARCHIVE_PATH.stat().st_size,
            "sha256": sha256_file(ARCHIVE_PATH),
        },
        "files": file_hashes,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Packaged {RELEASE_NAME} ({len(file_hashes)} data files + dataset-metadata.json)")


if __name__ == "__main__":
    main()
