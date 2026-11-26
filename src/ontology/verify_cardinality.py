#!/usr/bin/env python3
"""Verify the mathematical cardinality of the 12-dimensional generative space."""

import json
from pathlib import Path
from taxonomy import DIMENSIONS, PILLARS, compute_cardinality

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    total, counts = compute_cardinality()
    assert len(DIMENSIONS) == 12, f"Expected 12 dimensions, got {len(DIMENSIONS)}"
    assert len(PILLARS) == 30, f"Expected 30 pillars, got {len(PILLARS)}"
    for dim, count in counts.items():
        assert count >= 10, f"Dimension {dim} has {count} < 10 values"
    assert total >= 1_000_000_000_000, f"Total space {total} < 10^12"

    summary = {
        "dimension_count": len(DIMENSIONS),
        "pillar_count": len(PILLARS),
        "dimension_cardinalities": counts,
        "total_addressable_configurations": total,
        "meets_one_trillion_target": total >= 1_000_000_000_000,
    }
    out_path = ROOT / "data" / "manifests" / "cardinality_verification.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Verified 12D space: {total:,} addressable configurations (>= 1,000,000,000,000: {summary['meets_one_trillion_target']})")


if __name__ == "__main__":
    main()
