"""Verify SHA-256 checksums across manifests and enforce epistemic integrity."""

import json
from pathlib import Path
from src.export.exporter import sha256_file

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFESTS_DIR = ROOT / "data" / "manifests"
REPORT_MD = ROOT / "reports" / "MANIFEST_INTEGRITY_AUDIT.md"


def verify_all_manifests() -> dict:
    checks = []
    # Check sample_100, curated_1000, curated_10000
    for m_name, folder in [
        ("sample_100_manifest.json", ROOT / "data" / "sample"),
        ("curated_1000_manifest.json", ROOT / "data" / "curated"),
        ("curated_10000_manifest.json", ROOT / "data" / "curated"),
    ]:
        data = json.loads((MANIFESTS_DIR / m_name).read_text(encoding="utf-8"))
        for fname, meta in data["files"].items():
            fpath = folder / fname
            actual = sha256_file(fpath)
            ok = actual == meta["sha256"]
            checks.append({"manifest": m_name, "file": fname, "sha256_match": ok})
            if not ok:
                raise AssertionError(f"Checksum mismatch for {fpath}")

    # Check 100k manifest
    m100k = json.loads((MANIFESTS_DIR / "curated_100000_manifest.json").read_text(encoding="utf-8"))
    f100k = ROOT / "data" / "curated" / m100k["file"]["name"]
    ok100k = sha256_file(f100k) == m100k["file"]["sha256"]
    checks.append({"manifest": "curated_100000_manifest.json", "file": f100k.name, "sha256_match": ok100k})
    if not ok100k:
        raise AssertionError("Checksum mismatch for 100k Parquet")

    return {"total_files_verified": len(checks), "all_passed": all(c["sha256_match"] for c in checks), "checks": checks}


def main() -> None:
    res = verify_all_manifests()
    md = [
        "# Cryptographic Manifest & Epistemic Integrity Audit",
        "",
        f"- **Total Files Verified (SHA-256):** {res['total_files_verified']}",
        f"- **All Checksums Matched:** {res['all_passed']}",
        "",
        "| Manifest | File | SHA-256 Match |",
        "| :--- | :--- | :--- |",
    ]
    for c in res["checks"]:
        md.append(f"| {c['manifest']} | {c['file']} | {c['sha256_match']} |")
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Verified {res['total_files_verified']} manifest checksums (all_passed={res['all_passed']})")


if __name__ == "__main__":
    main()
