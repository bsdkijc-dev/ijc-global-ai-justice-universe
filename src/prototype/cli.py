"""Offline CLI for Citation Verification Gate & Appellate Filing Audit."""

import argparse
import json
from pathlib import Path
from src.prototype.citation_and_triage_gate import verify_citations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline Citation Verification Gate (PROTOTYPE_EXPERIMENTAL_NONBINDING)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Inline filing or brief text to audit")
    group.add_argument("--file", type=Path, help="Path to UTF-8 text file to audit")
    parser.add_argument("--out", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    content = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
    result = verify_citations(content)
    formatted = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(formatted, encoding="utf-8")
    print(formatted)


if __name__ == "__main__":
    main()
