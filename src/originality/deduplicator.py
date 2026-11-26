"""Originality and semantic deduplication screening (Hash + Jaccard + TF-IDF cosine)."""

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_JSONL = ROOT / "data" / "sample" / "programs_sample_100.jsonl"
REPORT_MD = ROOT / "reports" / "originality_report.md"

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def jaccard_similarity(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def compute_tfidf_matrix(docs: List[List[str]]) -> np.ndarray:
    vocab: Dict[str, int] = {}
    df: Counter = Counter()
    for tokens in docs:
        for tok in set(tokens):
            df[tok] += 1
            if tok not in vocab:
                vocab[tok] = len(vocab)

    n_docs = len(docs)
    mat = np.zeros((n_docs, len(vocab)), dtype=np.float64)
    for i, tokens in enumerate(docs):
        tf = Counter(tokens)
        total = max(len(tokens), 1)
        for tok, cnt in tf.items():
            j = vocab[tok]
            idf = math.log((1 + n_docs) / (1 + df[tok])) + 1.0
            mat[i, j] = (cnt / total) * idf

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def screen_originality(
    programs: List[Dict[str, Any]], threshold: float = 0.85
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    hashes = [p["tuple_sha256"] for p in programs]
    exact_duplicates = len(hashes) - len(set(hashes))

    texts = [f"{p['title']} {p['rationale']} {p['implementation_pathway']}" for p in programs]
    docs = [tokenize(t) for t in texts]
    tfidf = compute_tfidf_matrix(docs)
    sim_matrix = tfidf @ tfidf.T
    np.fill_diagonal(sim_matrix, 0.0)

    flagged_pairs = []
    max_sims = sim_matrix.max(axis=1)
    for i, p in enumerate(programs):
        p["originality_score"] = round(float(max(0.0, 1.0 - max_sims[i])), 4)
        for j in range(i + 1, len(programs)):
            cos_sim = float(sim_matrix[i, j])
            if cos_sim >= threshold:
                jac = jaccard_similarity(set(docs[i]), set(docs[j]))
                flagged_pairs.append({
                    "id_a": p["program_id"],
                    "id_b": programs[j]["program_id"],
                    "tfidf_cosine": round(cos_sim, 4),
                    "token_jaccard": round(jac, 4),
                })

    stats = {
        "total_programs": len(programs),
        "exact_hash_duplicates": exact_duplicates,
        "similarity_threshold": threshold,
        "flagged_near_duplicate_pairs": len(flagged_pairs),
        "mean_originality_score": round(sum(p["originality_score"] for p in programs) / max(len(programs), 1), 4),
        "min_originality_score": round(min(p["originality_score"] for p in programs), 4),
        "flagged_pairs": flagged_pairs,
    }
    return programs, stats


def main() -> None:
    programs = [
        json.loads(line)
        for line in SAMPLE_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    updated, stats = screen_originality(programs)
    with SAMPLE_JSONL.open("w", encoding="utf-8") as f:
        for p in updated:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    lines = [
        "# Originality & Semantic Deduplication Report",
        "",
        f"- **Total Programs Screened:** {stats['total_programs']}",
        f"- **Exact SHA-256 Duplicates:** {stats['exact_hash_duplicates']}",
        f"- **TF-IDF Cosine Threshold:** {stats['similarity_threshold']}",
        f"- **Flagged Near-Duplicate Pairs (>= 0.85):** {stats['flagged_near_duplicate_pairs']}",
        f"- **Mean Originality Score:** {stats['mean_originality_score']}",
        f"- **Minimum Originality Score:** {stats['min_originality_score']}",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"Screened {stats['total_programs']} programs | Exact dups: {stats['exact_hash_duplicates']} | "
        f"Near-dup pairs: {stats['flagged_near_duplicate_pairs']} | Mean originality: {stats['mean_originality_score']}"
    )


if __name__ == "__main__":
    main()
