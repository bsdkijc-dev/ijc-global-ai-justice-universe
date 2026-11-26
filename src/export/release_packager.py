"""Package a reproducible local release bundle (v0.3.0) with SHA-256 manifest."""

import json
import shutil
import tarfile
from pathlib import Path
from src.export.exporter import sha256_file

ROOT = Path(__file__).resolve().parent.parent.parent
RELEASE_NAME = "ijc-gajiu-v0.3.0"
RELEASE_DIR = ROOT / "data" / "releases" / RELEASE_NAME
ARCHIVE_PATH = ROOT / "data" / "releases" / f"{RELEASE_NAME}.tar.gz"
MANIFEST_PATH = ROOT / "data" / "manifests" / "release_v0.3.0_manifest.json"

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
    "data/sample/prototype_benchmark_results.json",
]


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

    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(RELEASE_DIR, arcname=RELEASE_NAME)

    manifest = {
        "release_version": "0.3.0",
        "release_name": RELEASE_NAME,
        "publication_status": "STAGED_LOCALLY_NOT_PUBLISHED",
        "archive": {
            "filename": ARCHIVE_PATH.name,
            "bytes": ARCHIVE_PATH.stat().st_size,
            "sha256": sha256_file(ARCHIVE_PATH),
        },
        "files": file_hashes,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Packaged {RELEASE_NAME} ({len(file_hashes)} files) -> {ARCHIVE_PATH.name}")


if __name__ == "__main__":
    main()
