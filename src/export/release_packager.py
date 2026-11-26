"""Package a reproducible local release bundle (v0.4.0) with Kaggle metadata and SHA-256 manifest."""

import json
import shutil
import tarfile
from pathlib import Path
from src.export.exporter import sha256_file

ROOT = Path(__file__).resolve().parent.parent.parent
RELEASE_NAME = "ijc-gajiu-v0.4.0"
RELEASE_DIR = ROOT / "data" / "releases" / RELEASE_NAME
ARCHIVE_PATH = ROOT / "data" / "releases" / f"{RELEASE_NAME}.tar.gz"
MANIFEST_PATH = ROOT / "data" / "manifests" / "release_v0.4.0_manifest.json"

BUNDLE_FILES = [
    "sources/source-registry.csv",
    "sources/source-registry.json",
    "sources/access-log.csv",
    "data/curated/jurisdiction_atlas_46.csv",
    "data/curated/jurisdiction_atlas_46.json",
    "data/curated/programs_curated_1000.csv",
    "data/curated/programs_curated_1000.parquet",
    "data/curated/top10_pilot_prototypes.csv",
    "data/curated/top10_pilot_prototypes.json",
    "data/curated/verified_authority_corpus.json",
    "data/sample/prototype_benchmark_results.json",
]

KAGGLE_METADATA = {
    "title": "IJC Global AI & Justice Innovation Universe",
    "id": "judicialcollege/ijc-global-ai-justice-universe",
    "licenses": [{"name": "MIT"}],
    "subtitle": "46-country AI justice atlas, 1,000 12D research programs & 238 authorities",
    "description": (
        "# IJC Global AI & Justice Innovation Universe (v0.4.0)\n\n"
        "**Founder:** Cecep Mustafa  \n"
        "**Repository:** https://github.com/bsdkijc-dev/ijc-global-ai-justice-universe\n\n"
        "## What's New in v0.4.0\n"
        "- Added `verified_authority_corpus.json` (**238** verified real-world cases, statutes, and judicial policies from the Oxford AI Justice Atlas).\n"
        "- Updated `prototype_benchmark_results.json` against the 238-entry corpus (`6/6` exact detection accuracy).\n"
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
        "release_version": "0.4.0",
        "release_name": RELEASE_NAME,
        "publication_status": "STAGED_FOR_KAGGLE_VERSION_UPDATE",
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
